from werkzeug.security import generate_password_hash

from core.models import User, db


def register_user(username, password):
    if User.query.filter_by(username=username).first():
        return None
    new_user = User(username=username, password_hash=generate_password_hash(password))
    db.session.add(new_user)
    db.session.commit()
    return new_user


def get_user(username):
    return User.query.filter_by(username=username).first()
