import json
import sqlalchemy
from models.Document import Document
from models.db import db
from sqlalchemy.dialects.postgresql.base import UUID
from sqlalchemy.dialects.postgresql import JSON

class SharedDocument(db.Model):
    __tablename__ = 'shared_documents'
    id = db.Column(UUID(as_uuid=True), primary_key=True, unique=True, server_default=sqlalchemy.text("uuid_generate_v4()"),)
    document_id = db.Column(UUID(as_uuid=True), sqlalchemy.ForeignKey(Document.id, ondelete='CASCADE'), unique=False, nullable=False)
    email = db.Column(db.String(255), unique=False, nullable=False)
    public = db.Column(sqlalchemy.Boolean, unique=False, nullable=True)
    created_at = db.Column(db.DateTime(), nullable=False, server_default=db.func.now())
    updated_at = db.Column(db.DateTime(), nullable=False, server_default=db.func.now(), server_onupdate=db.func.now())

    def __serialize__(self):
        document_row = {"id": self.id, "document_id": self.document_id, "email": self.email, "public":self.public, "created_at": self.created_at, "updated_at": self.updated_at}
        serialized_row = json.dumps(document_row, default=str)
        return serialized_row

def __init__(self, id, document_id, email, public, created_at, updated_at):
    self.id = id
    self.document_id = document_id
    self.email = email
    self.public = public
    self.created_at = created_at
    self.updated_at = updated_at