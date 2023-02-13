import sqlite3
from .config import config
from .func import timestamp, nimplantPrint

con = sqlite3.connect(
    "server/nimplant.db", check_same_thread=False, detect_types=sqlite3.PARSE_DECLTYPES
)

# Use the Row type to allow easy conversions to dicts
con.row_factory = sqlite3.Row

# Handle bool as 1 (True) and 0 (False)
sqlite3.register_adapter(bool, int)
sqlite3.register_converter("BOOLEAN", lambda v: bool(int(v)))

#
#   BASIC FUNCTIONALITY (NIMPLANT)
#


def initDb():
    try:
        # Create the server (configuration) table
        con.execute(
            """
        CREATE TABLE IF NOT EXISTS server
        (guid TEXT PRIMARY KEY, name TEXT, dateCreated DATETIME,
        xorKey INTEGER, managementIp TEXT, managementPort INTEGER, 
        listenerType TEXT, listenerIp TEXT, listenerHost TEXT, listenerPort INTEGER, 
        registerPath TEXT, taskPath TEXT, resultPath TEXT, riskyMode BOOLEAN,
        sleepTime INTEGER, sleepJitter INTEGER, killDate TEXT,
        userAgent TEXT, killed BOOLEAN)
        """
        )

        # Create the nimplant table
        con.execute(
            """
        CREATE TABLE IF NOT EXISTS nimplant
        (id INTEGER, guid TEXT PRIMARY KEY, serverGuid TEXT, active BOOLEAN, late BOOLEAN,
        cryptKey TEXT, ipAddrExt TEXT, ipAddrInt TEXT, username TEXT,
        hostname TEXT, osBuild TEXT, pid INTEGER, pname TEXT, riskyMode BOOLEAN,
        sleepTime INTEGER, sleepJitter INTEGER, killDate TEXT,
        firstCheckin TEXT, lastCheckin TEXT, pendingTasks TEXT,
        hostingFile TEXT, receivingFile TEXT, lastUpdate TEXT,
        FOREIGN KEY (serverGuid) REFERENCES server(guid))
        """
        )

        # Create the server_history table
        con.execute(
            """
        CREATE TABLE IF NOT EXISTS server_history
        (id INTEGER PRIMARY KEY AUTOINCREMENT, serverGuid TEXT, result TEXT, resultTime TEXT,
        FOREIGN KEY (serverGuid) REFERENCES server(guid))
        """
        )

        # Create the nimplant_history table
        con.execute(
            """
        CREATE TABLE IF NOT EXISTS nimplant_history
        (id INTEGER PRIMARY KEY AUTOINCREMENT, nimplantGuid TEXT, taskGuid TEXT, task TEXT, taskFriendly TEXT,
        taskTime TEXT, result TEXT, resultTime TEXT,
        FOREIGN KEY (nimplantGuid) REFERENCES nimplant(guid))
        """
        )

    except Exception as e:
        nimplantPrint(f"DB error: {e}")


# Define a function to compare the config to the last server object
def dbPreviousServerSameConfig(nimplant_server, xor_key) -> bool:
    try:
        nimplant_server = nimplant_server.asdict()

        # Get the previous server object
        prevServer = con.execute(
            """SELECT * FROM server WHERE NOT killed ORDER BY dateCreated DESC LIMIT 1"""
        ).fetchone()

        # If there is no previous server object, return True
        if prevServer is None:
            return False

        # Compare the config to the previous server object
        if (
            xor_key != prevServer["xorKey"]
            or nimplant_server["managementIp"] != prevServer["managementIp"]
            or nimplant_server["managementPort"] != prevServer["managementPort"]
            or nimplant_server["listenerType"] != prevServer["listenerType"]
            or nimplant_server["listenerIp"] != prevServer["listenerIp"]
            or nimplant_server["listenerHost"] != prevServer["listenerHost"]
            or nimplant_server["listenerPort"] != prevServer["listenerPort"]
            or nimplant_server["registerPath"] != prevServer["registerPath"]
            or nimplant_server["taskPath"] != prevServer["taskPath"]
            or nimplant_server["resultPath"] != prevServer["resultPath"]
            or nimplant_server["riskyMode"] != prevServer["riskyMode"]
            or nimplant_server["killDate"] != prevServer["killDate"]
            or nimplant_server["userAgent"] != prevServer["userAgent"]
        ):
            return False

        # If nothing has changed, return False
        return True

    except Exception as e:
        nimplantPrint(f"DB error: {e}")


# Get the previous server object for session restoring
def dbGetPreviousServerConfig():
    try:
        # Get the previous server object
        return con.execute(
            """SELECT * FROM server WHERE NOT killed ORDER BY dateCreated DESC LIMIT 1"""
        ).fetchone()

    except Exception as e:
        nimplantPrint(f"DB error: {e}")


# Get all the Nimplants for the previous server object
def dbGetPreviousNimplants(serverGuid):
    try:
        return con.execute(
            """SELECT * FROM nimplant WHERE serverGuid = :serverGuid""",
            {"serverGuid": serverGuid},
        ).fetchall()

    except Exception as e:
        nimplantPrint(f"DB error: {e}")


# Create the server object (only runs when config has changed or no object exists)
def dbInitNewServer(np_server):
    try:
        con.execute(
            """INSERT INTO server
                       VALUES (:guid, :name, CURRENT_TIMESTAMP, :xorKey, :managementIp, :managementPort,
                       :listenerType, :listenerIp, :listenerHost, :listenerPort, :registerPath,
                       :taskPath, :resultPath, :riskyMode, :sleepTime, :sleepJitter,
                       :killDate, :userAgent, :killed)""",
            np_server.asdict(),
        )
        con.commit()

    except Exception as e:
        nimplantPrint(f"DB error: {e}")


# Mark the server object as killed in the database, preventing it from being restored on next boot
def dbKillServer(serverGuid):
    try:
        con.execute(
            """UPDATE server SET killed = 1 WHERE guid = :serverGuid""",
            {"serverGuid": serverGuid},
        )
        con.commit()

    except Exception as e:
        nimplantPrint(f"DB error: {e}")


# Create a new nimplant object (runs once when Nimplant first checks in)
def dbInitNimplant(np, serverGuid):
    try:
        obj = {
            "id": np.id,
            "guid": np.guid,
            "serverGuid": serverGuid,
            "active": np.active,
            "late": np.late,
            "cryptKey": np.cryptKey,
            "ipAddrExt": np.ipAddrExt,
            "ipAddrInt": np.ipAddrInt,
            "username": np.username,
            "hostname": np.hostname,
            "osBuild": np.osBuild,
            "pid": np.pid,
            "pname": np.pname,
            "riskyMode": np.riskyMode,
            "sleepTime": np.sleepTime,
            "sleepJitter": np.sleepJitter,
            "killDate": np.killDate,
            "firstCheckin": np.firstCheckin,
            "lastCheckin": np.lastCheckin,
            "pendingTasks": ", ".join([t["task"] for t in np.pendingTasks]),
            "hostingFile": np.hostingFile,
            "receivingFile": np.receivingFile,
            "lastUpdate": timestamp(),
        }

        con.execute(
            """INSERT INTO nimplant
                       VALUES 
                       (:id, :guid, :serverGuid, :active, :late,
                       :cryptKey, :ipAddrExt, :ipAddrInt, :username, :hostname, :osBuild, :pid, :pname,
                       :riskyMode, :sleepTime, :sleepJitter, :killDate, :firstCheckin,
                       :lastCheckin, :pendingTasks, :hostingFile, :receivingFile, :lastUpdate)""",
            obj,
        )
        con.commit()

    except Exception as e:
        nimplantPrint(f"DB error: {e}")


# Update an existing nimplant object (runs every time Nimplant checks in)
def dbUpdateNimplant(np):
    try:
        obj = {
            "guid": np.guid,
            "active": np.active,
            "late": np.late,
            "ipAddrExt": np.ipAddrExt,
            "ipAddrInt": np.ipAddrInt,
            "sleepTime": np.sleepTime,
            "sleepJitter": np.sleepJitter,
            "lastCheckin": np.lastCheckin,
            "pendingTasks": ", ".join([t["task"] for t in np.pendingTasks]),
            "hostingFile": np.hostingFile,
            "receivingFile": np.receivingFile,
            "lastUpdate": timestamp(),
        }

        con.execute(
            """UPDATE nimplant
                       SET active = :active, late = :late, ipAddrExt = :ipAddrExt,
                        ipAddrInt = :ipAddrInt, sleepTime = :sleepTime, sleepJitter = :sleepJitter,
                        lastCheckin = :lastCheckin, pendingTasks = :pendingTasks, hostingFile = :hostingFile,
                        receivingFile = :receivingFile, lastUpdate = :lastUpdate 
                       WHERE guid = :guid""",
            obj,
        )
        con.commit()

    except Exception as e:
        nimplantPrint(f"DB error: {e}")


# Write to Nimplant log
def dbNimplantLog(np, taskGuid=None, task=None, taskFriendly=None, result=None):
    try:
        ts = timestamp()

        obj = {
            "nimplantGuid": np.guid,
            "taskGuid": taskGuid,
            "task": task,
            "taskFriendly": taskFriendly,
            "taskTime": ts,
            "result": result,
            "resultTime": ts,
        }

        # If there is only a task, just log the task
        if taskGuid is not None and task is not None and result is None:
            con.execute(
                """INSERT INTO nimplant_history (nimplantGuid, taskGuid, task, taskFriendly, taskTime)
                           VALUES (:nimplantGuid, :taskGuid, :task, :taskFriendly, :taskTime)""",
                obj,
            )

        # If there are a task GUID and result, update the existing task with the result
        elif taskGuid is not None and task is None and result is not None:
            con.execute(
                """UPDATE nimplant_history
                            SET result = :result, resultTime = :resultTime
                            WHERE taskGuid = :taskGuid""",
                obj,
            )

        # If there is no task or task GUID but there is a result, log the result without task (console messages)
        elif taskGuid is None and task is None and result is not None:
            con.execute(
                """INSERT INTO nimplant_history (nimplantGuid, result, resultTime)
                            VALUES (:nimplantGuid, :result, :resultTime)""",
                obj,
            )

        # If there are both a result and a task (GUID may be None or have a value), log them all at once (server-side tasks)
        elif task is not None and result is not None:
            con.execute(
                """INSERT INTO nimplant_history (nimplantGuid, taskGuid, task, taskFriendly, taskTime, result, resultTime)
                            VALUES (:nimplantGuid, :taskGuid, :task, :taskFriendly, :taskTime, :result, :resultTime)""",
                obj,
            )

        # Other cases should not occur
        else:
            raise Exception("Uncaught logic case occurred when calling dbNimplantLog()")

        con.commit()

    except Exception as e:
        nimplantPrint(f"DB error: {e}")


# Write to server log
def dbServerLog(np_server, result):
    try:
        ts = timestamp()

        obj = {"serverGuid": np_server.guid, "result": result, "resultTime": ts}

        con.execute(
            """INSERT INTO server_history (serverGuid, result, resultTime)
                       VALUES (:serverGuid, :result, :resultTime)""",
            obj,
        )
        con.commit()

    except Exception as e:
        nimplantPrint(f"DB error: {e}")


#
#   FUNCTIONALITY FOR API
#

# Get server configuration (/api/server)
def dbGetServerInfo(serverGuid):
    try:
        res = con.execute(
            """SELECT * FROM server WHERE guid = :serverGuid""",
            {"serverGuid": serverGuid},
        ).fetchone()

        # Format as JSON-friendly object
        resJson = {
            "guid": res["guid"],
            "name": res["name"],
            "xorKey": res["xorKey"],
            "config": {
                "managementIp": res["managementIp"],
                "managementPort": res["managementPort"],
                "listenerType": res["listenerType"],
                "listenerIp": res["listenerIp"],
                "listenerHost": res["listenerHost"],
                "listenerPort": res["listenerPort"],
                "registerPath": res["registerPath"],
                "taskPath": res["taskPath"],
                "resultPath": res["resultPath"],
                "riskyMode": res["riskyMode"],
                "sleepTime": res["sleepTime"],
                "sleepJitter": res["sleepJitter"],
                "killDate": res["killDate"],
                "userAgent": res["userAgent"],
            },
        }
        return resJson

    except Exception as e:
        nimplantPrint(f"DB error: {e}")
        return {}


# Get the last X entries of console history (/api/server/console[/<limit>/<offset>])
def dbGetServerConsole(guid, limit, offset):
    try:
        res = con.execute(
            """SELECT * FROM server_history WHERE serverGuid = :serverGuid LIMIT :limit OFFSET :offset""",
            {"serverGuid": guid, "limit": limit, "offset": offset},
        ).fetchall()

        res = [dict(r) for r in res]
        return res

    except Exception as e:
        nimplantPrint(f"DB error: {e}")
        return {}


# Get overview of nimplants (/api/nimplants)
def dbGetNimplantInfo(serverGuid):
    try:
        res = con.execute(
            """SELECT id, guid, active, late, ipAddrInt, ipAddrExt, username, hostname, pid, pname, lastCheckin
                FROM nimplant WHERE serverGuid = :serverGuid""",
            {"serverGuid": serverGuid},
        ).fetchall()

        res = [dict(r) for r in res]
        return res

    except Exception as e:
        nimplantPrint(f"DB error: {e}")
        return {}


# Get details for nimplant (/api/nimplants/<guid>)
def dbGetNimplantDetails(nimplantGuid):
    try:
        res = con.execute(
            """SELECT * FROM nimplant WHERE guid = :nimplantGuid""",
            {"nimplantGuid": nimplantGuid},
        ).fetchone()

        if res:
            res = dict(res)
        return res

    except Exception as e:
        nimplantPrint(f"DB error: {e}")
        return {}


# Get the last X lines of console history for a specific nimplant (/api/nimplants/<guid>/console[/<limit>/<offset>])
def dbGetNimplantConsole(nimplantGuid, limit, offset):
    try:
        res = con.execute(
            """SELECT * FROM nimplant_history WHERE nimplantGuid = :nimplantGuid LIMIT :limit OFFSET :offset""",
            {"nimplantGuid": nimplantGuid, "limit": limit, "offset": offset},
        ).fetchall()

        if res:
            res = [dict(r) for r in res]

        return res

    except Exception as e:
        nimplantPrint(f"DB error: {e}")
        return {}
