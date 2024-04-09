from app.models.model import Follow , user


def follow_filter(user_id , current_user_id):
    return(Follow.query.filter_by(following_id=user_id, 
                              follower_id=current_user_id).first())
    
def follow_users(current_user_id):
    return(Follow.query.filter_by(follower_id=current_user_id).all())

def data(user_id):
    return(user.query.get(user_id))