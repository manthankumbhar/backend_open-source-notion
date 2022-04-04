from flask import Flask
from models.db import db
from config import config
from flask_cors import CORS
from resources import resources

app = Flask(__name__)
app.register_blueprint(resources, url_prefix="")
cors = CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = config['DATABASE_URL'].replace("postgres://", "postgresql://", 1) # sqlalchemy documents need the database name to include "ql" and this is the best way to remove it
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config['DATABASE_TRACK_MODIFICATIONS']
db.init_app(app)
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=config['DEBUG'])

