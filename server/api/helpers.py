import json

from ..util.commands import handleCommand


def handle_incoming_command(app, nimplant, command):
    try:
        if nimplant and command:
            handleCommand(command, nimplant)
            return ok_response(app, f"Command queued: {command}")
        else:
            raise Exception("NimPlant with the given guid not found")
    except Exception as e:
        return error_response(app, e)


def error_response(app, exception):
    return app.response_class(
        response=json.dumps({
            "message": f"An unexpected error occurred: {exception}",
            "errors": [str(exception)]
        }),
        status=500
    )


def ok_response(app, message=""):
    try:
        return app.response_class(
            response=json.dumps({"status": "OK", "message": message}),
            status=200,
            mimetype='application/json'
        )
    except Exception as e:
        return error_response(app, e)


def json_response(app, data):
    try:
        return app.response_class(
            response=json.dumps(data),
            status=200,
            mimetype='application/json'
        )
    except Exception as e:
        return error_response(app, e)
