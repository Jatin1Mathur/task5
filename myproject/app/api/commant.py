from datetime import datetime 

from flask_migrate import Migrate
from flask_ngrok import run_with_ngrok 
from flask import Flask, request, jsonify, Blueprint
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_jwt_extended import JWTManager, create_access_token

from app.models.model import db,  post, comment
from app.utlis import delete,  add
from app.models.model import db, user
from app.services.commant_services import target , comments , comment_delete
from app.error_management.error_response import e_response 
from app.error_management.success_response import success_response


bp = Blueprint('authe', __name__, url_prefix='/auth')
@bp.route('/posts/<int:post_id>/comments', methods=['POST'])
@jwt_required()
def create_comment(post_id):
    current_user = get_jwt_identity()
    user_by_id = current_user.get('id')   
    content = request.json.get('content')
    if not content:
        return e_response('400')
    target_post = target(post_id)
    if not target_post:
        return e_response('404')
    new_comment = comment(
        user_id=user_by_id,
        post_id=post_id,
        content=content,
        created_at=datetime.now()
    )
    add(new_comment)
    return success_response({'message': 'Comment added successfully'}, 201)


@bp.route('/posts/<int:post_id>/comments', methods=['GET'])
def get_comments(post_id):
    target_post = post.query.get(post_id)
    if not target_post:
        return e_response('404')
    commant = comments(post_id)
    comments_data = [{
        'id': c.id, 
        'content': c.content,
        'created_at': c.created_at 
        } for c in commant]
    return success_response(comments_data, 200)

@bp.route('/comments/<int:comment_id>', methods=['DELETE'])
@jwt_required()
def delete_comment(comment_id):
    current_user_id = get_jwt_identity()['id']
    target_comment = comment_delete(comment_id)
    if not target_comment:
        return e_response('404')
    if target_comment.user_id != current_user_id:
        return e_response('403')
    delete(target_comment)
    return success_response({'message': 'Comment deleted successfully'}, 200)
