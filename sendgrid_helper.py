import os
from flask import jsonify
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def send_reset_password_mail(email, token):
    server_link = os.environ.get('SENDGRID_SERVER_LINK')
    from_email = os.environ.get('SENDGRID_EMAIL')
    to_email = email
    subject = 'Reset password link'
    content = 'To reset your password'
    html_content = 'To reset your password <a href="%s/reset-password/%s">click here</a>' % (server_link, token)
    message = Mail(from_email, to_email, subject, content, html_content)
    try:
        sg = SendGridAPIClient()
        res = sg.send(message)
        if res.status_code == 202:
            return jsonify({'success':'email sent!'}), 200
        else:
            return jsonify({'error':'please try again later'}), 400            
    except Exception as e:
        return jsonify({'error':str(e.message)}), 500