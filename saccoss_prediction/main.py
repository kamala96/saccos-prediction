# This file will handle CRUD operations

import numpy as np
from . import db
from .models import User
from .models import Workout
from flask import Blueprint, flash, redirect, render_template, url_for, request
from flask_login import current_user, login_required
from joblib import dump, load

# A Blueprint is way to organize contents of your file

main = Blueprint("main", __name__)

model = load('prediction-models/y1_model.joblib')

@main.route('/')
def index():
    return render_template('index.html')


@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name)


@main.route('/new')
@login_required
def new_workout():
    return render_template('create_workout.html')


@main.route("/new", methods=['POST'])
@login_required
def new_workout_post():
    pushups = request.form.get('pushups')
    comment = request.form.get('comment')
    workout = Workout(pushups=pushups, comment=comment, author=current_user)
    db.session.add(workout)
    db.session.commit()
    flash('Your workout has been added!')
    return redirect(url_for('main.user_workouts'))


@main.route("/all")
@login_required
def user_workouts():
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(email=current_user.email).first_or_404()

    # workouts = user.workouts --the same
    # workouts = Workout.query.filter_by(author=user).order_by(Workout.date_posted.desc())
    workouts = Workout.query.filter_by(author=user).paginate(page=page, per_page=2)

    return render_template('all_workouts.html', workouts=workouts, user=user)


@main.route("/workout/<int:workout_id>/update", methods=['GET', 'POST'])
@login_required
def update_workout(workout_id):
    workout = Workout.query.get_or_404(workout_id)
    if request.method == "POST":
        workout.pushups = request.form['pushups']
        workout.comment = request.form['comment']
        db.session.commit()
        flash('Your post has been updated!')
        return redirect(url_for('main.user_workouts'))

    return render_template('update_workout.html', workout=workout)


@main.route("/workout/<int:workout_id>/delete", methods=['GET', 'POST'])
@login_required
def delete_workout(workout_id):
    workout = Workout.query.get_or_404(workout_id)
    db.session.delete(workout)
    db.session.commit()
    flash('Your post has been deleted!')
    return redirect(url_for('main.user_workouts'))


@main.route('/predict')
@login_required
def do_predict():
    return render_template('do_predict.html')


@main.route('/predict', methods = ['POST'])
@login_required
def do_predict_post():
    
    #obtain all form values and place them in an array, convert into integers
    int_features = [float(x) for x in request.form.values()]
    #Combine them all into a final numpy array
    final_features = [np.array(int_features)]
    #predict the price given the values inputted by user
    prediction = model.predict(final_features)
    
    #Round the output to 2 decimal places
    output = round(prediction[0], 2)
    
    #If the output is negative, the values entered are unreasonable to the context of the application
    #If the output is greater than 0, return prediction
    if output <= 0:
        return render_template('do_predict.html', prediction_text = "The Predicted Value is 0%, may be the values entered are not reasonable")
    elif output > 0:
        return render_template('do_predict.html', prediction_text = 'The Predicted Value is: {}%'.format(output)) 