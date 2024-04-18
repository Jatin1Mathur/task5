from app.models.model import User, Rest_Token, db


def user_filter(email):
    return (User.query.filter(User.email == email)).first()


def User_id(obj):
    return (User.query.get(obj))


def User_log(email):
    return (User.query.filter_by(email=email)).first()


def User_update(user_id):
    return (User.query.get(user_id))


def existing_users(new_username, user_id): 
    return (User.query.filter(
        User.username == new_username).filter(User.id != User_id).first())


def update_password(pasword_change):
    return (User.query.filter_by(email=pasword_change).first())


def user_filter_token(user_id, token_encode):
    return (Rest_Token.query.filter(db.and_(
        Rest_Token.user_id == user_id and
        Rest_Token.token == token_encode)).first())


def user_check(user_id):
    return (Rest_Token.query.filter_by(user_id=user_id).first())