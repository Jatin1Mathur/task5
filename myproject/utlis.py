from model import db, user, post


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