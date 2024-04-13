from flask_migrate import Migrate
from flask_ngrok import run_with_ngrok 
from flask import Flask, request, jsonify, Blueprint
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

from app.models.model import db, post, Like
from app.utlis import delete, save_changes, add
from app.services.like_services import like_filter, like_entry, get_likes, target_view
from app.error_management.error_response import e_response, Response
from app.error_management.success_response import success_response
from config import basesit


blueprint = Blueprint('like', __name__, url_prefix='/auth')
@blueprint.route("/like/<int:post_id>", methods=['POST'])
@jwt_required()
def like_post(post_id):
    current_user_id = get_jwt_identity()
    user_by_id = current_user_id.get('id')
    like_create = like_filter(post_id, user_by_id)
    if like_create:
        return e_response('400')
    new_like = Like(post_id=post_id, status=True, user_id=current_user_id["id"])
    add(new_like)
    return success_response('You have liked this post' , 201)


@blueprint.route("/unlike/<int:post_id>", methods=['POST'])
@jwt_required() 
def unlike_post(post_id):
    current_user_id = get_jwt_identity()['id']
    unlike = like_entry(post_id, current_user_id)

    if not unlike:   
        return e_response('400')

    delete(unlike)
    return success_response( 'You have unliked this post',200)


@blueprint.route("/post/<int:post_id>/likes", methods=['GET'])
def get_post_likes(post_id):
    likes = get_likes(post_id)
    likes_info = [{'user_id': like.user_id} for like in likes]
    return success_response(likes_info, 200)

@blueprint.route("/view_post/<int:post_id>", methods=['GET'])
def view_post(post_id):
    view = target_view(post_id)
    if not view:
        return e_response('404')
    view.views += 1
    save_changes()
    return success_response({
        'message': 'Post viewed successfully',
        'views': view.views
    }, 200)
