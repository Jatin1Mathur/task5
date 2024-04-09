from flask_migrate import Migrate
from config import basesit
from flask_ngrok import run_with_ngrok 
from flask import Flask, request, jsonify, Blueprint
from app.models.model import db, post, Like
from app.utlis import delete, save_changes, add
from flask_jwt_extended import JWTManager, create_access_token
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.like_services import like_filter , like_entry , likes , target_p
from app.error_management.error_response import e_response , Response
from app.error_management.success_response import success_response
from app.validator.validators import check_like_required_fields

bp =  Blueprint('like', __name__, url_prefix='/auth')
@bp.route("/like/<int:post_id>", methods=['POST'])
@jwt_required()
def like_post(post_id):
    data = request.json
    current_user_id = get_jwt_identity()
    user_by_id = current_user_id.get('id')
    if not check_like_required_fields(data):
         return e_response('400')
    if like_filter(post_id , user_by_id):
        return e_response('400')
    new_like = Like(post_id=post_id, status=True, user_id=current_user_id)
    add(new_like)
    return success_response('You have liked this post' , 201)


@bp.route("/unlike/<int:post_id>", methods=['POST'])
@jwt_required() 
def unlike_post(post_id):
    current_user_id = get_jwt_identity()['id']
    like_entry(post_id ,current_user_id )

    if not like_entry:   
        return e_response('400')

    delete(like_entry)
    return success_response( 'You have unliked this post',200)


@bp.route("/post/<int:post_id>/likes", methods=['GET'])
def get_post_likes(post_id):
    likes(post_id)
    likes_info = [{'user_id': like.user_id} for like in likes]
    return success_response( likes_info,200)

@bp.route("/view_post/<int:post_id>", methods=['GET'])
def view_post(post_id):
    target_p(post_id)
    if not target_p:
        return e_response('404')
    target_p.views += 1
    save_changes()
    return success_response({
        'message': 'Post viewed successfully',
        'views': target_p.views
    } , 200)
