from config import basesit
from sqlalchemy.exc import IntegrityError
from flask_ngrok import run_with_ngrok 
from flask import Flask, request, jsonify, Blueprint
from app.models.model import db, post, comment
from app.utlis import delete, save_changes, add, rollback 
from flask_jwt_extended import JWTManager, create_access_token
from flask_jwt_extended import jwt_required 
from app.services.post_services import post_re , post_by_id , user_posts
from app.error_management.error_response import e_response , Response
from app.error_management.success_response import success_response
from app.validator.validators import check_post_required_fields
 
bp= Blueprint('autho',__name__, url_prefix='/auth')
@bp.route("/create_blog", methods=['POST'])
@jwt_required()
def create_blog():
    data = request.json
    title = data.get('title')
    author = data.get('author')
    content = data.get('content')
    tags = data.get('tags')
    if not check_post_required_fields(data):
        return e_response('400')
    if post_re(title):
        return e_response('409')
    new_post = post(title=title, content=content, author=author, tags=tags)
    add(new_post)
    return success_response('Blog post created successfully' , 201)


@bp.route("/retrieve_posts/<int:id>", methods=['GET'])
def retrieve_posts(id=None):
    if id is not None:
        post_by_id(id)
        if post_by_id:
            return jsonify({'title': post_by_id.title,
                            'content': post_by_id.content,
                            'created_at': post_by_id.created_at,
                            'author': post_by_id.author,
                            'tags': post_by_id.tags})
        else:
            return e_response('404')
    else:
        user_id = request.args.get('user_id')
        if user_id:
            user_posts(user_id)
            if user_posts:
                posts_data = [{'title': p.title, 'content': p.content,
                               'created_at': p.created_at, 'author': p.author,
                               'tags': p.tags} for p in user_posts]
                return success_response(posts_data ,  200)
            else:
                return e_response('404')
        else:
            return e_response('400')


@bp.route("/delete_posts/<int:id>", methods=['DELETE'])
def delete_post(id):
    post_by_id(id)
    if not post_by_id:
        return e_response('404')
    comments_to_delete = comment.query.filter_by(post_id=id).all()
    for c in comments_to_delete:  
        db.session.delete(c)
    delete(post_by_id)
    return success_response( 'Post and associated comments deleted successfully' , 200
        )


@bp.route("/update_posts/<int:post_id>", methods=['PATCH'])
def update_post(post_id):
    post_by_id(id)
    if not post_by_id:
        return e_response('404')
    data = request.json
    post_by_id.title = data.get('title', post_by_id.title)
    post_by_id.content = data.get('content', post_by_id.content)
    post_by_id.tags = data.get('tags', post_by_id.tags)
    save_changes()
    return success_response( 'Post updated successfully' , 200)

