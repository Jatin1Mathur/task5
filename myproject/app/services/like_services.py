from app.models.model import Like, Posts


def like_filter(post_id, user_by_id):
    return (Like.query.filter_by(post_id=post_id, user_id=user_by_id).first())


def like_entry(post_id, current_user_id):
    return (Like.query.filter_by(
        post_id=post_id,
        user_id=current_user_id).first())


def get_likes(post_id):
    return (Like.query.filter_by(post_id=post_id).all())


def target_view(post_id):
    return (Posts.query.get(post_id))

