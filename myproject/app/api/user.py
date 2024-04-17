import base64
from datetime import datetime, timedelta
import time
import secrets
from sqlalchemy.exc import IntegrityError
import random
from flask_ngrok import run_with_ngrok 
from flask import Flask, request, jsonify, Blueprint, Response 
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

from app.models.model import db, user, Rest_Token
from app.utlis import delete, save_changes, add, rollback, send_reset_password_email , send_deactivation_link , encrypt , decrypt
from app import bcrypt
from app.services.user_services import user_filter, User_log, User_update, User_id, existing_users, update_password , user_filter_token , user_check
from app.error_management.error_response import e_response, Response
from app.error_management.success_response import success_response
from app.validator.validators import check_user_required_fields
from config import basesit 


blueprint = Blueprint('auth', __name__, url_prefix='/auth')


@blueprint.route("/register", methods=['POST'])
def register_user():
    data = request.json
    if not check_user_required_fields(data):
        return e_response('400')
    if user_filter(data.get('email')):
        return e_response('400')
    
    hashed_password = bcrypt.generate_password_hash(data.get('password')).decode('utf-8')
    new_user = user(data.get('email'), data.get('username'), password=hashed_password)
    add(new_user)
    return success_response( "User created successfully", 200) 

@blueprint.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    User = user.query.filter_by(email=email).first()

    if not User:
        return e_response("400")

    hashed_password = User.password
    if not bcrypt.check_password_hash(hashed_password, password):
       
        User.link_count = User.link_count + 1 if User.link_count else 1
        
        if User.link_count == 3:
            
            expire_time = datetime.now() + timedelta(seconds=120)
            e_expire_time = base64.urlsafe_b64encode(str(expire_time.timestamp()).encode('utf-8')).decode('utf-8')
            link = base64.b64encode(email.encode('utf-8')).decode('utf-8')
            deactivation_link = basesit.DEACTIVATION_LINK + link + str(e_expire_time)
            send_deactivation_link(deactivation_link, email)
            return e_response('400')

        
        add(User)
        return e_response('401')
    else:
       
        User.link_count = 0
        add(User)

    user_log = User.query.filter_by(email=email).first()
    if not user_log:
        return e_response('404')

    if bcrypt.check_password_hash(user_log.password, password):
        access_token = create_access_token(identity={'id': User.id, 'username': User.username, 'email': User.email})
        return success_response({'access_token': access_token}, 200)
    else:
        return e_response('401')

    
@blueprint.route('/retrieve', methods=['GET'])
@jwt_required()
def get_user_info():
    current_user = get_jwt_identity()
    if current_user['id']:
        user = User_id(current_user['id'])
        if user:
            return success_response({'email': user.email, 'username': user.username}, 200)
    return e_response('401')


@blueprint.route('/update', methods=['PUT'])
@jwt_required()
def update_user():
    data = request.json
    user_id = get_jwt_identity()
    User = User_update(user_id['id'])
    if not User:
        return e_response('400') 
    if not User:
        return e_response('404')
    new_username = data.get('username', User.username)
    existing_user = existing_users(new_username, user_id)
    if existing_user:
        return e_response('409')
    User.email = data.get('email', User.email)
    User.username = new_username
    try:
        save_changes()
        return success_response({'message': 'User updated successfully'}, 200)
    except IntegrityError:
        rollback()
        return e_response('409')


@blueprint.route("/delete", methods=['DELETE'])
@jwt_required()
def delete_user():
    current_user = get_jwt_identity()
    if not current_user['id']:
        return e_response('404')
        delete(user_id)
    return success_response('User deleted successfully', 201)



@blueprint.route("/change_password", methods=['POST'])
@jwt_required()
def change_password():
    current_user = get_jwt_identity()
    data = request.json
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    if new_password == old_password:
        return e_response('409')
    pasword_change = current_user['email']
    User = update_password(pasword_change)
    if not User:
        return e_response('404')
    if not bcrypt.check_password_hash(User.password, old_password):
        return e_response('400')
    hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
    User.password = hashed_password
    save_changes()
    return success_response('Password changed successfully', 200)




@blueprint.route('/forget', methods=['POST'])
def forget_password():
    data = request.json
    email = data.get('email')
    User = user.query.filter_by(email=email).first()
    if not User:
        return e_response('404')  
    expire_time = datetime.now() + timedelta(seconds=240)
    token = secrets.token_urlsafe(4)
    encoded_email = encrypt(email)  
    token_encode = base64.urlsafe_b64encode(token.encode('utf-8')).decode('utf-8')
    link = encoded_email + '.' + token_encode
    reset_link = basesit.REST_LINK + link  
    print(reset_link)
    auth_token = Rest_Token.query.filter_by(user_id=user.id).first()
    if auth_token:
        auth_token.token = token_encode
        auth_token.expire_time = expire_time
        save_changes()
    else:
        reset_data = Rest_Token(user_id=User.id, token=token_encode, expire_time=expire_time, User_Status=True)
        add(reset_data)
        send_reset_password_email(email, reset_link)    
    return success_response('Reset password link sent to your email', 200)  

@blueprint.route('/reset/<link>', methods=['POST'])
def reset_password(link):
    email, token_encode = link.split('.')
    email = decrypt(email)  
    data = request.json
    new_password = data.get('new_password')
    confirm_password = data.get('confirm_password')
    if new_password != confirm_password:
        return e_response('401')
    User = user.query.filter_by(email=email).first()
    if not User:
        return e_response('402')
    auth_token = Rest_Token.query.filter_by(user_id=User.id).first()
    if not auth_token:
        return e_response('403')
    time = datetime.now()
    expire_time = auth_token.expire_time
    if time > expire_time:
        return e_response('404')
    if auth_token.token != token_encode:
        return e_response('405')
    hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
    User.password = hashed_password
    auth_token.User_Status = True
    save_changes()
    return success_response('Password reset successful', 200)
