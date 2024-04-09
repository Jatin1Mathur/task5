from app.models.model import user 


def user_filter(username,email):
    return(user.query.filter(user.db.and_(user.username  == username,  user.email == email)).first())

def User_id(obj):
    return (user.query.get(obj))

def User_log(email):
    return (user.query.filter_by(email=email).first())

def User_update(user_id):
    return (user.query.get(user_id))

def existing_user(new_username , user_id): 
    return (user.query.filter(user.username == new_username).filter(user.id != user_id).first())

