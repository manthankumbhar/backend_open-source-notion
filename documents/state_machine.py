from config import config
from models.db import db
from models.User import User
import jwt
from models.Document import Document

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
    
def upsert_document(user_id):
    try:
        document = Document(
            user_id = user_id
        )
        db.session.add(document)
        db.session.commit()
        return document.id
    except Exception as e:
        raise Exception({'error':str(e.message)})

def get_document_by_id(id):
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
            raise Exception({'message':'Authorization token empty'})
        decoded_token = jwt.decode(auth_token, config['ACCESS_TOKEN_SECRET'], algorithms=["HS256"])
        return decoded_token
    except:
        raise Exception({'error':'invalid token'})

def get_all_documents_by_user_id(user_id):
    try:
        documents = db.session.query(Document).filter(Document.user_id == user_id).all()
        arr = [];
        for i in documents:
            arr.append(vars(i)['id'])
        return arr
    except Exception as e:
        raise Exception({'error':str(e.message)})
