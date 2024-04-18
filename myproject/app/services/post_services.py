from app.models.model import Posts


def post_re(title):
    return (Posts.query.filter_by(title=title).first())


def post_by_id(obj):
    return (Posts.query.get(obj))


def user_posts(user_id):
    return (Posts.query.filter_by(user_id=user_id).all())
 

def user_update(post_id):
    return Posts.query.get(post_id)

