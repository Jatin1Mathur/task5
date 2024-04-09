from flask import Response
from http import HTTPStatus as status
from flask import Flask, request, jsonify
def success_response( message , code):
    response = {
        "message":"success",
        "code": code,
        "detail": message,
        "status": True
 
    }
    return response
