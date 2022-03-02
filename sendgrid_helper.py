from distutils.log import error
import os
from flask import jsonify
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from server import app

def send_reset_password_mail(email, token):
    try:
        server_link = app.config['SENDGRID_SERVER_LINK']
        from_email = app.config['SENDGRID_EMAIL']
        subject = 'Reset password link'
        content = 'To reset your password'
        html_content = 'To reset your password <a href="%s/reset-password/%s">click here</a>' % (server_link, token)
        message = Mail(from_email, email, subject, content, html_content)
        sg = SendGridAPIClient()
        res = sg.send(message)
        if res.status_code == 202:
            return {'success':'email sent!'}
        else:
            raise Exception({'error':'please try again later'})            
    except Exception as e:
        raise Exception({'error':str(e.message)})