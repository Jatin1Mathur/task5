from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db=SQLAlchemy()

class user(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100),  nullable=False)
    password = db.Column(db.String(100), nullable=False)
    
    
    
    def __init__(self, email, username,password):
            self.email = email
            self.username = username
            self.password = password
         

            
            
class post(db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    title = db.Column(db.String(100), unique=True, nullable=False)
    content = db.Column(db.String(6000), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    tags = db.Column(db.String(50), nullable=False)
    views = db.Column(db.Integer, default=0)
    
    def __init__(self, title, content, author, tags ):
        self.title = title
        self.content = content
        self.author = author
        self.tags = tags
       
       



        




class comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(3000), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, content, created_at, post_id, user_id):
        self.content = content
        self.created_at = created_at
        self.post_id = post_id
        self.user_id = user_id

        
        
       
      
class Follow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    following_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
def __init__(self,following_id , follower_id):
       
       self.following_id = following_id
       self.follower_id = follower_id

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))  
    status = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, post_id, status, user_id): 
        self.post_id = post_id
        self.status = status
        self.user_id = user_id


        

    