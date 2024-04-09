from flask_ngrok import run_with_ngrok 
from flask import Flask, request, jsonify, Blueprint
from app.models.model import db, user, Follow
from app.utlis import delete, add 
from flask_jwt_extended import JWTManager, create_access_token
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_migrate import Migrate
from app.services.follow_services import follow_filter , follow_users , data
from app.error_management.error_response import e_response , Response
from app.error_management.success_response import success_response

bp = Blueprint('authee', __name__, url_prefix='/auth')
@bp.route("/follow/<int:user_id>", methods=['POST'])
@jwt_required()
def follow_user(user_id):
    current_user_id = get_jwt_identity()['id']
    if current_user_id == user_id:
        return e_response('400')
    if follow_filter(user_id , current_user_id):
        return e_response('400')
    new_follow = Follow(following_id=user_id, follower_id=current_user_id)
    add(new_follow)
    return success_response( 'You are now following this user' , 201)


# Unfollow a user
@bp.route("/unfollow/<int:user_id>", methods=['POST'])
@jwt_required()
def unfollow_user(user_id):
    current_user_id = get_jwt_identity()['id']
    follow_filter(user_id , current_user_id)

    if not follow_filter:
        return e_response('400')

    delete(follow_filter)
    return success_response( 'You have unfollowed this user' , 200)


# Retrieve followed users and followers
@bp.route("/followed_users", methods=['GET'])
@jwt_required()
def get_followed_users():
    current_user_id = get_jwt_identity()['id']
    follow_users(current_user_id)
    followed_users_ids = [follow.following_id for follow in follow_users]
    followed_users_data = [data(user_id) for user_id in followed_users_ids]
    followed_users_info = [{
        'id': user.id, 
        'username': user.username} for user in followed_users_data]
    return success_response(followed_users_info , 200)

@bp.route("/followers", methods=['GET'])
@jwt_required()
def get_followers():
    current_user_id = get_jwt_identity()['id']
    follow_users(current_user_id)
    followers_ids = [follow.follower for follow in follow_users]
    followers_data = [data(user_id) for user_id in followers_ids]
    followers_info = [{'id': user.id,'username': user.username} for user in followers_data]
    return success_response(followers_info , 200)