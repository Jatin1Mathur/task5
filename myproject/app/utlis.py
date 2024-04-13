from app.models.model import db
from flask_mail import Mail, Message
from app import mail


def add(obj):
    db.session.add(obj)
    db.session.commit()


def save_changes():
    db.session.commit()


def delete(obj):
    db.session.delete(obj)
    db.session.commit()


def rollback():
    db.session.rollback()
    

def send_reset_password_email(user_email, reset_link):
    msg = Message('Password Reset Link', sender='your_email@gmail.com', recipients=[user_email])
    msg.body = f'Hello,\n\nYour reset link is: {reset_link}'
    mail.send(msg)
    
def send_deactivation_link(eactivation_link,email):
    msg = Message('Password Reset Link', sender='your_email@gmail.com', recipients=[email])
    msg.body = f'Hello,\n\nYour reset link is: {eactivation_link}'
    mail.send(msg)
    
        
