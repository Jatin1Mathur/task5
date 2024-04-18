from app.models.model import db
from flask_mail import Message
from app import mail
from cryptography.fernet import Fernet
import base64


fernet_key = Fernet.generate_key()
cipher = Fernet(fernet_key)


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

    msg = Message('Password Reset Link', sender='your_email@gmail.com',
                  recipients=[user_email])
    msg.body = f'Hello,\n\nYour reset link is: {reset_link}'
    mail.send(msg)
    
    
def send_deactivation_link(eactivation_link, email):
    msg = Message('Password Reset Link', sender='your_email@gmail.com',
                  recipients=[email])
    msg.body = f'Hello,\n\nYour reset link is: {eactivation_link}'
    mail.send(msg)
    

def encrypt(data):
    data_bytes = data.encode('utf-8')
    encrypted_data = cipher.encrypt(data_bytes)
    return base64.urlsafe_b64encode(encrypted_data).decode('utf-8')


def decrypt(encoded_data):
    encrypted_data = base64.urlsafe_b64decode(encoded_data.encode('utf-8'))
    decrypted_data = cipher.decrypt(encrypted_data)
    return decrypted_data.decode('utf-8')
