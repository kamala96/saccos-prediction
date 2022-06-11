# This file will handle CRUD operations

from matplotlib.pyplot import title
import numpy as np
from sqlalchemy import false
from . import MODELS_FOLDER, MODELS_PICS_FOLDER, UPLOAD_FOLDER, db
from .models import PredictionModels, User, Saccos
from .models import Workout
from flask import Blueprint, flash, redirect, render_template, url_for, request
from flask_login import current_user, login_required
from joblib import dump, load
from .generate_model import OUTCOME_NAMES, asset_quality_01_rating, asset_quality_02_rating, asset_quality_03_rating, asset_quality_04_rating, capital_adequacy_rating
import pandas as pd
from IPython.display import HTML

# A Blueprint is way to organize contents of your file

main = Blueprint("main", __name__)


@main.route('/')
def index():
    list_of_saccos = Saccos.query.all()
    title = 'Saccos Evaluation and Prediction System (SEPS)'
    return render_template(
        'index.html',
        title=title,
        list_of_saccos=list_of_saccos
    )


@main.route('/profile')
@login_required
def profile():
    return render_template(
        'profile.html',
        name=current_user.name
    )


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
    saccoss = saccoss.replace(" ", "-")

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
    # saccos = Saccos.query.get_or_404(saccos_id)
    saccos = Saccos.query.filter_by(id=saccos_id).first_or_404()
    filename = saccos.name.lower()
    filename = filename.replace(" ", "_")
    filename = filename+'.csv'
    clean_sample = pd.read_csv(
        UPLOAD_FOLDER+"/" + saccos.name.lower()+'/clean_'+filename, sep='\t')
    capital = pd.read_csv(MODELS_PICS_FOLDER+"/" +
                          saccos.name.lower()+"/capital-adequacy.csv", sep='\t')
    asset_1 = pd.read_csv(MODELS_PICS_FOLDER+"/" +
                          saccos.name.lower()+"/asset-quality-01.csv", sep='\t')
    asset_2 = pd.read_csv(MODELS_PICS_FOLDER+"/" +
                          saccos.name.lower()+"/asset-quality-02.csv", sep='\t')
    asset_3 = pd.read_csv(MODELS_PICS_FOLDER+"/" +
                          saccos.name.lower()+"/asset-quality-03.csv", sep='\t')
    asset_4 = pd.read_csv(MODELS_PICS_FOLDER+"/" +
                          saccos.name.lower()+"/asset-quality-04.csv", sep='\t')
    title = 'SEPS - ' + saccos.name
    # model_summary = PredictionModels.query.filter_by(author=saccos).group_by(PredictionModels.performance_criteria).all()
    # print(clean_sample.to_html())
    return render_template(
        'view_saccos.html',
        title=title, saccos=saccos,
        outcomes=OUTCOME_NAMES, data=clean_sample, capital=capital,
        asset_1=asset_1, asset_2=asset_2, asset_3=asset_3, asset_4=asset_4
    )


def get_model(saccos_id: int, performance: int):
    '''
    This function manages a retrieval of model files.
    '''
    saccos_data = Saccos.query.get_or_404(saccos_id)
    saccos_name = str(saccos_data.name.lower())
    sub_path = str(OUTCOME_NAMES.get(performance))
    base_path = MODELS_FOLDER+"/"+saccos_name+"/"+sub_path+'.joblib'

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
    title = 'SEPS - Prediction Page'
    return render_template(
        'do_predict.html',
        title=title, list_of_saccos=list_of_saccos,
        criteria=OUTCOME_NAMES
    )


def abbrev_to_length(key_word):
    if key_word == 'OP':
        result = 'Outstanding Performance'

    elif key_word == 'SP':
        result = 'Superior Performance'

    elif key_word == 'AP':
        result = 'Avarage Performance'

    elif key_word == 'UP':
        result = 'Under Performance'

    elif key_word == 'DP':
        result = 'Doubtful Performance'

    else:
        pass

    return result


@main.route('/predict', methods=['POST'])
# @login_required
def do_predict_post():
    list_of_saccos = Saccos.query.all()

    # obtain all form values and place them in an array, convert into floats
    int_features = [float(x) for x in request.form.values()]

    # obtain the saccos ID and performance metric
    saccos_id = int(int_features[0])
    performance_metric = int(int_features[1])

    saccos_data = Saccos.query.get_or_404(saccos_id)

    status = True
    criteria = OUTCOME_NAMES.get(performance_metric)
    features = ''
    message = ''
    model_used = ''
    saccos = saccos_data.name
    output = 0
    ratings = ''

    # remove the [saccos ID and performance metric -first two elements] and combine the remaining into a final numpy array
    n = 2
    int_features = int_features[n:]
    # del int_features[:n]
    final_features = [np.array(int_features)]

    model = get_model(saccos_id, performance_metric)

    if(model == False):
        status = False
        message = "The selection has not yet implemented"
    else:
        # predict the price given the values inputted by user
        prediction = model.predict(final_features)

        model_used = type(model).__name__

        # Round the output to 2 decimal places
        output = round(prediction[0], 2)

        # If the output is negative, the values entered are unreasonable to the context of the application
        # If the output is greater than 0, return prediction
        # if output <= 0:
        #     message = 'May be the values entered are not reasonable to the context'
        # else:
        #     message = 'Prediction is greatly reasonable'

    title = 'SEPS - Predicting ' + str(criteria) + ' for ' + saccos

    if performance_metric == 1:
        ratings = capital_adequacy_rating(float(output))
        ratings = abbrev_to_length(ratings)
        features = {
            'Core Capital': int_features[0],
            'Total Assets': int_features[1]
        }
    elif performance_metric == 2:
        ratings = asset_quality_01_rating(float(output))
        ratings = abbrev_to_length(ratings)
        features = {
            'Non-performing loans': int_features[0],
            'Gross Loan Portifolio/Total loans': int_features[1]
        }
    elif performance_metric == 3:
        ratings = asset_quality_02_rating(float(output))
        ratings = abbrev_to_length(ratings)
        features = {
            'Non-earning assets': int_features[0],
            'Total assets': int_features[1]
        }
    elif performance_metric == 4:
        ratings = asset_quality_03_rating(float(output))
        ratings = abbrev_to_length(ratings)
        features = {
            'General loan loss reserve': int_features[0],
            'Gross loans': int_features[1]
        }
    elif performance_metric == 5:
        ratings = asset_quality_04_rating(float(output))
        ratings = abbrev_to_length(ratings)
        features = {
            'Write-offs': int_features[0],
            'Recoveries': int_features[1],
            'Total loans': int_features[2],
        }
    else:
        pass

    return render_template(
        'do_predict.html',
        title=title,
        list_of_saccos=list_of_saccos,
        status=status,
        criteria=criteria,
        features=features,
        message=message,
        model_used=model_used,
        saccos=saccos,
        saccos_id=saccos_id,
        ratings=ratings,
        output=output
    )
