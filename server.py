import os
from flask import Flask
from models.User import db

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL').replace("postgres://", "postgresql://", 1) # sqlalchemy documents need the database name to include "ql" and this is the best way to remove it
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
with app.app_context():
    db.create_all()
app.config['ACCESS_TOKEN_SECRET'] =  os.environ.get('ACCESS_TOKEN_SECRET')
app.config['REFRESH_TOKEN_SECRET'] =  os.environ.get('REFRESH_TOKEN_SECRET')
app.config['SENDGRID_EMAIL'] = os.environ.get('SENDGRID_EMAIL')
app.config['SENDGRID_API_KEY'] = os.environ.get('SENDGRID_API_KEY')

from resources import *

if __name__ == '__main__':
    app.run(debug=True)

