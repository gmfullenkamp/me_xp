from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# Mock database for demo (swap with real DB later)
users = {}

class User(UserMixin):
    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Helper to register a user
def register_user(username, password):
    if username in users:
        return None
    user = User(id=len(users)+1, username=username, password_hash=generate_password_hash(password))
    users[username] = user
    return user

# Helper to load user
def get_user(username):
    return users.get(username)
