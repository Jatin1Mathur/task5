from config import basesit
from sqlalchemy.exc import IntegrityError
from flask_ngrok import run_with_ngrok 
from flask import Flask, request, jsonify, Blueprint , Response
from app.models.model import db, user
from app.utlis import delete, save_changes, add, rollback 
from flask_jwt_extended import JWTManager, create_access_token
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import bcrypt
from app.services.user_services import user_filter,User_log , User_update , User_id , existing_user
from app.error_management.error_response import e_response , Response
from app.error_management.success_response import success_response
from app.validator.validators import check_user_required_fields

bp=Blueprint('auth', __name__, url_prefix='/auth')
@bp.route("/register", methods=['POST'])
def register_user():
    data = request.json
    email = data.get('email')
    username = data.get('username')
    password = data.get('password')
    if  not check_user_required_fields(data):
        return e_response('400')
    if existing_user(username, email):  
        return  e_response('409')
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = user(email=email, username=username, password=hashed_password)  
    add(new_user)
    return success_response( 'User created successfully' , 201)  

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    User = user.query.filter_by(email=email).first()
    if not User:
        return e_response('404')
    if bcrypt.check_password_hash(User.password, password):
        access_token = create_access_token(identity={'id': User.id, 'username': User.username})
        return success_response({'access_token': access_token} , 200 )
    else:
        return e_response('401')


@bp.route('/retrieve', methods=['GET'])
@jwt_required()
def get_user_info():
    current_user = get_jwt_identity()
    if current_user['id']:
        User_id(current_user['id'])
        if User_id:
            return success_response({'email': User_id.email, 'username': User_id.username} , 200)
    return e_response('404')


@bp.route('/update', methods=['PUT'])
def update_user():
    data = request.json
    user_id = data.get('id')
    if not user_id:
        return e_response('400')
    User_update(user_id)
    if not User_update:
        return e_response('404')
    new_username = data.get('username', User_update.username)
    existing_user(new_username , user_id)
    if existing_user:
        return e_response('409')
    User_update.email = data.get('email', User_update.email)
    User_update.username = new_username
    try:
        save_changes()
        return success_response( 'User updated successfully' , 201 )
    except IntegrityError:
        rollback()
        return e_response('409')


@bp.route("/delete", methods=['DELETE'])
@jwt_required()
def delete_user():
    current_user = get_jwt_identity()
    user_id = current_user.get('id')
    if not user_id:
        return e_response('404')
        delete(user_id)
    return success_response('User deleted successfully' , 201)

