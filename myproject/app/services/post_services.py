from app.models.model import post

def post_re(title):
    return(post.query.filter_by(title=title).first())

def post_by_id(obj):
    return (post.query.get(obj))

def user_posts(user_id):
    return (post.query.filter_by(user_id=user_id).all())

def user_update(post_id):
    return post.query.get(post_id)

