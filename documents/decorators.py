from flask import jsonify, request
import documents.state_machine as state_machine

def auth(func):
    def inner():
        auth_header = request.headers.get('Authorization')
        payload = state_machine.token_valid_check(auth_header)
        return func(payload)
    return inner

def utils(func):
    def inner():
        try: 
            return func()
        except:
            return jsonify({'message':'Something went wrong.'}), 500
    # Causing problems without renaming the function name below - found this solution on stackoverflow
    inner.__name__ = func.__name__
    return inner