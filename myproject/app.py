from datetime import datetime
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from config import basesit
from sqlalchemy.exc import IntegrityError
from flask_ngrok import run_with_ngrok 
from flask import Flask, request, jsonify
from model import db, user, post, comment, Follow, Like
from utlis import  delete, save_changes, add, rollback 
from flask_jwt_extended import JWTManager, create_access_token, jwt_required 
from flask_jwt_extended import get_jwt_identity

app = Flask(__name__)
app.config.from_object(basesit)
db.init_app(app)
jwt = JWTManager(app)
bcrypt = Bcrypt(app)
migrate = Migrate(app, db)
date = datetime.now()
run_with_ngrok(app)

 
@app.route("/register", methods=['POST'])
def register_user():
    data = request.json
    email = data.get('email')
    username = data.get('username')
    password = data.get('password')
    if not all([email, username, password]):
        return jsonify({'error': 'All fields need to be provided'}), 400
    if user.query.filter_by(email=email).first() or user.query.filter_by(username=username).first():
        return jsonify({'error': 'User with this email or username already exists'}), 409
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = user(email=email, username=username, password=hashed_password)
    add(new_user)
    return jsonify({'message': 'User created successfully'}), 201


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    User = user.query.filter_by(email=email).first()
    if not User:
        return jsonify({'message': 'User not found'}), 404
    if bcrypt.check_password_hash(User.password, password):
        access_token = create_access_token(identity={ 'id': User.id , 'username' : User.username })
        return jsonify({'access_token': access_token}), 200
    else:
        return jsonify({'message': 'Invalid credentials'}), 401


@app.route('/retrieve', methods=['GET'])
@jwt_required()
def get_user_info():
    current_user = get_jwt_identity()
    user_id = current_user.get('id')
    if user_id:
        User = user.query.get(user_id)
        if User:
            return jsonify({'email': User.email, 'username': User.username})
    return jsonify({'message': 'User not found'}), 404
  

def update_user():
    data = request.json
    user_id = data.get('id')
    if not user_id:
        return jsonify({'error': 'User ID is missing in the request body'}), 400
    User = user.query.get(user_id)
    if not User:
        return jsonify({'error': 'User not found'}), 404
    new_username = data.get('username', User.username)
    existing_user = user.query.filter(user.username == new_username).filter(user.id != user_id).first()
    if existing_user:
        return jsonify({'error': 'Username already exists'}), 409
    User.email = data.get('email', User.email)
    User.username = new_username
    try:
        save_changes()
        return jsonify({'message': 'User updated successfully'})
    except IntegrityError:
        rollback()
        return jsonify({'error': 'Username already exists'}), 409


@app.route("/delete", methods=['DELETE'])
@jwt_required()
def delete_user():
    current_user = get_jwt_identity()
    user_id = current_user.get('id')
    if not user_id:
        return jsonify({'error': 'User not found'}), 404
        delete(user_id)
    return jsonify({'message': 'User deleted successfully'})


# Post Management


@app.route("/create_blog", methods=['POST'])
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


@app.route("/retrieve_posts/<int:id>", methods=['GET'])
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


@app.route("/delete_posts/<int:id>", methods=['DELETE'])
def delete_post(id):
    post_to_delete = post.query.get(id)
    if not post_to_delete:
        return jsonify({'error': 'Post not found'}), 404
    comments_to_delete = comment.query.filter_by(post_id=id).all()
    for c in comments_to_delete:  
        db.session.delete(c)
    delete(post_to_delete)
    return jsonify({'message': 'Post and associated comments deleted successfully'}), 200


@app.route("/update_posts/<int:post_id>", methods=['PATCH'])
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


# Comment Management
@app.route('/posts/<int:post_id>/comments', methods=['POST'])
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


@app.route('/posts/<int:post_id>/comments', methods=['GET'])
def get_comments(post_id):
    target_post = post.query.get(post_id)
    if not target_post:
        return jsonify({'error': 'Post not found'}), 404
    comments = comment.query.filter_by(post_id=post_id).all()
    comments_data = [{'id': c.id, 'content': c.content, 'created_at': c.created_at} for c in comments]
    return jsonify(comments_data), 200


@app.route('/comments/<int:comment_id>', methods=['DELETE'])
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

# Following and Followers Management


@app.route("/follow/<int:user_id>", methods=['POST'])
@jwt_required()
def follow_user(user_id):
    current_user_id = get_jwt_identity()['id']

    if current_user_id == user_id:
        return jsonify({'error': 'You cannot follow yourself'}), 400

    if Follow.query.filter_by(following_id=user_id, follower_id=current_user_id).first():
        return jsonify({'error': 'You are already following this user'}), 400

    new_follow = Follow(following_id=user_id, follower_id=current_user_id)
    add(new_follow)
    return jsonify({'message': 'You are now following this user'}), 201

# Unfollow a user


@app.route("/unfollow/<int:user_id>", methods=['POST'])
@jwt_required()
def unfollow_user(user_id):
    current_user_id = get_jwt_identity()['id']
    follow_entry = Follow.query.filter_by(following_id=user_id, follower_id=current_user_id).first()

    if not follow_entry:
        return jsonify({'error': 'You are not following this user'}), 400

    delete(follow_entry)
    return jsonify({'message': 'You have unfollowed this user'}), 200


# Retrieve followed users and followers
@app.route("/followed_users", methods=['GET'])
@jwt_required()
def get_followed_users():
    current_user_id = get_jwt_identity()['id']
    followed_users = Follow.query.filter_by(follower_id=current_user_id).all()
    followed_users_ids = [follow.following_id for follow in followed_users]
    followed_users_data = [user.query.get(user_id) for user_id in followed_users_ids]
    followed_users_info = [{'id': user.id, 'username': user.username} for user in followed_users_data]

    return jsonify(followed_users_info), 200


@app.route("/followers", methods=['GET'])
@jwt_required()
def get_followers():
    current_user_id = get_jwt_identity()['id']
    followers = Follow.query.filter_by(following_id=current_user_id).all()
    followers_ids = [follow.follower for follow in followers]
    followers_data = [user.query.get(user_id) for user_id in followers_ids]
    followers_info = [{'id': user.id, 'username': user.username} for user in followers_data]
    return jsonify(followers_info), 200

# Like Management


@app.route("/like/<int:post_id>", methods=['POST'])
@jwt_required()
def like_post(post_id):
    current_user_id = get_jwt_identity()['id']
    if Like.query.filter_by(post_id=post_id, user_id=current_user_id).first():
        return jsonify({'error': 'You have already liked this post'})
    new_like = Like(post_id=post_id, status=True, user_id=current_user_id)
    add(new_like)
    return jsonify({'message': 'You have liked this post'}), 201


@app.route("/unlike/<int:post_id>", methods=['POST'])
@jwt_required()
def unlike_post(post_id):
    current_user_id = get_jwt_identity()['id']
    like_entry = Like.query.filter_by(post_id=post_id, user_id=current_user_id).first()

    if not like_entry:   
        return jsonify({'error': 'You have not liked this post'}), 400

    delete(like_entry)
    return jsonify({'message': 'You have unliked this post'}), 200


@app.route("/post/<int:post_id>/likes", methods=['GET'])
def get_post_likes(post_id):
    likes = Like.query.filter_by(post_id=post_id).all()
    likes_info = [{'user_id': like.user_id} for like in likes]
    return jsonify(likes_info), 200


@app.route("/view_post/<int:post_id>", methods=['GET'])
def view_post(post_id):
    target_post = post.query.get(post_id)
    if not target_post:
        return jsonify({'error': 'Post not found'}), 404
    target_post.views += 1
    save_changes()
    return jsonify({'message': 'Post viewed successfully', 'views': target_post.views}), 200


if __name__ == '__main__':
    app.run()