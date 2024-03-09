import os
from threading import Thread

import flask
from flask_cors import CORS
from gevent.pywsgi import WSGIServer
from werkzeug.utils import secure_filename

from server.util.commands import get_commands, handle_command
from server.util.config import config
from server.util.crypto import random_string
from server.util.func import exit_server
from server.util.nimplant import np_server
from server.util.db import (
    db_get_nimplant_console,
    db_get_nimplant_details,
    db_get_nimplant_info,
    db_get_server_console,
    db_get_server_info,
)


# Parse server configuration
server_ip = config["server"]["ip"]
server_port = config["server"]["port"]

# Initiate flask app
app = flask.Flask(
    __name__,
    static_url_path="",
    static_folder="../web/static",
    template_folder="../web",
)
app.secret_key = random_string(32)


# Define the API server
def api_server():
    # Get available commands
    @app.route("/api/commands", methods=["GET"])
    def get_command_list():
        return flask.jsonify(get_commands()), 200

    # Get download information
    @app.route("/api/downloads", methods=["GET"])
    def get_downloads():
        try:
            downloads_path = os.path.abspath(
                f"server/downloads/server-{np_server.guid}"
            )
            res = []
            items = os.scandir(downloads_path)
            for item in items:
                if item.is_dir() and item.name.startswith("nimplant-"):
                    downloads = os.scandir(item.path)
                    for download in downloads:
                        if download.is_file():
                            res.append(
                                {
                                    "name": download.name,
                                    "nimplant": item.name.split("-")[1],
                                    "size": download.stat().st_size,
                                    "lastmodified": download.stat().st_mtime,
                                }
                            )

            res = sorted(res, key=lambda x: x["lastmodified"], reverse=True)
            return flask.jsonify(res), 200
        except FileNotFoundError:
            return flask.jsonify([]), 404

    # Download a file from the downloads folder
    @app.route("/api/downloads/<nimplant_guid>/<filename>", methods=["GET"])
    def get_download(nimplant_guid, filename):
        try:
            downloads_path = os.path.abspath(
                f"server/downloads/server-{np_server.guid}/nimplant-{nimplant_guid}"
            )
            return flask.send_from_directory(
                downloads_path, filename, as_attachment=True
            )
        except FileNotFoundError:
            return flask.jsonify("File not found"), 404

    # Get server configuration
    @app.route("/api/server", methods=["GET"])
    def get_server_info():
        return flask.jsonify(db_get_server_info(np_server.guid)), 200

    # Get the last X lines of console history
    @app.route("/api/server/console", methods=["GET"])
    @app.route("/api/server/console/<lines>", methods=["GET"])
    @app.route("/api/server/console/<lines>/<offset>", methods=["GET"])
    def get_server_console(lines="1000", offset="0"):
        # Process input as string and check if valid
        if not lines.isnumeric() or not offset.isnumeric():
            return flask.jsonify("Invalid parameters"), 400

        return flask.jsonify(db_get_server_console(np_server.guid, lines, offset)), 200

    # Exit the server
    @app.route("/api/server/exit", methods=["POST"])
    def post_exit_server():
        Thread(target=exit_server).start()
        return flask.jsonify("Exiting server..."), 200

    # Upload a file to the server's "uploads" folder
    @app.route("/api/upload", methods=["POST"])
    def post_upload():
        upload_path = os.path.abspath(f"server/uploads/server-{np_server.guid}")

        if "file" not in flask.request.files:
            return flask.jsonify("No file part"), 400

        file = flask.request.files["file"]
        if file.filename == "":
            return flask.jsonify("No file selected"), 400

        if file:
            os.makedirs(upload_path, exist_ok=True)
            filename = secure_filename(file.filename)
            full_path = os.path.join(upload_path, filename)
            file.save(full_path)
            return flask.jsonify({"result": "File uploaded", "path": full_path}), 200
        else:
            return flask.jsonify("File upload failed"), 400

    # Get all active nimplants with basic information
    @app.route("/api/nimplants", methods=["GET"])
    def get_nimplants():
        return flask.jsonify(db_get_nimplant_info(np_server.guid)), 200

    # Get a specific nimplant with its details
    @app.route("/api/nimplants/<guid>", methods=["GET"])
    def get_nimplant(guid):
        if np_server.get_nimplant_by_guid(guid):
            return flask.jsonify(db_get_nimplant_details(guid)), 200
        else:
            return flask.jsonify("Invalid Nimplant GUID"), 404

    # Get the last X lines of console history for a specific nimplant
    @app.route("/api/nimplants/<guid>/console", methods=["GET"])
    @app.route("/api/nimplants/<guid>/console/<lines>", methods=["GET"])
    @app.route("/api/nimplants/<guid>/console/<lines>/<offset>", methods=["GET"])
    def get_nimplant_console(guid, lines="1000", offset="0"):
        # Process input as string and check if valid
        if not lines.isnumeric() or not offset.isnumeric():
            return flask.jsonify("Invalid parameters"), 400

        if np_server.get_nimplant_by_guid(guid):
            return flask.jsonify(db_get_nimplant_console(guid, lines, offset)), 200
        else:
            return flask.jsonify("Invalid Nimplant GUID"), 404

    # Issue a command to a specific nimplant
    @app.route("/api/nimplants/<guid>/command", methods=["POST"])
    def post_nimplant_command(guid):
        np = np_server.get_nimplant_by_guid(guid)
        data = flask.request.json
        command = data["command"]

        if np and command:
            handle_command(command, np)
            return flask.jsonify(f"Command queued: {command}"), 200
        else:
            return flask.jsonify("Invalid Nimplant GUID or command"), 404

    # Exit a specific nimplant
    @app.route("/api/nimplants/<guid>/exit", methods=["POST"])
    def post_nimplant_exit(guid):
        np = np_server.get_nimplant_by_guid(guid)

        if np:
            handle_command("kill", np)
            return flask.jsonify("Instructed Nimplant to exit"), 200
        else:
            return flask.jsonify("Invalid Nimplant GUID"), 404

    @app.route("/")
    @app.route("/index")
    def home():
        return flask.render_template("index.html")

    @app.route("/server")
    def server():
        return flask.render_template("server.html")

    @app.route("/nimplants")
    def nimplants():
        return flask.render_template("nimplants.html")

    @app.route("/nimplants/details")
    def nimplantdetails():
        return flask.render_template("nimplants/details.html")

    @app.route("/<path:path>")
    def catch_all(_path):
        return flask.render_template("404.html")

    @app.errorhandler(Exception)
    def all_exception_handler(error):
        return flask.jsonify(status=f"Server error: {error}"), 500

    CORS(app, resources={r"/*": {"origins": "*"}})
    http_server = WSGIServer((server_ip, server_port), app, log=None)
    http_server.serve_forever()
