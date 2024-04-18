from config import basesit

from sqlalchemy.exc import IntegrityError
from flask_ngrok import run_with_ngrok 
from flask import Flask, request, jsonify, Blueprint
from flask_jwt_extended import JWTManager, create_access_token, jwt_required 

from app.models.model import db, Posts, Comment
from app.utlis import delete, save_changes, add, rollback 
from app.services.post_services import post_re, post_by_id, user_posts, user_update
from app.error_management.error_response import error_response, Response
from app.error_management.success_response import success_response
from app.validator.validators import check_post_required_fields

 
blueprint = Blueprint('authen', __name__, url_prefix='/auth')


@blueprint.route("/create_blog", methods=['POST'])
@jwt_required()
def create_blog():
    data = request.json
    title = data.get('title')
    author = data.get('author')
    content = data.get('content')
    tags = data.get('tags')
    if not check_post_required_fields(data):
        return error_response('400')
    if post_re(title):
        return error_response('409')
    new_post = Posts(title=title, content=content, author=author, tags=tags)
    add(new_post)
    return success_response({'message': 'Blog post created successfully'}, 201)


@blueprint.route("/retrieve_posts/<int:id>", methods=['GET'])
def retrieve_posts(id=None):
    if id is not None:
        Post_retrieve = post_by_id(id)
        if Post_retrieve:
            return jsonify({'title': Post_retrieve.title,
                            'content': Post_retrieve.content,
                            'created_at': Post_retrieve.created_at,
                            'author': Post_retrieve.author,
                            'tags': Post_retrieve.tags})
        else:
            return error_response('404')
    else:
        user_id = request.args.get('user_id')
        if user_id:
            user_posts(user_id)
            if user_posts:
                posts_data = [{'title': p.title, 'content': p.content,
                               'created_at': p.created_at, 'author': p.author,
                               'tags': p.tags} for p in user_posts]
                return success_response(posts_data,  200)
            else:
                return error_response('404')
        else:
            return error_response('400')


@blueprint.route("/delete_posts/<int:id>", methods=['DELETE'])
def delete_post(id):
    Post = post_by_id(id)
    if not Post:
        return error_response('404')
    comments_to_delete = Comment.query.filter_by(post_id=id).all()
    for c in comments_to_delete:  
        db.session.delete(c)
    delete(Post)
    return success_response(
        'Post and associated comments deleted successfully', 200)


@blueprint.route("/update_posts/<int:post_id>", methods=['PATCH'])
def update_post(post_id):
    Post = user_update(post_id)
    if not Post:
        return error_response('404')
    data = request.json
    Post.title = data.get('title', Post.title)
    Post.content = data.get('content', Post.content)
    Post.tags = data.get('tags', Post.tags)
    save_changes()
    return success_response({'message': 'Post updated successfully'}, 200)


