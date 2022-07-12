from models.db import db
from models.User import User
from models.Document import Document
from models.SharedDocument import SharedDocument

def get_user_by_user_id(user_id):
    users = db.session.query(User).filter(User.id == user_id)
    if users.count() <= 0:
        return None
    if users.count() == 1:
        for i in users:
            return vars(i)
    if users.count() > 1:
        raise Exception({'error':'voilates the unique ability!'})

def get_user_by_email(email):
    users = db.session.query(User).filter(User.email == email)
    if users.count() <= 0:
        return None
    if users.count() == 1:
        return users[0]
    if users.count() > 1:
        raise Exception({'error':'voilates the unique ability!'})
    
def upsert_document(user_id):
    document = Document(
        user_id = user_id
    )
    db.session.add(document)
    db.session.commit()
    document_row = db.session.query(Document).filter(Document.id == document.id).first()
    return document_row

def get_document_by_id(id):
    documents = db.session.query(Document).filter(Document.id == id)
    if documents.count() <= 0:
        return None
    if documents.count() == 1:
        return documents[0]
    if documents.count() > 1:
        raise Exception({'error':'voilates the unique ability!'})

def get_all_documents_by_user_id(user_id, email):
    documents = db.session.query(Document).filter(Document.user_id == user_id).all()
    document_id_array = []
    for document in documents:
        document_id_array.append({'id':document.id, 'name':document.name})

    shared_documents = db.session.query(SharedDocument).filter(SharedDocument.email == email, SharedDocument.public == None)
    shared_documents_array = []
    for shared_document in shared_documents:
        document_name = get_document_by_id(shared_document.document_id).name
        shared_documents_array.append({'id':shared_document.document_id, 'name':document_name})
    return {"shared_documents":shared_documents_array, "documents": document_id_array}

def update_document_by_document_id(document_id, data_from_user, doc_name_from_user):
    document = db.session.query(Document).filter(Document.id == document_id).first()
    document.data = data_from_user
    document.name = doc_name_from_user
    db.session.commit()
    return {'data updated'}

def update_document_data_by_document_id(document_id, data_from_user):
    document = db.session.query(Document).filter(Document.id == document_id).first()
    document.data = data_from_user
    db.session.commit()
    return {'data updated'}

def delete_document(document_id):
    document = db.session.query(Document).filter(Document.id == document_id).first()
    db.session.delete(document)
    db.session.commit()

def upsert_shared_document(document_id, email):
    shared_document = SharedDocument(
        document_id = document_id,
        email = email
    )
    db.session.add(shared_document)
    db.session.commit()
    document_row = db.session.query(SharedDocument).filter(SharedDocument.id == shared_document.id).first()
    return document_row

def upsert_shared_document_with_public(document_id, email, public):
    shared_document = SharedDocument(
        document_id = document_id,
        email = email,
        public = public
    )
    db.session.add(shared_document)
    db.session.commit()
    document_row = db.session.query(SharedDocument).filter(SharedDocument.id == shared_document.id).first()
    return document_row

def update_shared_document(document_id, email, public):
    shared_document = db.session.query(SharedDocument).filter(SharedDocument.document_id == document_id, SharedDocument.email == email).first()
    shared_document.public = public
    db.session.commit()
    return {'data updated'}

def get_shared_document_by_id_and_email(id, email):
    shared_document = db.session.query(SharedDocument).filter(SharedDocument.document_id == id, SharedDocument.email == email)
    if shared_document.count() <= 0:
        return None
    if shared_document.count() == 1:
        return shared_document[0]
    if shared_document.count() > 1:
        raise Exception({'error':'voilates the unique ability!'})