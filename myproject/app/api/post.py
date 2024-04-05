
from config import basesit
from sqlalchemy.exc import IntegrityError
from flask_ngrok import run_with_ngrok 
from flask import Flask, request, jsonify, Blueprint
from app.models.model import db, post, comment
from app.utlis import  delete, save_changes, add, rollback 
from flask_jwt_extended import JWTManager, create_access_token, jwt_required 

 
bluep= Blueprint('autho',__name__,url_prefix='/auth')

@bluep.route("/create_blog", methods=['POST'])
@jwt_required()
def create_blog():
    data = request.json
    title = data.get('title')
    author = data.get('author')
    content = data.get('content')
    tags = data.get('tags')
    if not all([title, author, content, tags]):
        return jsonify({'error': 'All fields need to be provided'}), 400
    if post.query.filter_by(title=title).first():
        return jsonify({'error': 'A post with this title already exists'}), 409
    new_post = post(title=title, content=content, author=author, tags=tags)
    add(new_post)
    return jsonify({'message': 'Blog post created successfully'}), 201


@bluep.route("/retrieve_posts/<int:id>", methods=['GET'])
def retrieve_posts(id=None):
    if id is not None:
        post_by_id = post.query.get(id)
        if post_by_id:
            return jsonify({'title': post_by_id.title, 'content': post_by_id.content,
                            'created_at': post_by_id.created_at, 'author': post_by_id.author,
                            'tags': post_by_id.tags})
        else:
            return jsonify({'message': 'Post not found'}), 404
    else:
        user_id = request.args.get('user_id')
        if user_id:
            user_posts = post.query.filter_by(user_id=user_id).all()
            if user_posts:
                posts_data = [{'title': p.title, 'content': p.content,
                               'created_at': p.created_at, 'author': p.author,
                               'tags': p.tags} for p in user_posts]
                return jsonify(posts_data), 200
            else:
                return jsonify({'message': 'No posts found for the specified user'}), 404
        else:
            return jsonify({'error': 'User ID not provided in the query parameters'}), 400


@bluep.route("/delete_posts/<int:id>", methods=['DELETE'])
def delete_post(id):
    post_to_delete = post.query.get(id)
    if not post_to_delete:
        return jsonify({'error': 'Post not found'}), 404
    comments_to_delete = comment.query.filter_by(post_id=id).all()
    for c in comments_to_delete:  
        db.session.delete(c)
    delete(post_to_delete)
    return jsonify({'message': 'Post and associated comments deleted successfully'}), 200


@bluep.route("/update_posts/<int:post_id>", methods=['PATCH'])
def update_post(post_id):
    Post = post.query.get(post_id)
    if not Post:
        return jsonify({'error': 'Post not found'}), 404
    data = request.json
    Post.title = data.get('title', Post.title)
    Post.content = data.get('content', Post.content)
    Post.tags = data.get('tags', Post.tags)
    save_changes()
    return jsonify({'message': 'Post updated successfully'}), 200

