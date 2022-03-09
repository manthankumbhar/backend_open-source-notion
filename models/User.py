import sqlalchemy
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql.base import UUID

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(UUID(as_uuid=True), primary_key=True, unique=True, server_default=sqlalchemy.text("uuid_generate_v4()"),)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime(), nullable=False, server_default=db.func.now())
    updated_at = db.Column(db.DateTime(), nullable=False, server_default=db.func.now(), server_onupdate=db.func.now())
    reset_password_hash = db.Column(db.String(64), unique=True, nullable=True)
    reset_password_last_requested_at = db.Column(db.DateTime(), nullable=True)

def __init__(self, email, password, created_at, updated_at, reset_password_hash, reset_password_last_requested_at):
    self.email = email
    self.password = password    
    self.created_at = created_at
    self.updated_at = updated_at
    self.reset_password_hash = reset_password_hash
    self.reset_password_last_requested_at = reset_password_last_requested_at