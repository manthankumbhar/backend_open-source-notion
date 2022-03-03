import datetime
import os
from server import app
from flask import jsonify
from models.User import User, db
import jwt

def get_user_by_email(email):
    try:
        users = db.session.query(User).filter(User.email == email)
        if users.count() <= 0:
            return None
        if users.count() == 1:
            for i in users:
                return vars(i)
        if users.count() > 1:
            raise Exception({'error':'voilates the unique ability!'})
    except Exception as e:
        raise Exception({'error':str(e.message)})

def token_valid_check(token):
    try:
        users = db.session.query(User).filter(User.reset_password_hash == token)
        if users.count() <= 0:
            return None
        if users.count() == 1:
            for i in users:
                return vars(i)
        if users.count() > 1:
            raise Exception({'error':'voilates the unique ability!'})
    except Exception as e:
        raise Exception({'error':str(e.message)})

def create_user(email, password):
    try:
        user = User(
            email = email,
            password = password
        )
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        raise Exception({'error':str(e.message)})

def create_token(user_id):
    try:
        access_token_payload = {'userid': str(user_id), 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}
        refresh_token_payload = {'userid': str(user_id), 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24*365)}
        access_token = jwt.encode(access_token_payload, app.config['ACCESS_TOKEN_SECRET'])
        refresh_token = jwt.encode(refresh_token_payload, app.config['REFRESH_TOKEN_SECRET'])
        return {'access_token':access_token.decode('UTF-8'), 'refresh_token': refresh_token.decode('UTF-8')}
    except Exception as e:
        raise Exception({'error':str(e.message)})

def update_reset_password_token(email, reset_password_hash):
    try:
        user = db.session.query(User).filter(User.email == email).first()
        user.reset_password_last_requested_at = datetime.datetime.utcnow()
        user.reset_password_hash = reset_password_hash
        db.session.commit()
        updated_user = db.session.query(User).filter(User.email == email).first()
        return {'updated_user':updated_user}
    except Exception as e:
        raise Exception({'error':str(e.message)})

def update_user(email, password, reset_password_hash):
    try:
        user = db.session.query(User).filter(User.email == email).first()
        user.password = password
        user.reset_password_hash = reset_password_hash
        db.session.commit()
        updated_user = db.session.query(User).filter(User.email == email).first()
        return {'updated_user':updated_user}
    except Exception as e:
        raise Exception({'error':str(e.message)})
    





