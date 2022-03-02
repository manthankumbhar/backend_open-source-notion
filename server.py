import os
from flask import Flask
from models.User import db

app = Flask(__name__)

from config import *
from resources import *

if __name__ == '__main__':
    app.run(debug=True)

