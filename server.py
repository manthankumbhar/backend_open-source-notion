import datetime
import os
from pyexpat import model
import re
from time import timezone
from flask import Flask, jsonify, request, render_template
from flask_bcrypt import Bcrypt
import jwt
import secrets
from flask_cors import CORS, cross_origin
from models.User import db, User
from sendgrid_helper import send_reset_password_mail
from state_machine import create_token, create_user, get_user_by_email, token_valid_check, update_reset_password_token, update_user

app = Flask(__name__)
bcrypt = Bcrypt(app)
cors = CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
# .replace("postgres://", "postgresql://", 1) # sqlalchemy documents need the database name to include "ql" and this is the best way to remove it
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
with app.app_context():
    db.create_all()
app.config['ACCESS_TOKEN_SECRET'] =  os.environ.get('ACCESS_TOKEN_SECRET')
app.config['REFRESH_TOKEN_SECRET'] =  os.environ.get('REFRESH_TOKEN_SECRET')
app.config['SENDGRID_EMAIL'] = os.environ.get('SENDGRID_EMAIL')
app.config['SENDGRID_API_KEY'] = os.environ.get('SENDGRID_API_KEY')

@app.route('/', methods=['POST', 'GET'])
def hello_world():
    return jsonify({'success': 'Hello, World!'}), 200    
    
@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    email = data['email']
    password = data['password']
    if email == "" or None or password == "" or None:
        return jsonify({'error':'email or password not entered'}), 400
    data_from_db = get_user_by_email(email)
    if data_from_db is not None:
        return jsonify({'error':'This email has an existing account.'}), 400    
    hashed_password = bcrypt.generate_password_hash(password, 10).decode('UTF-8')
    try:
        create_user(email, hashed_password)
        user_id = get_user_by_email(email)['id']
        token = create_token(user_id)
        return token, 200
    except Exception as e:
        return jsonify({'error': str(e.message)}), 500

@app.route('/signin', methods=['POST'])
def signin():
    data = request.get_json()
    email = data['email']
    password = data['password']
    if email == "" or None or password == "" or None:
        return jsonify({'error':'email or password not entered'}), 400
    data_from_db = get_user_by_email(email)
    if data_from_db is None:
        return jsonify({'error':'This email does not have an existing account.'}), 400
    try:
        if bcrypt.check_password_hash(data_from_db['password'], password) == True:
            token = create_token(data_from_db['id'])
            return token, 200
        else:
            return jsonify({'error':'Incorrect email or password.'}), 400
    except Exception as e:
        return jsonify({'error': str(e.message)}), 500

@app.route('/reset-password', methods=['POST'])
def send_reset_password_link():
    data = request.get_json()
    email = data['email']
    if email == "" or None:
        return jsonify({'error':'email not entered'}), 400
    data_from_db = get_user_by_email(email)
    if data_from_db is None:
        return jsonify({'error':'This email does not have an existing account.'}), 400
    reset_password_last_requested_at = data_from_db['reset_password_last_requested_at']
    reset_password_hash = data_from_db['reset_password_hash']     
    if reset_password_last_requested_at is None and reset_password_hash is None:        
        try:
            new_reset_password_hash = secrets.token_urlsafe(48)
            update_reset_password_token(email, new_reset_password_hash)
            send_reset_password_mail(email,new_reset_password_hash)
            return jsonify({'success':'Check your inbox for the link to reset your password.'}), 200
        except Exception as e:
            return jsonify({'error':'Internal server error, please try again later'}), 500
    if reset_password_last_requested_at is not None and reset_password_hash is not None:
        is_new_request = datetime.datetime.utcnow() > reset_password_last_requested_at + datetime.timedelta(minutes=15)
        if is_new_request is True:
            try:
                updated_reset_password_hash = secrets.token_urlsafe(48)
                update_reset_password_token(email, updated_reset_password_hash)
                send_reset_password_mail(email,updated_reset_password_hash)
                return jsonify({'success':'Check your inbox for the link to reset your password.'}), 200
            except Exception as e:
                return jsonify({'error':'Internal server error, please try again later'}), 500
        else:
            try:
                send_reset_password_mail(email,reset_password_hash)
                return jsonify({'success':'Check your inbox for the link to reset your password.'}), 200
            except Exception as e:
                return jsonify({'error':'Internal server error, please try again later'}), 500

@app.route('/reset-password/<token>', methods=['GET'])
def get_reset_password(token):
    data_from_db = token_valid_check(token)
    if data_from_db is None:
        return jsonify({'error':'token is invalid'}), 400
    reset_password_last_requested_at = data_from_db['reset_password_last_requested_at']
    is_token_expired = datetime.datetime.utcnow() > reset_password_last_requested_at + datetime.timedelta(minutes=15)
    if is_token_expired is True:
        return jsonify({'error':'link has expired'}), 400
    return render_template('reset-password.html', token = token), 200

@app.route('/reset-password/<token>', methods=['POST'])
def post_reset_password(token):
    data_from_db = token_valid_check(token)
    if data_from_db is None:
        return jsonify({'error':'Token is invalid'}), 400
    reset_password_last_requested_at = data_from_db['reset_password_last_requested_at']
    is_token_expired = datetime.datetime.utcnow() > reset_password_last_requested_at + datetime.timedelta(minutes=15)
    if is_token_expired is True:
        return jsonify({'error':'Link has expired'}), 400
    new_password = request.form['password']
    if new_password == "" or None:
        return jsonify({'error':'Password is not entered'}), 400
    try:
        hashed_new_password = bcrypt.generate_password_hash(new_password, 10).decode('UTF-8')
        updated_reset_password_hash = secrets.token_urlsafe(48)
        update_user(data_from_db['email'], hashed_new_password, updated_reset_password_hash)
        return jsonify({'success':'reset password successful!'}), 200
    except Exception as e:
        return jsonify({'error':str(e.message)}), 500

@app.route('/refresh-token', methods=['POST'])
def refresh_tokens():    
    data = request.get_json()
    token_from_client = data['refreshToken']
    if token_from_client == '' or None:
        return jsonify({'error':'empty token'}), 400
    try: 
        is_token_valid = jwt.decode(token_from_client, app.config['REFRESH_TOKEN_SECRET'], algorithms=["HS256"])
        user_id = is_token_valid['userid']
        token = create_token(user_id)
        return token, 200
    except:
        return jsonify({'error':'invalid token'}), 400

if __name__ == '__main__':
    app.run(debug=True)

