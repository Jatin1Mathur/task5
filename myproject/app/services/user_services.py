from app.models.model import user,Rest_Token , db


def user_filter(email):
    return(user.query.filter(user.email == email)).first()


def User_id(obj):
    return (user.query.get(obj))


def User_log(email):
    return (user.query.filter_by(email=email)).first()


def User_update(user_id):
    return (user.query.get(user_id))


def existing_users(new_username, user_id): 
    return (user.query.filter(user.username == new_username).filter(user.id != user_id).first())


def update_password(pasword_change):
    return(user.query.filter_by(email=pasword_change).first())


def user_filter_token(user_id, token_encode):
    return (Rest_Token.query.filter(db.and_(Rest_Token.user_id == user_id and Rest_Token.token == token_encode)).first())

def user_check(user_id):
    return(Rest_Token.query.filter_by(user_id=user_id).first())