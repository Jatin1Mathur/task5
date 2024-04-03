from model import db, user , post

def add_user(email,username , hashed_password):
        new_user = user(email=email, username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return new_user

def new_post(title,content, author,tags):
        new_post = post(title=title, content=content, author=author, tags=tags)
        db.session.add(new_post)
        db.session.commit()
        

def add(obj):
    db.session.add(obj)
    db.session.commit()

def save_changes():
    db.session.commit()

def delete(obj):
    db.session.delete(obj)
    db.session.commit()
    
def rollback():
    db.session.rollback()