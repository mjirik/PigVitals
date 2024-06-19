import os
from pathlib import Path

# read file with secret key or generate one if it doesn't exist
if not os.path.exists('secret_key.txt'):
    with open('secret_key.txt', 'w') as f:
        f.write(os.urandom(16).hex())

with open('secret_key.txt', 'r') as f:
    SECRET_KEY = f.read()