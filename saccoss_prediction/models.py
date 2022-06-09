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
    evaluations = db.relationship(
        'Evaluations', cascade="all,delete", backref='author', lazy=True)
    actual_and_predicted = db.relationship(
        'ActualAndPredicted', cascade="all,delete", backref='author', lazy=True)


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


class ActualAndPredicted(db.Model):
    act_id = db.Column(db.Integer, primary_key=True)
    month = db.Column(db.Date)
    prediction_model = db.Column(db.String(1000))
    performance_criteria = db.Column(db.String(1000))
    actual = db.Column(db.Float)
    predicted = db.Column(db.Float)
    date_created = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow)
    saccoss_id = db.Column(
        db.Integer, db.ForeignKey('saccos.id'), nullable=False)


class Evaluations(db.Model):
    ev_id = db.Column(db.Integer, primary_key=True)
    month = db.Column(db.Date)
    cc = db.Column(db.Float)
    ta = db.Column(db.Float)
    npl = db.Column(db.Float)
    glp_tl = db.Column(db.Float)
    nea = db.Column(db.Float)
    gllr = db.Column(db.Float)
    gl = db.Column(db.Float)
    wo = db.Column(db.Float)
    rcv = db.Column(db.Float)
    capital_adequacy = db.Column(db.Float)
    asset_quality_01 = db.Column(db.Float)
    asset_quality_02 = db.Column(db.Float)
    asset_quality_03 = db.Column(db.Float)
    asset_quality_04 = db.Column(db.Float)
    capital_adequacy_Rating_Status = db.Column(db.String(1000))
    asset_quality_01_Rating_Status = db.Column(db.String(1000))
    asset_quality_02_Rating_Status = db.Column(db.String(1000))
    asset_quality_03_Rating_Status = db.Column(db.String(1000))
    asset_quality_04_Rating_Status = db.Column(db.String(1000))
    saccoss_id = db.Column(
        db.Integer, db.ForeignKey('saccos.id'), nullable=False)
