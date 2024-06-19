import os
from pathlib import Path
import json

# read file with secret key or generate one if it doesn't exist
if not os.path.exists('secret_key.txt'):
    with open('secret_key.txt', 'w') as f:
        f.write(os.urandom(16).hex())

with open('secret_key.txt', 'r') as f:
    SECRET_KEY = f.read()

# read users from json file or create one if it doesn't exist
if not os.path.exists('users.json'):
    with open('users.json', 'w') as f:
        f.write('{"admin": {"id": "1", "username": "user1", "password": "password1", "role": "admin"}, '
                '"user2": {"id": "2", "username": "user2", "password": "password2", "role": "user"}}')
with open('users.json', 'r') as f:
    users_raw = json.load(f)
