from app.models.model import user,Rest_Token


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

