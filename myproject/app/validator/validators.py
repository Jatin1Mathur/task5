def check_user_required_fields(data):
        required_fields = ["email", "password" , "username"]
        for field in required_fields:
            if field not in data:
                return False
        return True


def check_post_required_fields(data):
        required_fields = ["title", "content", "author", "tags" , "views"]
        for field in required_fields:
            if field not in data:
                return False
        return True


def check_command_required_fields(data):
        required_fields = ["content"]
        for field in required_fields:
            if field not in data:
                return False
        return True
    
    
def check_like_required_fields(data):
        required_fields = ["status"]
        for field in required_fields:
            if field not in data:
                return False
        return True