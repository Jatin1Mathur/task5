from flask import Flask, request, jsonify , blueprints 
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
from flask_migrate import Migrate
from model import  db , user, post , Comment , follow ,like




app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:jatin@localhost/user'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'


db.init_app(app)
jwt = JWTManager(app)
bcrypt = Bcrypt(app)
migrate = Migrate(app, db)

#User Management 
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
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User created successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    username = data.get('username')
    users = user.query.filter_by(email=email).first()
    if not users:
        return jsonify({'message': 'User not found'}), 404
    if bcrypt.check_password_hash(users.password, password):
        access_token = create_access_token(identity={'username': users.username, 'password': users.password , 'email' : users.email})
        return jsonify({'access_token': access_token}), 200
    else:
        return jsonify({'message': 'Invalid credentials'}), 401
    
@app.route('/retrieve/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    Users = user.query.get(user_id)
    if Users:
        return jsonify({'username': Users.username, 'email': Users.email})
    else:
        return jsonify({'message': 'User not found'})

@app.route("/update/<int:user_id>", methods=['PUT'])
@jwt_required()
def update_user(user_id):
    Users = user.query.get(user_id)
    if not Users:
        return jsonify({'error': 'User not found'})
    data = request.json
    Users.email = data.get('email', Users.email)
    Users.username = data.get('username', Users.username)
    db.session.commit()
    return jsonify({'message': 'User updated successfully'})

@app.route("/delete/<int:user_id>", methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    Users = user.query.get(user_id)
    if not Users:
        return jsonify({'error': 'User not found'})
    db.session.delete(Users)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'})

#Post Management
@app.route("/create_blog" , methods = ['POST'])
def create_blog():
    post_id = get_jwt_identity
    data = request.json
    title = data.get('title')
    author = data.get('author')
    content = data.get('content')
    creation_date = data.get('creation_date')
    tags = data.get('tags')
    if not all([title, author, creation_date, tags , content]):
        return jsonify({'error': 'All fields need to be provided'}), 400
    if post.query.filter_by(title=title).first() or post.query.filter_by(content=content).first():
        return jsonify({'error': 'User with this title or content already exists'}), 409
    new_post = post(title=title, content=content, author=author, tags=tags)
    db.session.add(new_post)
    db.session.commit()
    return jsonify({'message': 'blog created successfully'}), 201

@app.route("/retrieve_posts/<int:post_id>" , methods = ['GET'])
@app.route("/retrieve_blog" , methods = ['GET'])
@jwt_required
def get_user(post_id):
    Users = post.query.get(post_id)
    if Users:
        return jsonify({'title': Users.title, 'content': Users.content , 'creation_date' : Users.creation_date , 'author' : Users.author , 'tags' : Users.tags })
    else:
        return jsonify({'message': 'User not found'})





@app.route("/delete_posts/<int:post_id>", methods=['DELETE'])
@jwt_required()

def delete_post(post_id):
    post_id = get_jwt_identity
    Users = post.query.get(post_id)
    if not post:
        return jsonify({'error': 'Post not found'}), 404
    if post.author != get_jwt_identity():
        return jsonify({'error': 'Unauthorized to delete this post'}), 403
    db.session.delete(post)
    db.session.commit()
    return jsonify({'message': 'Post deleted successfully'})
    
    
@app.route("/update_posts/<int:post_id>", methods=['PUT'])
@jwt_required()
def update_post(post_id):
    post_id = get_jwt_identity
    Users = post.query.get(post_id)
    if not post:
        return jsonify({'error': 'Post not found'}), 404
    if post.author != get_jwt_identity():
        return jsonify({'error': 'Unauthorized to update this post'}), 403
    data = request.json
    post.title = data.get('title', post.title)       
    post.content = data.get('content', post.content)
    post.tags = data.get('tags', post.tags)
    db.session.commit()
    return jsonify({'message': 'Post updated successfully'})


#comment Management
@app.route("/posts/<int:post_id>/comments", methods=['POST'])
@jwt_required()
def create_comment(post_id):
    data = request.json
    content = data.get('content')
    author = get_jwt_identity() 
    new_comment = Comment(content=content, author=author, post_id=post_id)
    db.session.add(new_comment)
    db.session.commit()
    return jsonify({'message': 'Comment created successfully'}), 201

@app.route("/posts/<int:post_id>/comments", methods=['GET'])
def get_comments(post_id):
    comments = Comment.query.filter_by(post_id=post_id).all()
    result = []
    for comment in comments:
        result.append({
            'id': comment.id,
            'content': comment.content,
            'author': comment.author,
            'creation_date': comment.creation_date.strftime('%Y-%m-%d %H:%M:%S')
        })
    return jsonify(result)

@app.route("/posts/<int:post_id>/comments/<int:comment_id>", methods=['DELETE'])
@jwt_required()
def delete_comment(post_id, comment_id):
    comment = Comment.query.get(comment_id)
    if not comment:
        return jsonify({'error': 'Comment not found'}), 404
    if comment.author != get_jwt_identity():
        return jsonify({'error': 'Unauthorized to delete this comment'}), 403
    db.session.delete(comment)
    db.session.commit()
    return jsonify({'message': 'Comment deleted successfully'})





if __name__ == '__main__':
    app.run(debug=True)
    
