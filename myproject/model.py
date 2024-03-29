from flask_sqlalchemy import SQLAlchemy


db=SQLAlchemy()

class user(db.Model):
    __tablename__ = 'user'

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100),  nullable=False)
    password = db.Column(db.String(100), nullable=False)
    
    
    
    def __init__(self, email, username,password):
            self.email = email
            self.username = username
            self.password = password
         

            
            
class post(db.Model):
    __tablename__ = 'post'
    post_id = db.Column(db.Integer , primary_key = True)
    id = db.Column(db.Integer, db.ForeignKey("user.user_id"))
    title = db.Column(db.String(100), unique=True , nullable = False)
    content = db.Column(db.String(6000), nullable = False)
    author = db.Column(db.String(100), nullable = False)
    creation_date = db.Column(db.DateTime , nullable = False )
    tags = db.Column(db.String(50) , nullable = False )
    
    
    
    def __init__(self ,title , content , author , creation_date, tags ,blog_id,id):
        self.author = author
        self.content = content
        self.title = title
        self.creation_date = creation_date
        self.tags = tags
        self.blog_id = blog_id
        self.id = id



class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(3000), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    Comment_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)


    def __init__(self , id , body , timestamp , comment_id):
        self.id = id 
        self.body = body
        self.timestamp = timestamp
        self.Comment_id = comment_id
       
class follow(db.Model):
    follow_id = db.Column(nullable = False , primary_key = True )
    following = db.Column( db.ForeignKey('user.user_id') ,nullable = False )  
    follower = db.Column( db.ForeignKey('user.user_id') , nullable = False,)
    
    def __init__(self,id,following , follower):
        self.id = id
        self.following = following
        self.follower = follower

class like(db.Model):
    like_id = db.Column( primary_key = True , nullable = False)
    like = db.Column(db.ForeignKey('post.id'), nullable = False   )
    unlike = db.Column( db.ForeignKey('post.id'), nullable = False ,  nullable= False )
    
    def __init__(self , like_id , like , unlike):
        self.like_id = like_id
        self.like = like
        self.unlike = unlike
        

    