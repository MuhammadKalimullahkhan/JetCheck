from flask import flash, render_template
from jetcheck import app
from flask_mail import Mail, Message


app.config['MAIL_SERVER'] = 'mail.jetck.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'info@jetck.com'
app.config['MAIL_PASSWORD'] = 'AoCqTl!TO,K%'
app.config['MAIL_DEFAULT_SENDER'] = ('JetCheck', 'jetcheck@jetck.com')


mail = Mail(app)


def send_email(to, subject, body):
    msg = Message(subject, recipients=[to])
    msg.body = body
    mail.send(msg)


def generate_verification_email_html(data:dict):
    return render_template('mail/verify_email.html', data=data)


def send_email_verification_mail(data: dict):
    subject = 'Verify Email Address - JetCheck'
    msg = Message(subject=subject, recipients=[data['to']])
    msg.html = generate_verification_email_html(data)
    mail.send(msg)
