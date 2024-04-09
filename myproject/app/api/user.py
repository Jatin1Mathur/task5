from sqlalchemy.exc import IntegrityError
from flask_ngrok import run_with_ngrok 
from flask import Flask, request, jsonify, Blueprint , Response
from flask_jwt_extended import JWTManager, create_access_token , jwt_required, get_jwt_identity

from app.models.model import db, user
from app.utlis import delete, save_changes, add, rollback 
from app import bcrypt
from app.services.user_services import user_filter,User_log , User_update , User_id , existing_users
from app.error_management.error_response import e_response , Response
from app.error_management.success_response import success_response
from app.validator.validators import check_user_required_fields
from config import basesit


blueprint=Blueprint('auth', __name__, url_prefix='/auth')
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
    return success_response( "User created successfully",200)  

@blueprint.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    User = User_log(email)
    if not User:
        return e_response('404')
    if bcrypt.check_password_hash(User.password, password):
        access_token = create_access_token(identity={'id': User.id, 'username': User.username , 'email' :User.email})
        return success_response({'access_token': access_token} , 200 )
    else:
        return e_response('401')
    
@blueprint.route('/retrieve', methods=['GET'])
@jwt_required()
def get_user_info():
    current_user = get_jwt_identity()
    if current_user['id']:
        user = User_id(current_user['id'])
        if user:
            return success_response({'email': user.email, 'username': user.username} , 200)
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
    existing_user = existing_users(new_username , user_id)
    if existing_user:
        return e_response('409')
    User.email = data.get('email', User.email)
    User.username = new_username
    try:
        save_changes()
        return success_response({'message': 'User updated successfully'} , 200)
    except IntegrityError:
        rollback()
        return e_response('409')


@blueprint.route("/delete", methods=['DELETE'])
@jwt_required()
def delete_user():
    current_user = get_jwt_identity()
    user_id = current_user.get('id')
    if not user_id:
        return e_response('404')
        delete(user_id)
    return success_response('User deleted successfully' , 201)

