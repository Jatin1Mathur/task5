from flask import Flask, request, Response
from http import HTTPStatus as status

app = Flask(__name__)

error_message = {
    '500': {
        'message': "Internal error.",
        'detail': "An internal server error occurred while processing the request."
    },
    '404': {
        'message': "No user exists with given user id.",
        'detail': "The provided user id does not exist in the system."
    },
    '400': {
        'message': "Bad Request",
        'detail': "Record not found"
    },
    
    '201': {
        'message': "Created",
        'detail': "Record is created"
    },
    '200': {
        'message': "OK",
        'detail': "Code is running smoothly"
    },
    '403': {
        'message': "Forbidden",
        'detail': "Lack permission to access a certain part of a website"
    },
    '409': {
        'message': "Conflict",
        'detail': "Used to indicate a conflict with the current state of a resource"
    }
}


def e_response(error_code):
    response = f"{error_code}{error_message[error_code]['message']}{error_message[error_code]['detail']}"
    return Response(response=response, status=status.BAD_REQUEST, mimetype="text/plain")


if __name__ == "__main__":
    app.run()
