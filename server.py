import datetime
import os
from pyexpat import model
from time import timezone
from flask import Flask, jsonify, request, render_template
from flask_bcrypt import Bcrypt
import jwt
import secrets
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from flask_cors import CORS, cross_origin
from models.User import db, User

app = Flask(__name__)
bcrypt = Bcrypt(app)
cors = CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost/test_flask'
# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL').replace("postgresql://", "postgres://", 1) # sqlalchemy documents need the database name to exclude "ql" and this is the best way to remove it
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

def get_user_by_email(email):
    user = db.session.query(User).filter(User.email == email)
    if user.count() <= 0:
        return None
    if user.count() == 1:
        for i in user:
            return i.__dict__ 
    if user.count() > 1:
        return {'error':'voilates the unique ability!'}, 500

def token_valid_check(token):
    user = db.session.query(User).filter(User.reset_password_hash == token)
    if user.count() <= 0:
        return None
    if user.count() == 1:
        for i in user:
            return i.__dict__ 
    if user.count() > 1:
        return {'error':'voilates the unique ability!'}, 500

def send_reset_password_mail(email, token):
    from_email = app.config['SENDGRID_EMAIL']
    to_email = email
    subject = 'Reset password link'
    content = 'To reset your password'
    html_content = 'To reset your password <a href="https://backend-notion-clone.herokuapp.com/reset-password/%s">click here</a>' % token
    message = Mail(from_email, to_email, subject, content, html_content)
    try:
        sg = SendGridAPIClient(app.config['SENDGRID_API_KEY'])
        res = sg.send(message)
        if res.status_code == 202:
            return jsonify({'success':'email sent!'}), 200
        else:
            return jsonify({'error':'please try again later'}), 400            
    except Exception as e:
        return jsonify({'error':str(e.message)}), 500
    
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
    reset_password_hash = secrets.token_urlsafe(48)
    try:
        user = User(
            email = email,
            password = hashed_password,
            reset_password_hash = reset_password_hash
        )
        db.session.add(user)
        db.session.commit()
        user_id = get_user_by_email(email)['id']
        accessToken = jwt.encode({'userid': str(user_id), 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['ACCESS_TOKEN_SECRET'])
        refreshToken = jwt.encode({'userid': str(user_id), 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24*365)}, app.config['REFRESH_TOKEN_SECRET'])
        return jsonify({'accessToken':accessToken.decode('UTF-8'), 'refreshToken': refreshToken.decode('UTF-8')}), 200
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
            accessToken = jwt.encode({'userid': str(data_from_db['id']), 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['ACCESS_TOKEN_SECRET'])            
            refreshToken = jwt.encode({'userid': str(data_from_db['id']), 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24*365)}, app.config['REFRESH_TOKEN_SECRET'])            
            return jsonify({'accessToken':accessToken.decode('UTF-8'), 'refreshToken': refreshToken.decode('UTF-8')}), 200
        else:
            return jsonify({'error':'Incorrect email or password.'}), 400
    except Exception as e:
        return jsonify({'error': str(e.message)}), 500

@app.route('/reset-password', methods=['POST'])
def send_reset_password_link():
    data = request.get_json()
    if data['email'] == "" or None:
        return jsonify({'error':'email not entered'}), 400
    data_from_db = get_user_by_email(data['email'])
    if data_from_db is None:
        return jsonify({'error':'This email does not have an existing account.'}), 400
    reset_password_last_requested_at = data_from_db['reset_password_last_requested_at']
    reset_password_hash = data_from_db['reset_password_hash']     
    if reset_password_last_requested_at is None:        
        try:
            user = db.session.query(User).filter(User.email == data['email']).first()
            user.reset_password_last_requested_at = datetime.datetime.utcnow()
            db.session.commit()
            send_reset_password_mail(data['email'],reset_password_hash)
            return jsonify({'success':'Check your inbox for the link to reset your password.'}), 200
        except Exception as e:
            return jsonify({'error':'Internal server error, please try again later'}), 500
    if reset_password_last_requested_at is not None:
        is_new_request = datetime.datetime.utcnow() > reset_password_last_requested_at + datetime.timedelta(minutes=15)
        if is_new_request is True:
            try:
                updated_reset_password_hash = secrets.token_urlsafe(48)
                user = db.session.query(User).filter(User.email == data['email']).first()
                user.reset_password_last_requested_at = datetime.datetime.utcnow()
                user.reset_password_hash = updated_reset_password_hash
                db.session.commit()
                send_reset_password_mail(data['email'],updated_reset_password_hash)
                return jsonify({'success':'Check your inbox for the link to reset your password.'}), 200
            except Exception as e:
                return jsonify({'error':'Internal server error, please try again later'}), 500
        else:
            try:
                send_reset_password_mail(data['email'],reset_password_hash)
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
        updated_reset_password_hash = secrets.token_urlsafe(48)
        hashed_new_password = bcrypt.generate_password_hash(new_password, 10).decode('UTF-8')
        user = db.session.query(User).filter(User.email == data_from_db['email']).first()
        user.reset_password_hash = updated_reset_password_hash
        user.password = hashed_new_password
        db.session.commit()
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
        accessToken = jwt.encode({'userid': str(user_id), 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['ACCESS_TOKEN_SECRET'])            
        refreshToken = jwt.encode({'userid': str(user_id), 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24*365)}, app.config['REFRESH_TOKEN_SECRET'])
        return jsonify({'accessToken':accessToken.decode('UTF-8'), 'refreshToken': refreshToken.decode('UTF-8')}), 200
    except:
        return jsonify({'error':'invalid token'}), 400

if __name__ == '__main__':
    app.run(debug=True)

