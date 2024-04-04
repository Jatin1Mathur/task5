from datetime import datetime
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from config import basesit
from sqlalchemy.exc import IntegrityError
from flask_ngrok import run_with_ngrok 
from flask import Flask, request, jsonify, Blueprint
from app.models.model import db, user, post, comment, Follow, Like
from app.utlis import  delete, save_changes, add, rollback 
from flask_jwt_extended import JWTManager, create_access_token, jwt_required 
from flask_jwt_extended import get_jwt_identity
 

bluep = bluep = Blueprint('like', __name__ , url_prefix = '/auth')


@bluep.route("/like/<int:post_id>", methods=['POST'])
@jwt_required()
def like_post(post_id):
    current_user_id = get_jwt_identity()
    user_by_id = current_user_id.get('id')
    if Like.query.filter_by(post_id=post_id, user_id=user_by_id).first():
        return jsonify({'error': 'You have already liked this post'}), 400
    
    new_like = Like(post_id=post_id, status=True, user_id=current_user_id)
    add(new_like)
    return jsonify({'message': 'You have liked this post'}), 201


@bluep.route("/unlike/<int:post_id>", methods=['POST'])
@jwt_required() 
def unlike_post(post_id):
    current_user_id = get_jwt_identity()['id']
    like_entry = Like.query.filter_by(post_id=post_id, user_id=current_user_id).first()

    if not like_entry:   
        return jsonify({'error': 'You have not liked this post'}), 400

    delete(like_entry)
    return jsonify({'message': 'You have unliked this post'}), 200


@bluep.route("/post/<int:post_id>/likes", methods=['GET'])
def get_post_likes(post_id):
    likes = Like.query.filter_by(post_id=post_id).all()
    likes_info = [{'user_id': like.user_id} for like in likes]
    return jsonify(likes_info), 200


@bluep.route("/view_post/<int:post_id>", methods=['GET'])
def view_post(post_id):
    target_post = post.query.get(post_id)
    if not target_post:
        return jsonify({'error': 'Post not found'}), 404
    target_post.views += 1
    save_changes()
    return jsonify({'message': 'Post viewed successfully', 'views': target_post.views}), 200
