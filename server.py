import datetime
import os
from flask import Flask, jsonify, request, render_template
from flask_bcrypt import Bcrypt
import jwt
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy
from sqlalchemy.dialects.postgresql.base import UUID
from uuid import uuid4
import secrets
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from flask_cors import CORS, cross_origin

app = Flask(__name__)
bcrypt = Bcrypt(app)
cors = CORS(app)

db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL').replace("://", "ql://", 1)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['ACCESS_TOKEN_SECRET'] =  os.environ.get('ACCESS_TOKEN_SECRET')
app.config['REFRESH_TOKEN_SECRET'] =  os.environ.get('REFRESH_TOKEN_SECRET')

class Users(db.Model):
    __tablename__ = 'users'
    id = db.Column(UUID(as_uuid=True), primary_key=True, unique=True, server_default=sqlalchemy.text("uuid_generate_v4()"),)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now(), server_onupdate=db.func.now())
    reset_password_hash = db.Column(db.String(64), unique=True, nullable=False)
    reset_password_last_requested_at = db.Column(db.DateTime, nullable=True)

def __init__(self, email, password, created_at, updated_at, reset_password_hash, reset_password_last_requested_at):
    self.email = email
    self.password = password    
    self.created_at = created_at
    self.updated_at = updated_at
    self.reset_password_hash = reset_password_hash
    self.reset_password_last_requested_at = reset_password_last_requested_at

@app.route('/', methods=['POST', 'GET'])
def hello_world():
    return jsonify({'success': 'Hello, World!'}), 200    

def get_data_by_email(email):
    count = db.session.query(Users).filter(Users.email == email).count()
    if count <= 0:
        return None
    if count == 1:
        user_details = db.session.query(Users).filter(Users.email == email)
        for i in user_details:
            return i.__dict__ 
    if count > 1:
        return {'error':'voilates the unique ability!'}, 400

def token_valid_check(token):
    count = db.session.query(Users).filter(Users.reset_password_hash == token).count()
    if count <= 0:
        return None
    if count == 1:
        user_details = db.session.query(Users).filter(Users.reset_password_hash == token)
        for i in user_details:
            return i.__dict__ 
    if count > 1:
        return {'error':'voilates the unique ability!'}, 400

def send_reset_password_mail(email, token):
    from_email = os.environ.get('SENDGRID_EMAIL')
    to_email = email
    subject = 'Reset password link'
    content = 'To reset your password'
    html_content = 'To reset your password <a href="https://backend-notion-clone.herokuapp.com/reset-password/%s">click here</a>' % token
    message = Mail(from_email, to_email, subject, content, html_content)
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        res = sg.send(message)
        if res.status_code == 202:
            return jsonify({'success':'email sent!'}), 200
        else:
            return jsonify({'error':'please try again later'}), 400            
    except Exception as e:
        return jsonify({'error':str(e.message)}), 400
    
@app.route('/signup', methods=['POST'])
@cross_origin()
def signup():
    data = request.get_json()
    email = data['email']
    password = data['password']
    if email == "" or None or password == "" or None:
        return jsonify({'error':'email or password not entered'}), 400
    data_from_db = get_data_by_email(email)
    if data_from_db is not None:
        return jsonify({'error':'user already exists!'}), 400    
    hashed_password = bcrypt.generate_password_hash(password, 10).decode('UTF-8')
    reset_password_hash = secrets.token_urlsafe(48)
    try:
        user = Users(
            email = email,
            password = hashed_password,
            reset_password_hash = reset_password_hash
        )
        db.session.add(user)
        db.session.commit()
        user_id = get_data_by_email(email)['id']
        accessToken = jwt.encode({'userid': str(user_id), 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['ACCESS_TOKEN_SECRET'])
        refreshToken = jwt.encode({'userid': str(user_id), 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24*365)}, app.config['REFRESH_TOKEN_SECRET'])
        return jsonify({'accessToken':accessToken.decode('UTF-8'), 'refreshToken': refreshToken.decode('UTF-8')}), 200
    except Exception as e:
        return jsonify({'error': str(e.message)}), 400

@app.route('/signin', methods=['POST'])
@cross_origin()
def signin():
    data = request.get_json()
    email = data['email']
    password = data['password']
    if email == "" or None or password == "" or None:
        return jsonify({'error':'email or password not entered'}), 400
    data_from_db = get_data_by_email(email)
    if data_from_db is None:
        return jsonify({'error':"user doesn't exist"}), 400
    try:
        if bcrypt.check_password_hash(data_from_db['password'], password) == True:
            accessToken = jwt.encode({'userid': str(data_from_db['id']), 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['ACCESS_TOKEN_SECRET'])            
            refreshToken = jwt.encode({'userid': str(data_from_db['id']), 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24*365)}, app.config['REFRESH_TOKEN_SECRET'])            
            return jsonify({'accessToken':accessToken.decode('UTF-8'), 'refreshToken': refreshToken.decode('UTF-8')}), 200
        else:
            return jsonify({'error':'incorrect email or password'}), 400
    except Exception as e:
        return jsonify({'error': str(e.message)}), 400

@app.route('/reset-password', methods=['POST'])
@cross_origin()
def send_reset_password_link():
    data = request.get_json()
    if data['email'] == "" or None:
        return jsonify({'error':'email not entered'}), 400
    data_from_db = get_data_by_email(data['email'])
    if data_from_db is None:
        return jsonify({'error':"user doesn't exist"}), 400
    reset_password_last_requested_at = data_from_db['reset_password_last_requested_at']
    reset_password_hash = data_from_db['reset_password_hash']     
    if reset_password_last_requested_at is None:        
        try:
            user = db.session.query(Users).filter(Users.email == data['email']).first()
            user.reset_password_last_requested_at = datetime.datetime.now()
            db.session.commit()
            send_reset_password_mail(data['email'],reset_password_hash)
            return jsonify({'success':'email sent!'}), 200
        except Exception as e:
            return jsonify({'error':str(e.message)}), 400
    if reset_password_last_requested_at is not None:
        is_new_request = datetime.datetime.now() > reset_password_last_requested_at + datetime.timedelta(minutes=15)
        if is_new_request is True:
            try:
                updated_reset_password_hash = secrets.token_urlsafe(48)
                user = db.session.query(Users).filter(Users.email == data['email']).first()
                user.reset_password_last_requested_at = datetime.datetime.now()
                user.reset_password_hash = updated_reset_password_hash
                db.session.commit()
                send_reset_password_mail(data['email'],updated_reset_password_hash)
                return jsonify({'success':'email sent!'}), 200
            except Exception as e:
                return jsonify({'error':str(e.message)}), 400
        else:
            try:
                send_reset_password_mail(data['email'],reset_password_hash)
                return jsonify({'success':'email sent!'}), 200
            except Exception as e:
                return jsonify({'error':str(e.message)}), 400

@app.route('/reset-password/<token>', methods=['GET'])
@cross_origin()
def get_reset_password(token):
    data_from_db = token_valid_check(token)
    if data_from_db is None:
        return jsonify({'error':'token is invalid'}), 400
    reset_password_last_requested_at = data_from_db['reset_password_last_requested_at']
    is_token_expired = datetime.datetime.now() > reset_password_last_requested_at + datetime.timedelta(minutes=15)
    if is_token_expired is True:
        return jsonify({'error':'link has expired'}), 400
    return render_template('reset-password.html', token = token), 200

@app.route('/reset-password/<token>', methods=['POST'])
@cross_origin()
def post_reset_password(token):
    data_from_db = token_valid_check(token)
    if data_from_db is None:
        return jsonify({'error':'token is invalid'}), 400
    reset_password_last_requested_at = data_from_db['reset_password_last_requested_at']
    is_token_expired = datetime.datetime.now() > reset_password_last_requested_at + datetime.timedelta(minutes=15)
    if is_token_expired is True:
        return jsonify({'error':'link has expired'}), 400
    new_password = request.form['password']
    if new_password == "" or None:
        return jsonify({'error':'password is not entered'}), 400
    try:
        updated_reset_password_hash = secrets.token_urlsafe(48)
        hashed_new_password = bcrypt.generate_password_hash(new_password, 10).decode('UTF-8')
        user = db.session.query(Users).filter(Users.email == data_from_db['email']).first()
        user.reset_password_hash = updated_reset_password_hash
        user.password = hashed_new_password
        db.session.commit()
        return jsonify({'success':'reset password successful!'}), 200
    except Exception as e:
        return jsonify({'error':str(e.message)}), 400

@app.route('/refresh-tokens', methods=['POST'])
@cross_origin()
def refresh_tokens():    
    data = request.get_json()
    token_from_client = data['refreshToken']
    if token_from_client == '' or None:
        return jsonify({'error':'empty token'}), 400
    try: 
        is_token_valid = jwt.decode(token_from_client, app.config['REFRESH_TOKEN_SECRET'], algorithms=["HS256"])
        user_id = is_token_valid['userid']
        accessToken = jwt.encode({'userid': str(user_id), 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['ACCESS_TOKEN_SECRET'])            
        refreshToken = jwt.encode({'userid': str(user_id), 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24*365)}, app.config['REFRESH_TOKEN_SECRET'])
        return jsonify({'accessToken':accessToken.decode('UTF-8'), 'refreshToken': refreshToken.decode('UTF-8')}), 200
    except:
        return jsonify({'error':'invalid token'}), 400

if __name__ == '__main__':
    app.run(debug=True)

