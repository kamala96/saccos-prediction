# This file will handle CRUD operations

import datetime
import shutil
from matplotlib.pyplot import title
import numpy as np
from . import MODELS_FOLDER, MODELS_PICS_FOLDER, UPLOAD_FOLDER, db
from .models import ActualAndPredicted, Evaluations, FeatureImportances, PredictionModels, User, Saccos
from .models import Workout
from flask import Blueprint, flash, redirect, render_template, url_for, request, Markup
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
    current_name = request.form.get('current_name').strip()
    current_name = current_name.strip()
    current_name = current_name.replace(" ", "-")
    current_name = current_name.upper()

    initial_name = request.form.get('initial_name')
    initial_name = initial_name.strip()
    initial_name = initial_name.replace(" ", "-")
    initial_name = initial_name.upper()

    reg_number = request.form.get('reg_number')
    reg_number = reg_number.strip()
    reg_number = reg_number.upper()

    start_date = request.form.get('start_date')
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")

    district = request.form.get('district')
    district = district.upper()

    region = request.form.get('region')
    region = region.strip()
    region = region.upper()

    initial_members = request.form.get('initial_members')

    total_males = request.form.get('total_males')
    total_females = request.form.get('total_females')
    current_members = '_'.join([total_males, total_females])

    try:
        exists = Saccos.query.filter_by(current_name=current_name).first()
        if exists:
            flash('This saccos can not be used, already exists', 'warning')
            return redirect(url_for('main.index'))
    except:
        flash('Oops!, internal server error', 'danger')
        return redirect(url_for('main.index'))

    new_saccos = Saccos(
        initial_name=initial_name,
        current_name=current_name,
        start_date=start_date,
        reg_number=reg_number,
        district=district,
        region=region,
        start_members=initial_members,
        current_members=current_members,
    )
    try:
        db.session.add(new_saccos)
        db.session.commit()
        flash('Your request has been received successfuly!', 'success')
    except Exception as e:
        flash('Oops!, internal server error', 'danger')
    return redirect(url_for('main.index'))


@main.route("/saccos/<int:saccos_id>/delete", methods=['GET', 'POST'])
def delete_saccos(saccos_id):
    try:
        saccos = Saccos.query.get_or_404(saccos_id)
    except:
        flash('No such saccos!', 'info')
        return redirect(url_for('main.index'))

    db.session.query(PredictionModels).filter(
        PredictionModels.saccoss_id == saccos_id).delete()
    db.session.commit()

    db.session.query(Evaluations).filter(
        Evaluations.saccoss_id == saccos_id).delete()
    db.session.commit()

    db.session.query(ActualAndPredicted).filter(
        ActualAndPredicted.saccoss_id == saccos_id).delete()
    db.session.commit()

    db.session.query(FeatureImportances).filter(
        FeatureImportances.feature_saccos == saccos_id).delete()
    db.session.commit()

    saccos_name = str(saccos.current_name.lower())
    saccos_models_directory = MODELS_FOLDER+"/"+saccos_name
    saccos_dataset_directory = UPLOAD_FOLDER+"/"+saccos_name

    # To remove files
    # Option 1
    # file_path = '/tmp/file.txt'
    # os.remove(file_path)
    # os.unlink(file_path)
    #
    # Option 2
    # file_path = Path('/tmp/file.txt')
    # file_path.unlink()
    #
    # Pattern matching -- remove all .txt files in the /tmp directory
    # files = glob.glob('/tmp/*.txt')
    # f.unlink()
    #
    # To remove empty dir (Folders)
    # Option 1
    # dir_path = Path('/tmp/img')
    # dir_path.rmdir()
    #
    # option 2
    # dir_path = '/tmp/img'
    # os.rmdir(dir_path)
    #
    # To remove directory with its contents
    # dir_path = '/tmp/img'
    # shutil.rmtree(dir_path)
    try:
        shutil.rmtree(saccos_models_directory)
        shutil.rmtree(saccos_dataset_directory)
    except OSError as e:
        pass
        # print("Error: %s : %s" % (e.strerror))

    try:
        db.session.delete(saccos)
        db.session.commit()
        flash('Your post has been deleted!', 'success')
    except:
        flash('Oops!, internal server error', 'danger')
    return redirect(url_for('main.index'))


@main.route("/saccos/<int:saccos_id>", methods=['GET'])
def view_saccos(saccos_id):
    # saccos = Saccos.query.get_or_404(saccos_id)
    try:
        saccos = Saccos.query.filter_by(id=saccos_id).first_or_404()
    except:
        flash('No such saccos!', 'info')
        return redirect(url_for('main.index'))

    filename = saccos.current_name.lower()
    filename = filename.replace(" ", "_")
    filename = filename+'.csv'

    try:
        clean_sample = pd.read_csv(
            UPLOAD_FOLDER+"/" + saccos.current_name.lower()+'/clean_'+filename, sep='\t')
        capital = pd.read_csv(MODELS_PICS_FOLDER+"/" +
                              saccos.current_name.lower()+"/capital-adequacy.csv", sep='\t')
        asset_1 = pd.read_csv(MODELS_PICS_FOLDER+"/" +
                              saccos.current_name.lower()+"/asset-quality-01.csv", sep='\t')
        asset_2 = pd.read_csv(MODELS_PICS_FOLDER+"/" +
                              saccos.current_name.lower()+"/asset-quality-02.csv", sep='\t')
        asset_3 = pd.read_csv(MODELS_PICS_FOLDER+"/" +
                              saccos.current_name.lower()+"/asset-quality-03.csv", sep='\t')
        asset_4 = pd.read_csv(MODELS_PICS_FOLDER+"/" +
                              saccos.current_name.lower()+"/asset-quality-04.csv", sep='\t')
    except FileNotFoundError:
        flash(Markup('You are not yet done, please visit <a href="' + url_for('generate_model.generate') +
                     '" class="alert-link"> here </a> to generate model for this saccoss'), 'info')
        return redirect(url_for('main.index'))
    except pd.errors.EmptyDataError:
        flash(message='Oops!, some important files has no data', category='danger')
        return redirect(url_for('main.index'))
    except pd.errors.ParserError:
        flash(message='Oops!, parser error', category='danger')
        return redirect(url_for('main.index'))
    except Exception as e:
        flash(message=e, category='danger')
        return redirect(url_for('main.index'))

    title = 'SEPS - ' + saccos.current_name
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
    try:
        saccos_data = Saccos.query.get_or_404(saccos_id)
    except:
        flash('No such saccos!', 'info')
        return redirect(url_for('main.do_predict'))

    saccos_name = str(saccos_data.current_name.lower())
    sub_path = str(OUTCOME_NAMES.get(performance))
    base_path = MODELS_FOLDER+"/"+saccos_name+"/"+sub_path+'.joblib'

    try:
        with open(base_path, 'rb') as file:
            joblib_model = load(file)
        return joblib_model
    except:
        return False

    # try:
    #     with open(base_path, 'rb') as file:
    #         joblib_model = load(file)
    #     return joblib_model
    # except:
    #     flash(Markup('Oops!, this saccos has not yet implementated. Please visit <a href="' + url_for('generate_model.generate') +
    #           '" class="alert-link"> here </a> to generate its implementations'), 'info')
    #     return redirect(url_for('main.do_predict'))

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


@main.route('/prediction')
# @login_required
def do_predict():
    try:
        list_of_saccos = Saccos.query.all()
    except:
        flash('Internal server error', 'info')
        return redirect(url_for(request.url))

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
    saccos = saccos_data.current_name
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
        flash(Markup('Oops!, this saccos has not yet been implemented. Please visit <a href="' + url_for('generate_model.generate') +
                     '" class="alert-link"> here </a> to generate its implementations'), 'info')
        return redirect(url_for('main.do_predict'))
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
