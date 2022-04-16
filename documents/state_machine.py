from config import config
from models.db import db
from models.User import User
import jwt
from models.Document import Document

def get_user_by_user_id(user_id):
    users = db.session.query(User).filter(User.id == user_id)
    if users.count() <= 0:
        return None
    if users.count() == 1:
        for i in users:
            return vars(i)
    if users.count() > 1:
        raise Exception({'error':'voilates the unique ability!'})
    
def upsert_document(user_id):
    document = Document(
        user_id = user_id
    )
    db.session.add(document)
    db.session.commit()
    document_row = db.session.query(Document).filter(Document.id == document.id).first()
    return vars(document_row)

def get_document_by_id(id):
    documents = db.session.query(Document).filter(Document.id == id)
    if documents.count() <= 0:
        return None
    if documents.count() == 1:
        for i in documents:
            return vars(i)
    if documents.count() > 1:
        raise Exception({'error':'voilates the unique ability!'})

def token_valid_check(auth_header):
    auth_token = auth_header.split(' ')[1]
    if auth_token == "" or auth_token == None:
        raise Exception({'message':'Authorization token empty'})
    decoded_token = jwt.decode(auth_token, config['ACCESS_TOKEN_SECRET'], algorithms=["HS256"])
    return decoded_token

def get_all_documents_by_user_id(user_id):
    documents = db.session.query(Document).filter(Document.user_id == user_id).all()
    document_id_array = []
    for document in documents:
        document_id_array.append({'id':vars(document)['id'], 'name':vars(document)['name']})
    return document_id_array
