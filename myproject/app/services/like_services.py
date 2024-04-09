from app.models.model import Like , post

def like_filter(post_id , user_by_id):
    return(Like.query.filter_by(post_id=post_id, user_id=user_by_id).first())

def like_entry(post_id ,current_user_id ):
    return(Like.query.filter_by(
        post_id=post_id,
        user_id=current_user_id).first())
    
def likes(post_id):
    return(Like.query.filter_by(post_id=post_id).all())

def target_p(post_id):
    return(post.query.get(post_id))