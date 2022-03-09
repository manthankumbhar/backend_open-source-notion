import os

env_list = [
    'DATABASE_URL', 
    'DATABASE_TRACK_MODIFICATIONS',
    'ACCESS_TOKEN_SECRET',
    'REFRESH_TOKEN_SECRET',
    'SENDGRID_EMAIL',
    'SENDGRID_API_KEY',
    'SENDGRID_SERVER_LINK',
    'DEBUG', 
]

for i in env_list:
    if i not in os.environ:
        raise Exception({'error':'%s - environment variable not defined' % i})

config = {}
for i in env_list:
    config[i] = os.environ.get(i)