from app.models.model import comment , post

def target(obj):
    return(post.query.get(obj))

def comments(post_id):
    return(comment.query.filter_by(post_id=post_id).all())

def comment_delete(comment_id):
    return(comment.query.get(comment_id))