from config import basesit
from sqlalchemy.exc import IntegrityError
from flask_ngrok import run_with_ngrok 
from flask import Flask, request, jsonify, Blueprint
from app.models.model import db, user
from app.utlis import  delete, save_changes, add, rollback 
from flask_jwt_extended import JWTManager, create_access_token, jwt_required ,get_jwt_identity
from app import bcrypt
bluep= Blueprint('auth',__name__,url_prefix='/auth')

@bluep.route("/register", methods=['POST'])
def register_user():
    data = request.json
    email = data.get('email')
    username = data.get('username')
    password = data.get('password')
    if not all([email, username, password]):
        return jsonify({'error': 'All fields need to be provided'}), 400
    if user.query.filter_by(email=email).first() or user.query.filter_by(username=username).first():
        return jsonify({'error': 'User with this email or username already exists'}), 409
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = user(email=email, username=username, password=hashed_password)
    add(new_user)
    return jsonify({'message': 'User created successfully'}), 201


@bluep.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    User = user.query.filter_by(email=email).first()
    if not User:
        return jsonify({'message': 'User not found'}), 404
    if bcrypt.check_password_hash(User.password, password):
        access_token = create_access_token(identity={ 'id': User.id , 'username' : User.username })
        return jsonify({'access_token': access_token}), 200
    else:
        return jsonify({'message': 'Invalid credentials'}), 401


@bluep.route('/retrieve', methods=['GET'])
@jwt_required()
def get_user_info():
    current_user = get_jwt_identity()
    #user_id = current_user.get('id')
    print(current_user['id'], "kjgjhghjg")
    
    if current_user['id']:
        User = user.query.get(current_user['id'])
        if User:
            return jsonify({'email': User.email, 'username': User.username})
    return jsonify({'message': 'User not found'}), 404
  
@bluep.route('/update', methods=['PUT'])
def update_user():
    data = request.json
    user_id = data.get('id')
    if not user_id:
        return jsonify({'error': 'User ID is missing in the request body'}), 400
    User = user.query.get(user_id)
    if not User:
        return jsonify({'error': 'User not found'}), 404
    new_username = data.get('username', User.username)
    existing_user = user.query.filter(user.username == new_username).filter(user.id != user_id).first()
    if existing_user:
        return jsonify({'error': 'Username already exists'}), 409
    User.email = data.get('email', User.email)
    User.username = new_username
    try:
        save_changes()
        return jsonify({'message': 'User updated successfully'})
    except IntegrityError:
        rollback()
        return jsonify({'error': 'Username already exists'}), 409


@bluep.route("/delete", methods=['DELETE'])
@jwt_required()
def delete_user():
    current_user = get_jwt_identity()
    user_id = current_user.get('id')
    if not user_id:
        return jsonify({'error': 'User not found'}), 404
        delete(user_id)
    return jsonify({'message': 'User deleted successfully'})

