import datetime
from config import config
from flask import jsonify
from models.db import db
from models.User import User
import jwt
from models.Document import Document
from uuid import UUID

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
        access_token = jwt.encode(access_token_payload, config['ACCESS_TOKEN_SECRET'])
        refresh_token = jwt.encode(refresh_token_payload, config['REFRESH_TOKEN_SECRET'])
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

def get_user_by_user_id(user_id):
    try:
        users = db.session.query(User).filter(User.id == user_id)
        if users.count() <= 0:
            return None
        if users.count() == 1:
            for i in users:
                return vars(i)
        if users.count() > 1:
            raise Exception({'error':'voilates the unique ability!'})
    except Exception as e:
        raise Exception({'error':str(e.message)})
    
def create_document(user_id):
    try:
        document = Document(
            user_id = user_id
        )
        db.session.add(document)
        db.session.commit()
        return document.id
    except Exception as e:
        raise Exception({'error':str(e.message)})

def get_document_by_document_id(id):
    try:
        documents = db.session.query(Document).filter(Document.id == id)
        if documents.count() <= 0:
            return None
        if documents.count() == 1:
            for i in documents:
                return vars(i)
        if documents.count() > 1:
            raise Exception({'error':'voilates the unique ability!'})
    except Exception as e:
        raise Exception({'error':str(e.message)})

def token_valid_check(auth_header):
    try: 
        auth_token = auth_header.split(' ')[1]
        if auth_token == "" or auth_token == None:
            return {'message':'Authorization token empty'}
        decoded_token = jwt.decode(auth_token, config['ACCESS_TOKEN_SECRET'], algorithms=["HS256"])
        if decoded_token['userid'] == "" or decoded_token['userid'] == None:
            raise Exception({'error':'user_id not found'})
        return decoded_token['userid']
    except:
        raise Exception({'error':'invalid token'})

def get_all_documents_by_user_id(user_id):
    try:
        document = db.session.query(Document).filter(Document.user_id == user_id).all()
        arr = [];
        for i in document:
            arr.append(vars(i)['id'])
        return arr
    except Exception as e:
        raise Exception({'error':str(e.message)})
