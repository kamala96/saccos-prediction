# This file will handle CRUD operations

import numpy as np
from sqlalchemy import false
from . import MODELS_FOLDER, db
from .models import User, Saccos
from .models import Workout
from flask import Blueprint, flash, redirect, render_template, url_for, request
from flask_login import current_user, login_required
from joblib import dump, load
from .generate_model import OUTCOME_NAMES

# A Blueprint is way to organize contents of your file

main = Blueprint("main", __name__)


@main.route('/')
def index():
    list_of_saccos = Saccos.query.all()
    return render_template('index.html', list_of_saccos=list_of_saccos)


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
    workouts = Workout.query.filter_by(
        author=user).paginate(page=page, per_page=2)

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


@main.route('/add-saccos', methods=['POST'])
def add_saccos():
    '''
    This function adds a saccos into a database.
    '''
    saccoss = request.form.get('saccoss')

    exists = Saccos.query.filter_by(name=saccoss).first()

    if exists:
        flash('Already exists')
        return redirect(url_for('main.index'))

    new_saccos = Saccos(name=saccoss)
    db.session.add(new_saccos)
    db.session.commit()
    flash('Your request has been received successfuly!')

    return redirect(url_for('main.index'))


@main.route("/saccos/<int:saccos_id>/delete", methods=['GET', 'POST'])
def delete_saccos(saccos_id):
    saccos = Saccos.query.get_or_404(saccos_id)
    db.session.delete(saccos)
    db.session.commit()
    flash('Your post has been deleted!')
    return redirect(url_for('main.index'))


@main.route("/saccos/<int:saccos_id>", methods=['GET'])
def view_saccos(saccos_id):
    saccos = Saccos.query.get_or_404(saccos_id)
    return render_template('view_saccos.html', saccos=saccos)


def get_model(saccos_id: int, performance: int):
    '''
    This function manages a retrieval of model files.
    '''
    saccos_data = Saccos.query.get_or_404(saccos_id)
    sub_path = OUTCOME_NAMES.get(performance)
    base_path = MODELS_FOLDER+"/"+saccos_data.name.lower()+"/"+sub_path+'.joblib'

    # with open(base_path, 'rb') as file:
    #         joblib_model = load(file)
    # return joblib_model

    try:
        with open(base_path, 'rb') as file:
            joblib_model = load(file)
        return joblib_model
    except:
        return False

    # if performance == 1:
    #     # Capital adequacy
    #     with open(base_path, 'rb') as file:
    #         joblib_model = load(file)
    #     return joblib_model
    # elif performance == 2:
    #     # Asset quality 01
    #     return False
    # elif performance == 3:
    #     # Asset quality 02
    #     return False
    # elif performance == 4:
    #     # Asset quality 03
    #     return False
    # elif performance == 5:
    #     # Asset quality 04
    #     return False
    # else:
    #     return False


@main.route('/predict')
# @login_required
def do_predict():
    list_of_saccos = Saccos.query.all()
    return render_template('do_predict.html', list_of_saccos=list_of_saccos, criteria=OUTCOME_NAMES)


@main.route('/predict', methods=['POST'])
# @login_required
def do_predict_post():
    list_of_saccos = Saccos.query.all()

    # obtain all form values and place them in an array, convert into integers
    int_features = [float(x) for x in request.form.values()]

    # obtain the saccos ID and performance metric
    saccos_id = int_features[0]
    performance_metric = int_features[1]

    # remove the [saccos ID and performance metric] and combine the remaining into a final numpy array
    del int_features[0]
    del int_features[1]
    final_features = [np.array(int_features)]

    model = get_model(saccos_id, performance_metric)
    prediction_text = ""

    if(model == False):
        prediction_text = "The selection has not yet implemented"
    else:
        # predict the price given the values inputted by user
        prediction = model.predict(final_features)

        # Round the output to 2 decimal places
        output = round(prediction[0], 2)

        # If the output is negative, the values entered are unreasonable to the context of the application
        # If the output is greater than 0, return prediction
        if output <= 0:
            prediction_text = 'The Predicted Value of {} is 0%, may be the values entered are not reasonable'.format(
                OUTCOME_NAMES.get(performance_metric))
        else:
            prediction_text = 'The Predicted Value is: {}%'.format(output)

    return render_template(
        'do_predict.html',
        prediction_text=prediction_text,
        list_of_saccos=list_of_saccos, criteria=OUTCOME_NAMES)
