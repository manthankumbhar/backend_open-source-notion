import datetime
import os
from flask import jsonify
from models.User import User, db
import jwt

def get_user_by_email(email):
    users = db.session.query(User).filter(User.email == email)
    if users.count() <= 0:
        return None
    if users.count() == 1:
        for i in users:
            return vars(i)
    if users.count() > 1:
        return {'error':'voilates the unique ability!'}, 500

def token_valid_check(token):
    users = db.session.query(User).filter(User.reset_password_hash == token)
    if users.count() <= 0:
        return None
    if users.count() == 1:
        for i in users:
            return vars(i)
    if users.count() > 1:
        return {'error':'voilates the unique ability!'}, 500

def create_user(email, password):
    user = User(
        email = email,
        password = password
    )
    db.session.add(user)
    db.session.commit()

def create_token(user_id):
    accessToken = jwt.encode({'userid': str(user_id), 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, os.environ.get('ACCESS_TOKEN_SECRET'))
    refreshToken = jwt.encode({'userid': str(user_id), 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24*365)}, os.environ.get('REFRESH_TOKEN_SECRET'))
    return jsonify({'accessToken':accessToken.decode('UTF-8'), 'refreshToken': refreshToken.decode('UTF-8')})

def update_reset_password_token(email, reset_password_hash):
    user = db.session.query(User).filter(User.email == email).first()
    user.reset_password_last_requested_at = datetime.datetime.utcnow()
    user.reset_password_hash = reset_password_hash
    db.session.commit()

def update_user(email, password, reset_password_hash):
    user = db.session.query(User).filter(User.email == email).first()
    user.password = password
    user.reset_password_hash = reset_password_hash
    db.session.commit()
    





