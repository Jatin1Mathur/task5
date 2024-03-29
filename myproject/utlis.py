from model import db, user
def add_user(email, username, password):
    new_user = user(email=email, username=username, 
                        password = password)
    db.session.add(new_user)
    db.session.commit()
    return new_user


def delete_user(user):
        db.session.delete(user)
        db.session.commit() 


def com_changes():
    db.session.commit()