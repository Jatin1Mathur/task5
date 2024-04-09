from datetime import datetime 

from flask_migrate import Migrate
from flask_ngrok import run_with_ngrok 
from flask import Flask, request, jsonify, Blueprint
from flask_jwt_extended import get_jwt_identity, jwt_required , JWTManager, create_access_token

from app.models.model import db,  post, comment
from app.utlis import delete,  add
from app.models.model import db, user
from app.services.commant_services import target , comments , comment_delete
from app.error_management.error_response import e_response 
from app.error_management.success_response import success_response


blueprint = Blueprint('authe', __name__, url_prefix='/auth')
@blueprint.route('/posts/<int:post_id>/comments', methods=['POST'])
@jwt_required()
def create_comment(post_id):
    current_user = get_jwt_identity()
       
    content = request.json.get('content')
    if not content:
        return e_response('400')
    target_post = target(post_id)
    if not target_post:
        return e_response('404')
    new_comment = comment(
        user_id=current_user['id'],
        post_id=post_id,
        content=content,
        created_at=datetime.now()
    )
    add(new_comment)
    return success_response({'message': 'Comment added successfully'}, 201)


@blueprint.route('/posts/<int:post_id>/comments', methods=['GET'])
def get_comments(post_id):
    target_post = post.query.get(post_id)
    if not target_post:
        return e_response('404')
    comment_on_post = comments(post_id)
    comments_data = [{
        'id': c.id, 
        'content': c.content,
        'created_at': c.created_at 
        } for c in comment_on_post]
    return success_response(comments_data, 200)

@blueprint.route('/comments/<int:comment_id>', methods=['DELETE'])
@jwt_required()
def delete_comment(comment_id):
    current_user_id = get_jwt_identity()
    target_comment = comment_delete(comment_id)
    if not target_comment:
        return e_response('404')
    if target_comment.user_id != current_user_id['id']:
        return e_response('403')
    delete(target_comment)
    return success_response({'message': 'Comment deleted successfully'}, 200)
