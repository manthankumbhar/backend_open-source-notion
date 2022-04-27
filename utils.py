from functools import wraps
import traceback
from flask import jsonify, request
import inspect
from config import config
import jwt

def token_valid_check(auth_header):
    auth_token = auth_header.split(' ')[1]
    if auth_token == "" or auth_token == None:
        raise Exception({'message':'Authorization token empty'})
    decoded_token = jwt.decode(auth_token, config['ACCESS_TOKEN_SECRET'], algorithms=["HS256"])
    return decoded_token

def authorize_user(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        payload = token_valid_check(auth_header)
        if 'payload' in inspect.getfullargspec(func).args:
            kwargs['payload'] = payload
        return func(*args, **kwargs)
    return wrapper

def server_error_check(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try: 
            return func(*args, **kwargs)
        except:
            traceback.print_exc()
            return jsonify({'message':'Something went wrong.'}), 500
    return wrapper