import os
from flask import Flask
from models.User import db
from config import config

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = config['SQLALCHEMY_DATABASE_URI'].replace("postgres://", "postgresql://", 1) # sqlalchemy documents need the database name to include "ql" and this is the best way to remove it
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config['SQLALCHEMY_TRACK_MODIFICATIONS']
db.init_app(app)
with app.app_context():
    db.create_all()

import resources

if __name__ == '__main__':
    app.run(debug=config['DEBUG'])

