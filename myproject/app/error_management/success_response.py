def success_response(message, code):
    response = {
        "message": "success",
        "code": code,
        "detail": message,
        "status": True
    }
    return response
