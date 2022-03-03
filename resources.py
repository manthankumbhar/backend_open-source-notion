import datetime
from __main__ import app
from sendgrid_helper import send_reset_password_mail
from state_machine import create_token, create_user, get_user_by_email, token_valid_check, update_reset_password_token, update_user
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from time import timezone
from flask import jsonify, request, render_template
import jwt
import secrets
from config import config

bcrypt = Bcrypt(app)
cors = CORS(app)

@app.route('/', methods=['POST', 'GET'])
def hello_world():
    return jsonify({'success': 'Hello, World!'}), 200    
    
@app.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        email = data['email']
        password = data['password']
        if email == "" or None or password == "" or None:
            return jsonify({'error':'email or password not entered'}), 400
        user = get_user_by_email(email)
        if user is not None:
            return jsonify({'error':'This email has an existing account.'}), 400    
        hashed_password = bcrypt.generate_password_hash(password, 10).decode('UTF-8')
        create_user(email, hashed_password)
        user_id = get_user_by_email(email)['id']
        token = create_token(user_id)
        return jsonify(token), 200
    except Exception as e:
        return jsonify({'error': str(e.message)}), 500

@app.route('/signin', methods=['POST'])
def signin():
    try:
        data = request.get_json()
        email = data['email']
        password = data['password']
        if email == "" or None or password == "" or None:
            return jsonify({'error':'email or password not entered'}), 400
        user = get_user_by_email(email)
        if user is None:
            return jsonify({'error':'This email does not have an existing account.'}), 400
        if bcrypt.check_password_hash(user['password'], password) == True:
            token = create_token(user['id'])
            return jsonify(token), 200
        else:
            return jsonify({'error':'Incorrect email or password.'}), 400
    except Exception as e:
        return jsonify({'error': str(e.message)}), 500

@app.route('/reset-password', methods=['POST'])
def send_reset_password_link():
    try:
        data = request.get_json()
        email = data['email']
        if email == "" or None:
            return jsonify({'error':'email not entered'}), 400
        user = get_user_by_email(email)
        if user is None:
            return jsonify({'error':'This email does not have an existing account.'}), 400
        reset_password_last_requested_at = user['reset_password_last_requested_at']
        reset_password_hash = user['reset_password_hash']     
        if reset_password_last_requested_at is None and reset_password_hash is None:        
            new_reset_password_hash = secrets.token_urlsafe(48)
            update_reset_password_token(email, new_reset_password_hash)
            send_reset_password_mail(email,new_reset_password_hash)
            return jsonify({'success':'Check your inbox for the link to reset your password.'}), 200
        else:
            is_new_request = datetime.datetime.utcnow() > reset_password_last_requested_at + datetime.timedelta(minutes=15)
            if is_new_request is True:
                updated_reset_password_hash = secrets.token_urlsafe(48)
                update_reset_password_token(email, updated_reset_password_hash)
                send_reset_password_mail(email,updated_reset_password_hash)
                return jsonify({'success':'Check your inbox for the link to reset your password.'}), 200
            else:
                send_reset_password_mail(email,reset_password_hash)
                return jsonify({'success':'Check your inbox for the link to reset your password.'}), 200
    except Exception as e:
        return jsonify({'error':'Internal server error, please try again later'}), 500

@app.route('/reset-password/<token>', methods=['GET'])
def get_reset_password(token):
    try:
        user = token_valid_check(token)
        if user is None:
            return jsonify({'error':'token is invalid'}), 400
        reset_password_last_requested_at = user['reset_password_last_requested_at']
        is_token_expired = datetime.datetime.utcnow() > reset_password_last_requested_at + datetime.timedelta(minutes=15)
        if is_token_expired is True:
            return jsonify({'error':'link has expired'}), 400
        return render_template('reset-password.html', token = token), 200
    except Exception as e:
        return jsonify({'error':str(e.message)}), 500

@app.route('/reset-password/<token>', methods=['POST'])
def post_reset_password(token):
    try:
        user = token_valid_check(token)
        if user is None:
            return jsonify({'error':'Token is invalid'}), 400
        reset_password_last_requested_at = user['reset_password_last_requested_at']
        is_token_expired = datetime.datetime.utcnow() > reset_password_last_requested_at + datetime.timedelta(minutes=15)
        if is_token_expired is True:
            return jsonify({'error':'Link has expired'}), 400
        new_password = request.form['password']
        if new_password == "" or None:
            return jsonify({'error':'Password is not entered'}), 400
        hashed_new_password = bcrypt.generate_password_hash(new_password, 10).decode('UTF-8')
        updated_reset_password_hash = secrets.token_urlsafe(48)
        update_user(user['email'], hashed_new_password, updated_reset_password_hash)
        return jsonify({'success':'reset password successful!'}), 200
    except Exception as e:
        return jsonify({'error':str(e.message)}), 500

@app.route('/refresh-token', methods=['POST'])
def refresh_tokens():    
    try: 
        data = request.get_json()
        token_from_client = data['refreshToken']
        if token_from_client == '' or None:
            return jsonify({'error':'empty token'}), 400
        is_token_valid = jwt.decode(token_from_client, config['REFRESH_TOKEN_SECRET'], algorithms=["HS256"])
        user_id = is_token_valid['userid']
        token = create_token(user_id)
        return jsonify(token), 200
    except:
        return jsonify({'error':'invalid token'}), 400