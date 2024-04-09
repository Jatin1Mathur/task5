def check_user_required_fields(data):
        required_fields = ["email", "password" , "username"]
        for field in required_fields:
            if field not in data:
                return False
        return True


def check_post_required_fields(data):
        required_fields = ["title", "content", "author", "tags" ]
        for field in required_fields:
            if field not in data:
                return False
        return True



    
    
