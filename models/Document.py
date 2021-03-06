import json
import sqlalchemy
from models.db import db
from sqlalchemy.dialects.postgresql.base import UUID
from sqlalchemy.dialects.postgresql import JSON

class Document(db.Model):
    __tablename__ = 'documents'
    id = db.Column(UUID(as_uuid=True), primary_key=True, unique=True, server_default=sqlalchemy.text("uuid_generate_v4()"),)
    user_id = db.Column(UUID(as_uuid=True), unique=False, nullable=False)
    data = db.Column(JSON, nullable=True)
    name = db.Column(db.String(30), nullable=True)
    created_at = db.Column(db.DateTime(), nullable=False, server_default=db.func.now())
    updated_at = db.Column(db.DateTime(), nullable=False, server_default=db.func.now(), server_onupdate=db.func.now())

    def __serialize__(self):
        document_row = {"id": self.id, "user_id": self.user_id, "data":self.data, "name":self.name, "created_at": self.created_at, "updated_at": self.updated_at}
        serialized_row = json.dumps(document_row, default=str)
        return serialized_row

def __init__(self, id, user_id, data, name, created_at, updated_at):
    self.id = id
    self.user_id = user_id 
    self.data = data
    self.name = name
    self.created_at = created_at
    self.updated_at = updated_at 