from flask_ngrok import run_with_ngrok 
from flask import Flask, request, jsonify, Blueprint
from app.models.model import db, user, Follow
from app.utlis import delete, add 
from flask_jwt_extended import JWTManager, create_access_token
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_migrate import Migrate


bp = Blueprint('authee', __name__, url_prefix='/auth')
@bp.route("/follow/<int:user_id>", methods=['POST'])
@jwt_required()
def follow_user(user_id):
    current_user_id = get_jwt_identity()['id']
    if current_user_id == user_id:
        return jsonify({'error': 'You cannot follow yourself'}), 400
    if Follow.query.filter_by(following_id=user_id, 
                              follower_id=current_user_id).first():
        return jsonify({'error': 'You are already following this user'}), 400
    new_follow = Follow(following_id=user_id, follower_id=current_user_id)
    add(new_follow)
    return jsonify({'message': 'You are now following this user'}), 201


# Unfollow a user
@bp.route("/unfollow/<int:user_id>", methods=['POST'])
@jwt_required()
def unfollow_user(user_id):
    current_user_id = get_jwt_identity()['id']
    follow_entry = Follow.query.filter_by(following_id=user_id,
                                          follower_id=current_user_id).first()

    if not follow_entry:
        return jsonify({'error': 'You are not following this user'}), 400

    delete(follow_entry)
    return jsonify({'message': 'You have unfollowed this user'}), 200


# Retrieve followed users and followers
@bp.route("/followed_users", methods=['GET'])
@jwt_required()
def get_followed_users():
    current_user_id = get_jwt_identity()['id']
    followed_users = Follow.query.filter_by(follower_id=current_user_id).all()
    followed_users_ids = [follow.following_id for follow in followed_users]
    followed_users_data = [user.query.get(user_id) for user_id in followed_users_ids]
    followed_users_info = [{
        'id': user.id, 
        'username': user.username} for user in followed_users_data]
    return jsonify(followed_users_info), 200


@bp.route("/followers", methods=['GET'])
@jwt_required()
def get_followers():
    current_user_id = get_jwt_identity()['id']
    followers = Follow.query.filter_by(following_id=current_user_id).all()
    followers_ids = [follow.follower for follow in followers]
    followers_data = [user.query.get(user_id) for user_id in followers_ids]
    followers_info = [{'id': user.id,'username': user.username} for user in followers_data]
    return jsonify(followers_info), 200
