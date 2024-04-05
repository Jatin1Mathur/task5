from datetime import datetime 
from flask_migrate import Migrate
from flask_ngrok import run_with_ngrok 
from flask import Flask, request, jsonify, Blueprint
from app.models.model import db,  post, comment
from app.utlis import delete,  add
from flask_jwt_extended import JWTManager, create_access_token
from app.models.model import db, user
from flask_jwt_extended import get_jwt_identity, jwt_required


bp = Blueprint('authe', __name__, url_prefix='/auth')
@bp.route('/posts/<int:post_id>/comments', methods=['POST'])
@jwt_required()
def create_comment(post_id):
    current_user_id = get_jwt_identity()
    user_by_id = current_user_id.get('id')   
    content = request.json.get('content')
    if not content:
        return jsonify({'error': 'Content is required'}), 400
    target_post = post.query.get(post_id)
    if not target_post:
        return jsonify({'error': 'Post not found'}), 404
    new_comment = comment(
        user_id=user_by_id,
        post_id=post_id,
        content=content,
        created_at=datetime.now()
    )
    add(new_comment)
    return jsonify({'message': 'Comment added successfully'}), 201


@bp.route('/posts/<int:post_id>/comments', methods=['GET'])
def get_comments(post_id):
    target_post = post.query.get(post_id)
    if not target_post:
        return jsonify({'error': 'Post not found'}), 404
    comments = comment.query.filter_by(post_id=post_id).all()
    comments_data = [{
        'id': c.id, 
        'content': c.content,
        'created_at': c.created_at 
        } for c in comments]
    return jsonify(comments_data), 200


@bp.route('/comments/<int:comment_id>', methods=['DELETE'])
@jwt_required()
def delete_comment(comment_id):
    current_user_id = get_jwt_identity()['id']
    target_comment = comment.query.get(comment_id)
    if not target_comment:
        return jsonify({'error': 'Comment not found'}), 404
    if target_comment.user_id != current_user_id:
        return jsonify({'error': 'Unauthorized to delete this comment'}), 403
    delete(target_comment)
    return jsonify({'message': 'Comment deleted successfully'}), 200
