from flask import Response
from http import HTTPStatus as status
def success_response( message , code):
    response = {
        "message":"success",
        "code": code,
        "detail": message,
        "status": True
 
    }
    return response
