import base64
import secrets
from datetime import datetime, timedelta 
from sqlalchemy.exc import IntegrityError

from flask import request, Blueprint
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from app.models.model import User, Rest_Token
from app.utlis import delete, save_changes, add, rollback, send_reset_password_email, send_deactivation_link, encrypt, decrypt
from app import bcrypt
from app.services.user_services import user_filter,  User_update, User_id, existing_users, update_password
from app.error_management.error_response import error_response
from app.error_management.success_response import success_response
from app.validator.validators import check_user_required_fields
from config import basesit


blueprint = Blueprint('auth', __name__, url_prefix='/auth')


@blueprint.route("/register", methods=['POST'])
def register_user():
    data = request.json
    if not check_user_required_fields(data):
        return error_response('400')
    if user_filter(data.get('email')):
        return error_response('400')
    hashed_password = bcrypt.generate_password_hash(data.get('password')).decode('utf-8')
    new_user = User(data.get('email'), data.get('username'),
                    password=hashed_password)
    add(new_user)
    return success_response("User created successfully", 200) 


@blueprint.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    user = User.query.filter_by(email=email).first()

    if not user:
        return error_response("404") 

    if not bcrypt.check_password_hash(user.password, password):
        if user.link_count is None:
            user.link_count = 1
        else:
            user.link_count += 1
        if user.link_count == 4:
            token = secrets.token_urlsafe(4)
            encoded_email_id = base64.b64encode(email.encode('utf-8')).decode('utf-8')
            link = base64.b64encode(token.encode('utf-8')).decode('utf-8')
            deactivation_link = basesit.DEACTIVATION_LINK + encoded_email_id + link
            send_deactivation_link(deactivation_link, email)        
            return error_response('401')  
        add(user)
        print(user)
        return error_response('401')  
    else:
        user_log = user.query.filter_by(email=email).first()
    if not user_log:
        return error_response('404')

    if bcrypt.check_password_hash(user_log.password, password):
        access_token = create_access_token(identity={'id': user.id,
                                                     'username': user.username,
                                                     'email': user.email})
        return success_response({'access_token': access_token}, 200)
    else:
        return error_response('401')

   
@blueprint.route('/retrieve', methods=['GET'])
@jwt_required()
def get_user_info():
    current_user = get_jwt_identity()
    if current_user['id']:
        user = User_id(current_user['id'])
        if user:
            return success_response({'email': user.email,
                                     'username': user.username}, 200)
    return error_response('401')


@blueprint.route('/update', methods=['PUT'])
@jwt_required()
def update_user():
    data = request.json
    user_id = get_jwt_identity()
    user = User_update(user_id['id'])
    if not user:
        return error_response('400') 
    if not user:
        return error_response('404')
    new_username = data.get('username', user.username)
    existing_user = existing_users(new_username, user_id)
    if existing_user:
        return error_response('409')
    user.email = data.get('email', user.email)
    user.username = new_username
    try:
        save_changes()
        return success_response({'message': 'User updated successfully'}, 200)
    except IntegrityError:
        rollback()
        return error_response('409')


@blueprint.route("/delete", methods=['DELETE'])
@jwt_required()
def delete_user():
    current_user = get_jwt_identity()
    if not current_user['id']:
        return error_response('404')
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
        return error_response('409')
    pasword_change = current_user['email']
    User = update_password(pasword_change)
    if not User:
        return error_response('404')
    if not bcrypt.check_password_hash(User.password, old_password):
        return error_response('400')
    hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
    User.password = hashed_password
    save_changes()
    return success_response('Password changed successfully', 200)


@blueprint.route('/forget', methods=['POST'])
def forget_password():
    data = request.json
    email = data.get('email')
    user = User.query.filter_by(email=email).first()
    if not user:
        return error_response('404')  
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
        reset_data = Rest_Token(user_id=user.id, token=token_encode,
                                expire_time=expire_time, User_Status=True)
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
        return error_response('401')
    user = User.query.filter_by(email=email).first()
    if not user:
        return error_response('402')
    auth_token = Rest_Token.query.filter_by(user_id=user.id).first()
    if not auth_token:
        return error_response('403')
    time = datetime.now()
    expire_time = auth_token.expire_time
    if time > expire_time:
        return error_response('404')
    if auth_token.token != token_encode:
        return error_response('405')
    hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
    User.password = hashed_password
    auth_token.User_Status = True
    save_changes()
    return success_response('Password reset successful', 200)
