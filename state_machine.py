from flask import jsonify
from models.User import User, SQLAlchemy
from server import get_user_by_email

db = SQLAlchemy()

def create_user(data):
    user = User(
        data
    )
    db.session.add(user)
    db.session.commit()

    





