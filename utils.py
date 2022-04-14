from functools import wraps
from flask import jsonify, request
import documents.state_machine as state_machine

def authenticate_user(func):
    @wraps(func)
    def wrapper():
        auth_header = request.headers.get('Authorization')
        payload = state_machine.token_valid_check(auth_header)
        return func(payload)
    return wrapper

def server_error_check(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try: 
            return func(*args, **kwargs)
        except:
            return jsonify({'message':'Something went wrong.'}), 500
    return wrapper