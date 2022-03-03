import os

config = {
    'SQLALCHEMY_DATABASE_URI': os.environ.get('DATABASE_URL'),
    'SQLALCHEMY_TRACK_MODIFICATIONS':False,
    'ACCESS_TOKEN_SECRET':os.environ.get('ACCESS_TOKEN_SECRET'),
    'REFRESH_TOKEN_SECRET':os.environ.get('REFRESH_TOKEN_SECRET'),
    'SENDGRID_EMAIL':os.environ.get('SENDGRID_EMAIL'),
    'SENDGRID_API_KEY':os.environ.get('SENDGRID_API_KEY'),
    'SENDGRID_SERVER_LINK':os.environ.get('SENDGRID_SERVER_LINK'),
    'DEBUG': os.environ.get('DEBUG'),
}

for i in config.values():
    if i == "" or i == None:
        raise Exception({'error':'environment variable not defined'})