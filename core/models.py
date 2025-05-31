from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import check_password_hash

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    specializations = db.relationship("Specialization", backref="user", lazy=True)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Specialization(db.Model):
    __tablename__ = 'specializations'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    xp = db.Column(db.Integer, default=0)
    level = db.Column(db.Integer, default=1)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    goals = db.relationship("GoalCompletion", backref="specialization", lazy=True)

class GoalCompletion(db.Model):
    __tablename__ = 'goal_completions'
    id = db.Column(db.Integer, primary_key=True)
    goal_name = db.Column(db.String(200), nullable=False)
    completed_date = db.Column(db.Date, default=datetime.utcnow)
    specialization_id = db.Column(db.Integer, db.ForeignKey('specializations.id'), nullable=False)
