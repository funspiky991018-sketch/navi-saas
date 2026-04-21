from models.user import User

# In-memory "database"
users_db = []

def create_user(user: User):
    users_db.append(user)
    return user

def get_user_by_email(email: str):
    for user in users_db:
        if user.email == email:
            return user
    return None
