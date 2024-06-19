# models.py
from flask_login import UserMixin
from settings import users_raw
import os
import json

class User(UserMixin):
    def __init__(self, id, username, password, role='user'):
        self.id = id
        self.username = username
        self.password = password
        self.role = role

    def set_password(self, new_password):
        self.password = new_password

# Sample user data
users = {username: User(**data) for username, data in users_raw.items()}

def get_user_by_id(user_id):
    for user in users.values():
        if user.id == user_id:
            return user
    return None

def get_user_by_username(username):
    return users.get(username)

def add_user(username, password, role='user'):
    new_id = str(len(users) + 1)
    new_user = User(new_id, username, password, role)
    users[username] = new_user
    return new_user