# models.py
from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

# Sample user data
users = {
    'user1': User('1', 'user1', 'password1'),
    'user2': User('2', 'user2', 'password2')
}

def get_user_by_id(user_id):
    for user in users.values():
        if user.id == user_id:
            return user
    return None

def get_user_by_username(username):
    return users.get(username)
