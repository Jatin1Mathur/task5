from app.models.model import Comment, Posts


def target(obj):    
    return (Posts.query.get(obj))


def comments(post_id):
    return (Comment.query.filter_by(post_id=post_id).all())


def comment_delete(comment_id):
    return (Comment.query.get(comment_id))