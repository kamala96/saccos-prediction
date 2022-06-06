from . import db
from flask_login import UserMixin
from datetime import datetime


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    workouts = db.relationship('Workout', backref='author', lazy=True)


class Workout(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pushups = db.Column(db.Integer, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False,
                            default=datetime.utcnow)
    comment = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class Saccos(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(1000))
    date_created = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow)
    prediction_models = db.relationship(
        'PredictionModels', cascade="all,delete", backref='author', lazy=True)


class PredictionModels(db.Model):
    # __tablename__ = 'models'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(1000))
    performance_criteria = db.Column(db.String(1000))
    model_used = db.Column(db.String(1000))
    r2_score = db.Column(db.Float)
    mean_absolute_error = db.Column(db.Float)
    root_mean_squared_error = db.Column(db.Float)
    selected = db.Column(db.Boolean, default=False)
    date_created = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow)
    saccoss_id = db.Column(
        db.Integer, db.ForeignKey('saccos.id'), nullable=False)
