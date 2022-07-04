import numbers
import os
from pathlib import Path
from flask import Blueprint, flash, render_template, url_for, request, redirect, Markup
from joblib import dump
from matplotlib import pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.neighbors import KNeighborsRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from werkzeug.utils import secure_filename
from .models import ActualAndPredicted, Evaluations, FeatureImportances, Saccos, PredictionModels
from . import MODELS_FOLDER, MODELS_PICS_FOLDER, UPLOAD_FOLDER, db
import seaborn as sns

import numpy as np
import pandas as pd

generate_model = Blueprint('generate_model', __name__)

ALLOWED_EXTENSIONS = {'csv'}

OUTCOME_NAMES = dict(
    {
        1: 'capital-adequacy',
        2: 'asset-quality-01',
        3: 'asset-quality-02',
        4: 'asset-quality-03',
        5: 'asset-quality-04'
    })

RENAME_COLUMN = {
    'Date': 'Month', 'CC': 'Core capital', 'TA': 'Total assets', 'NPL': 'Non-performing loans',
    'GLP-TL': 'Gross Loan Portifolio/Total loans', 'NEA': 'Non-earning assets',
    'GLLR': 'General loan loss reserve', 'GL': 'Gross loans', 'WO': 'Write-offs', 'RCV': 'Recoveries'
}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def renamed_file_name(saccos_name):
    new_name = saccos_name+".csv"
    return new_name.lower()


def read_data(file_name, saccos_id):
    try:
        file_data = pd.read_csv(UPLOAD_FOLDER + "/" +
                                saccos_id + "/" + file_name)
    except:
        flash('No file found', 'danger')
        return redirect(url_for('generate_model.generate'))
    return file_data


def handle_plain_negatives(row):
    if row < 0:
        # whatever  you logic
        return 0
    else:
        return row


def handle_percentage_negatives(row):
    if isinstance(row, numbers.Number):
        if row < 0:
            # whatever  you logic
            return 0
        else:
            row = row * 100
            row = "{:.2f}".format(row)
            row = float(row)
            return row
    return 0


def handle_division_by_zero(n, d):
    # return n / d if d else 0
    try:
        result = (n/d)
        return result
    except (ZeroDivisionError, ValueError):
        return 0


def capital_adequacy_rating(row):
    if row >= 11.0:
        result = 'OP'

    elif row >= 9.0:
        result = 'SP'

    elif row >= 6.0:
        result = 'AP'

    elif row >= 4.0:
        result = 'UP'

    else:
        result = 'DP'

    return result


def asset_quality_01_rating(row):
    if row > 10.1:
        result = 'DP'

    elif row >= 8.1:
        result = 'UP'

    elif row >= 6.1:
        result = 'AP'

    elif row >= 5.1:
        result = 'SP'

    else:
        result = 'OP'

    return result


def asset_quality_02_rating(row):
    if row > 21.1:
        result = 'DP'

    elif row >= 18.1:
        result = 'UP'

    elif row >= 15.1:
        result = 'AP'

    elif row >= 10.1:
        result = 'SP'

    else:
        result = 'OP'

    return result


def asset_quality_03_rating(row):
    if row > 1.0:
        result = 'OP'

    elif row >= 0.75:
        result = 'SP'

    elif row >= 0.50:
        result = 'AP'

    elif row >= 0.25:
        result = 'UP'

    else:
        result = 'DP'

    return result


def asset_quality_04_rating(row):
    if row >= 3.6:
        result = 'DP'

    elif row >= 2.6:
        result = 'UP'

    elif row >= 2.1:
        result = 'AP'

    elif row >= 1.6:
        result = 'SP'

    else:
        result = 'OP'

    return result


def pre_processing(data):
    pd.set_option('display.float_format',  '{:,.2f}'.format)
    data[[
        RENAME_COLUMN["CC"], RENAME_COLUMN["TA"], RENAME_COLUMN["NPL"], RENAME_COLUMN["GLP-TL"],
        RENAME_COLUMN["GLLR"], RENAME_COLUMN["NEA"], RENAME_COLUMN["GL"], RENAME_COLUMN["WO"], RENAME_COLUMN["RCV"]
    ]] = data[[
        RENAME_COLUMN["CC"], RENAME_COLUMN["TA"], RENAME_COLUMN["NPL"], RENAME_COLUMN["GLP-TL"],
        RENAME_COLUMN["GLLR"], RENAME_COLUMN["NEA"], RENAME_COLUMN["GL"], RENAME_COLUMN["WO"], RENAME_COLUMN["RCV"]
    ]].apply(pd.to_numeric)
    # data[["CC", "TA", "NPL", "GLP-TL", "GLLR", "GL", "WO", "RCV"]] = data[["CC", "TA", "NPL", "GLP-TL", "GLLR", "GL", "WO", "RCV"]].apply(pd.to_numeric)
    data[RENAME_COLUMN["Date"]] = pd.to_datetime(
        data[RENAME_COLUMN["Date"]], format='%Y/%m/%d')
    # data = data.drop('xxxx', axis=1)
    data = data.set_index(RENAME_COLUMN["Date"])
    return data


def further_preprocessing(data):
    # data['y1'] = data.apply(lambda row: row.CC / row.TA, axis = 1)

    # Capital adequacy
    data[OUTCOME_NAMES.get(1)] = handle_division_by_zero(
        data[RENAME_COLUMN["CC"]], data[RENAME_COLUMN["TA"]])
    # twin_col1 = OUTCOME_NAMES.get(1)+" [Rating Status]"
    # data[twin_col1] = np.where(data[OUTCOME_NAMES.get(1)] >= 10, True, False)
    # data.loc[data['y1'] <= 0, 'y1'] = 0
    # data.loc[data['y1'] > 0, 'y1'] = data['y1'] * 100

    # Asset quality 1
    data[OUTCOME_NAMES.get(2)] = handle_division_by_zero(
        data[RENAME_COLUMN["NPL"]], data[RENAME_COLUMN["GLP-TL"]])

    # Asset quality 2
    data[OUTCOME_NAMES.get(3)] = handle_division_by_zero(
        data[RENAME_COLUMN["NEA"]], data[RENAME_COLUMN["TA"]])

    # Asset quality 3
    data[OUTCOME_NAMES.get(4)] = handle_division_by_zero(
        data[RENAME_COLUMN["GLLR"]], data[RENAME_COLUMN["GL"]])

    # Asset quality 4
    data[OUTCOME_NAMES.get(5)] = handle_division_by_zero(
        (data[RENAME_COLUMN["WO"]] - data[RENAME_COLUMN["RCV"]]), data[RENAME_COLUMN["GLP-TL"]])

    data = data.asfreq('M')
    data = data.sort_index()

    # handling negative values
    data[RENAME_COLUMN["CC"]] = data[RENAME_COLUMN["CC"]].apply(
        handle_plain_negatives)
    data[RENAME_COLUMN["TA"]] = data[RENAME_COLUMN["TA"]].apply(
        handle_plain_negatives)
    data[RENAME_COLUMN["NPL"]] = data[RENAME_COLUMN["NPL"]].apply(
        handle_plain_negatives)
    data[RENAME_COLUMN["GLP-TL"]] = data[RENAME_COLUMN["GLP-TL"]
                                         ].apply(handle_plain_negatives)
    data[RENAME_COLUMN["GLLR"]] = data[RENAME_COLUMN["GLLR"]].apply(
        handle_plain_negatives)
    data[RENAME_COLUMN["NEA"]] = data[RENAME_COLUMN["NEA"]].apply(
        handle_plain_negatives)
    data[RENAME_COLUMN["GL"]] = data[RENAME_COLUMN["GL"]].apply(
        handle_plain_negatives)
    data[RENAME_COLUMN["WO"]] = data[RENAME_COLUMN["WO"]].apply(
        handle_plain_negatives)
    data[RENAME_COLUMN["RCV"]] = data[RENAME_COLUMN["RCV"]].apply(
        handle_plain_negatives)

    data[OUTCOME_NAMES.get(1)] = data[OUTCOME_NAMES.get(
        1)].apply(handle_percentage_negatives)
    data[OUTCOME_NAMES.get(2)] = data[OUTCOME_NAMES.get(
        2)].apply(handle_percentage_negatives)
    data[OUTCOME_NAMES.get(3)] = data[OUTCOME_NAMES.get(
        3)].apply(handle_percentage_negatives)
    data[OUTCOME_NAMES.get(4)] = data[OUTCOME_NAMES.get(
        4)].apply(handle_percentage_negatives)
    data[OUTCOME_NAMES.get(5)] = data[OUTCOME_NAMES.get(
        5)].apply(handle_percentage_negatives)

    # Adding rating columns
    twin_col1 = OUTCOME_NAMES.get(1)+" [Rating Status]"
    data[twin_col1] = data[OUTCOME_NAMES.get(1)].apply(capital_adequacy_rating)
    twin_col2 = OUTCOME_NAMES.get(2)+" [Rating Status]"
    data[twin_col2] = data[OUTCOME_NAMES.get(2)].apply(asset_quality_01_rating)
    twin_col3 = OUTCOME_NAMES.get(3)+" [Rating Status]"
    data[twin_col3] = data[OUTCOME_NAMES.get(3)].apply(asset_quality_02_rating)
    twin_col4 = OUTCOME_NAMES.get(4)+" [Rating Status]"
    data[twin_col4] = data[OUTCOME_NAMES.get(4)].apply(asset_quality_03_rating)
    twin_col5 = OUTCOME_NAMES.get(5)+" [Rating Status]"
    data[twin_col5] = data[OUTCOME_NAMES.get(5)].apply(asset_quality_04_rating)

    final = data.fillna(0)

    return final


def define_x_y(data, y_column):
    if y_column == OUTCOME_NAMES.get(1):
        #         x = data_df.drop(['PE'], axis=1).values
        x = data[[RENAME_COLUMN["CC"], RENAME_COLUMN["TA"]]]
        y = data[y_column]
        return x, y
    elif y_column == OUTCOME_NAMES.get(2):
        x = data[[RENAME_COLUMN["NPL"], RENAME_COLUMN["GLP-TL"]]]
        y = data[y_column]
        return x, y
    elif y_column == OUTCOME_NAMES.get(3):
        x = data[[RENAME_COLUMN["NEA"], RENAME_COLUMN["TA"]]]
        y = data[y_column]
        return x, y
    elif y_column == OUTCOME_NAMES.get(4):
        x = data[[RENAME_COLUMN["GLLR"], RENAME_COLUMN["GL"]]]
        y = data[y_column]
        return x, y
    elif y_column == OUTCOME_NAMES.get(5):
        x = data[[RENAME_COLUMN["WO"], RENAME_COLUMN["RCV"],
                  RENAME_COLUMN["GLP-TL"]]]
        y = data[y_column]
        return x, y
    else:
        return False


def get_score(model, X_train, X_test, y_train, y_test):
    model.fit(X_train, y_train)
    return model.score(X_test, y_test)


def save_model(model, path):
    path = path+'.joblib'
    dump(model, path)


def plot_actual_vs_predicted(saccos, criteria, path):
    Actual = []
    Predicted = []

    data = ActualAndPredicted.query.with_entities(
        ActualAndPredicted.actual, ActualAndPredicted.predicted).filter_by(saccoss_id=saccos, performance_criteria=criteria)

    for i in data:
        Actual.append(i[0])
        Predicted.append(i[1])

    plt.figure(figsize=(12, 10))
    ax1 = sns.distplot(Actual, hist=False, color="r", label="Actual Value")
    sns.distplot(Predicted, hist=False, color="b",
                 label="Fitted Values", ax=ax1)

    plt.title('Actual vs Predicted Values for '+criteria)
    plt.xlabel('Actual ' + criteria + ' (%)')
    plt.ylabel('Predicted ' + criteria + ' (%)')
    # plt.show()
    # plt.close()
    plt.savefig(path)


def loop_models(X_train, X_test, Y_train, Y_test, saccos_id, saccos, criteria):
    models = [LinearRegression(), RandomForestRegressor(),
              KNeighborsRegressor(), DecisionTreeRegressor()]
    r2_scores = {
        'LinearRegression()': 0,
        'RandomForestRegressor()': 0,
        'KNeighborsRegressor()': 0,
        'DecisionTreeRegressor()': 0,
    }
    mean_absolute_errors = {
        'LinearRegression()': 0,
        'RandomForestRegressor()': 0,
        'KNeighborsRegressor()': 0,
        'DecisionTreeRegressor()': 0,
    }
    root_mean_squared_errors = {
        'LinearRegression()': 0,
        'RandomForestRegressor()': 0,
        'KNeighborsRegressor()': 0,
        'DecisionTreeRegressor()': 0,
    }
    selected = {
        'LinearRegression()': False,
        'RandomForestRegressor()': False,
        'KNeighborsRegressor()': False,
        'DecisionTreeRegressor()': False,
    }
    best_model_name = ''

    for model in models:
        model.fit(X_train, Y_train)
        predictions = model.predict(X_test)
        r2_scores[type(model).__name__ +
                  "()"] = round(r2_score(Y_test, predictions), 5)
        mean_absolute_errors[type(model).__name__ +
                             "()"] = round(mean_absolute_error(Y_test, predictions), 5)
        root_mean_squared_errors[type(model).__name__ +
                                 "()"] = round(np.sqrt(mean_squared_error(Y_test, predictions)), 5)
    best_model_name = min(mean_absolute_errors, key=mean_absolute_errors.get)
    # best_model_value = mean_absolute_errors.get(best_model_name)

    # Model file path
    Path(MODELS_FOLDER, saccos).mkdir(exist_ok=True)
    model_path = MODELS_FOLDER+"/"+saccos+"/"+criteria+'.joblib'

    # fitting the right model
    final_model = ''
    if best_model_name.startswith("L"):
        final_model = LinearRegression()
        selected[best_model_name] = True
    elif best_model_name.startswith("R"):
        final_model = RandomForestRegressor()
        selected[best_model_name] = True
    elif best_model_name.startswith("K"):
        final_model = KNeighborsRegressor()
        selected[best_model_name] = True
    elif best_model_name.startswith("D"):
        final_model = DecisionTreeRegressor()
        selected[best_model_name] = True
    else:
        pass

    final_model = final_model.fit(X_train, Y_train)
    prediction = final_model.predict(X_test)
    # error = mean_absolute_error(Y_test, prediction)
    dump(final_model, model_path)

    # ----------------------------------------------------------------------------------
    # MODEL -- FEATURE IMPORTANCES -- START ############################################
    model_title = type(final_model).__name__
    importances = pd.DataFrame(data={
        'Attribute': X_train.columns,
        'Importance': 0,
    })
    if model_title == 'LinearRegression':
        # Put simply, if an assigned coefficient is a large (negative or positive) number, it has some influence on the prediction.
        # if the coefficient is zero, it doesn’t have any impact on the prediction
        importances = pd.DataFrame(data={
            'Attribute': X_train.columns,
            'Importance': final_model.coef_
        })
        importances = importances.sort_values(by='Importance', ascending=False)

    elif model_title == 'RandomForestRegressor':
        importances = pd.DataFrame(data={
            'Attribute': X_train.columns,
            'Importance': (final_model.feature_importances_ / sum(final_model.feature_importances_)) * 100
        })
        importances = importances.sort_values(by='Importance', ascending=False)

    elif model_title == 'KNeighborsRegressor':
        pass
        # importances = pd.DataFrame(data={
        #     'Attribute': X_train.columns,
        #     'Importance': (final_model.feature_importances_ / sum(final_model.feature_importances_)) * 100
        # })
        # importances = importances.sort_values(by='Importance', ascending=False)
    elif model_title == 'DecisionTreeRegressor':
        importances = pd.DataFrame(data={
            'Attribute': X_train.columns,
            'Importance': (final_model.feature_importances_ / sum(final_model.feature_importances_)) * 100
        })
        importances = importances.sort_values(by='Importance', ascending=False)

    else:
        pass

    # Initialize empty array of insert data
    feature_rows = []

    # Iterate through the dataset and prepare insert query
    for i, row in importances.iterrows():
        my_row = FeatureImportances(
            feature_index=i+1,
            feature_name=row['Attribute'],
            feature_criteria=criteria,
            feature_value=row['Importance'],
            feature_saccos=saccos_id
        )
        feature_rows.append(my_row)

    # save our data
    try:
        db.session.add_all(feature_rows)
        db.session.commit()
    except:
        flash('Internal server error', 'danger')
        # return redirect(request.url)

    # MODEL -- FEATURE IMPORTANCES -- END ############################################
    # ---------------------------------------------------------------------------------------

    # Preparing and recording actual vs predicted
    final_df = pd.DataFrame(data=Y_test)
    final_df['predicted'] = prediction

    # Initialize empty array of insert data
    actual_and_predicted_rows = []

    # Iterate through the dataset and prepare insert query
    for i, row in final_df.iterrows():
        my_row = ActualAndPredicted(
            month=i,
            prediction_model=type(final_model).__name__,
            performance_criteria=criteria,
            actual=row[criteria],
            predicted=float("{:.2f}".format(row['predicted'])),
            saccoss_id=saccos_id
        )
        actual_and_predicted_rows.append(my_row)

    # save our data
    db.session.add_all(actual_and_predicted_rows)
    db.session.commit()

    # Now create visualizations according to db
    Path(MODELS_PICS_FOLDER, saccos).mkdir(parents=True, exist_ok=True)
    model_predictions_path = MODELS_PICS_FOLDER+"/"+saccos+"/"+criteria+'.csv'
    model_pics_path = MODELS_PICS_FOLDER+"/"+saccos+"/"+criteria+'.png'
    final_df.to_csv(model_predictions_path, sep='\t')
    plot_actual_vs_predicted(saccos_id, criteria, model_pics_path)

    # --------------------------------------------------------------

    # Recording model informations
    data_rows = []
    for model2 in models:
        row = PredictionModels(
            title=type(model2).__name__ + ' for '+criteria+' of '+saccos,
            performance_criteria=criteria,
            model_used=type(model2).__name__,
            r2_score=r2_scores.get(type(model2).__name__+"()"),
            mean_absolute_error=mean_absolute_errors.get(
                type(model2).__name__+"()"),
            root_mean_squared_error=root_mean_squared_errors.get(
                type(model2).__name__+"()"),
            selected=selected.get(type(model2).__name__+"()"),
            saccoss_id=saccos_id)
        data_rows.append(row)

    db.session.add_all(data_rows)
    db.session.commit()

    # insert_model = PredictionModels(title='Generated Model 01', performance_criteria=OUTCOME_NAMES.get(
    #     1), model_used='Linear Regression', model_accuracy=score_1, saccoss_id=full_saccos.id)


#    db.session.add(insert_model_5)
#    db.session.commit()
    return True


@generate_model.route('/generate', methods=['GET', 'POST'])
def generate():
    title = 'SEPS - Model Generation Page'
    list_of_saccos = Saccos.query.all()

    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part', 'warning')
            return redirect(request.url)

        saccos_id = int(request.form.get('saccos-name'))
        try:
            full_saccos = Saccos.query.get_or_404(saccos_id)
        except:
            flash('No such saccoss', 'info')
            return redirect(request.url)

        # outcome = int(request.form.get('outcome'))
        file = request.files['file']

        # If the user does not select a file.
        if file.filename == '':
            flash('No selected file', 'warning')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            Path(UPLOAD_FOLDER, full_saccos.current_name.lower()).mkdir(
                exist_ok=True)
            # some custom file name
            file.filename = renamed_file_name(full_saccos.current_name)
            # some custom file name
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER,
                      full_saccos.current_name.lower(), filename))

            data = read_data(filename, full_saccos.current_name.lower())
            data = pre_processing(data)
            data = further_preprocessing(data)
            data.to_csv(UPLOAD_FOLDER+"/" +
                        full_saccos.current_name.lower()+'/clean_'+filename, sep='\t')

            # Delete the evaluation records for a saccos -- then populate with new records
            try:
                db.session.query(Evaluations).filter(
                    Evaluations.saccoss_id == saccos_id).delete()
                db.session.commit()
            except:
                pass

            # cols = "','".join([str(i) for i in data.columns.tolist()])
            # print(cols)

            # Initialize empty array of insert data
            data_rows = []

            # Iterate through the dataset and prepare insert query
            for i, row in data.iterrows():
                my_row = Evaluations(
                    month=i,
                    cc=row[RENAME_COLUMN["CC"]],
                    ta=row[RENAME_COLUMN["TA"]],
                    npl=row[RENAME_COLUMN["NPL"]],
                    glp_tl=row[RENAME_COLUMN["GLP-TL"]],
                    nea=row[RENAME_COLUMN["NEA"]],
                    gllr=row[RENAME_COLUMN["GLLR"]],
                    gl=row[RENAME_COLUMN["GL"]],
                    wo=row[RENAME_COLUMN["WO"]],
                    rcv=row[RENAME_COLUMN["RCV"]],
                    capital_adequacy=row[OUTCOME_NAMES.get(1)],
                    asset_quality_01=row[OUTCOME_NAMES.get(2)],
                    asset_quality_02=row[OUTCOME_NAMES.get(3)],
                    asset_quality_03=row[OUTCOME_NAMES.get(4)],
                    asset_quality_04=row[OUTCOME_NAMES.get(5)],
                    capital_adequacy_Rating_Status=row[OUTCOME_NAMES.get(
                        1)+" [Rating Status]"],
                    asset_quality_01_Rating_Status=row[OUTCOME_NAMES.get(
                        2)+" [Rating Status]"],
                    asset_quality_02_Rating_Status=row[OUTCOME_NAMES.get(
                        3)+" [Rating Status]"],
                    asset_quality_03_Rating_Status=row[OUTCOME_NAMES.get(
                        4)+" [Rating Status]"],
                    asset_quality_04_Rating_Status=row[OUTCOME_NAMES.get(
                        5)+" [Rating Status]"],
                    saccoss_id=saccos_id
                )
                data_rows.append(my_row)

            # save our data
            try:
                db.session.add_all(data_rows)
                db.session.commit()
            except:
                flash('Internal server error', 'danger')
                return redirect(request.url)

            x_y_splits_1 = define_x_y(data, OUTCOME_NAMES.get(1))
            x_y_splits_2 = define_x_y(data, OUTCOME_NAMES.get(2))
            x_y_splits_3 = define_x_y(data, OUTCOME_NAMES.get(3))
            x_y_splits_4 = define_x_y(data, OUTCOME_NAMES.get(4))
            x_y_splits_5 = define_x_y(data, OUTCOME_NAMES.get(5))

            X_1 = x_y_splits_1[0]
            y_1 = x_y_splits_1[1]
            X_2 = x_y_splits_2[0]
            y_2 = x_y_splits_2[1]
            X_3 = x_y_splits_3[0]
            y_3 = x_y_splits_3[1]
            X_4 = x_y_splits_4[0]
            y_4 = x_y_splits_4[1]
            X_5 = x_y_splits_5[0]
            y_5 = x_y_splits_5[1]

            X_train_1, X_test_1, y_train_1, y_test_1 = train_test_split(
                X_1, y_1, test_size=0.2, random_state=0)
            X_train_2, X_test_2, y_train_2, y_test_2 = train_test_split(
                X_2, y_2, test_size=0.2, random_state=0)
            X_train_3, X_test_3, y_train_3, y_test_3 = train_test_split(
                X_3, y_3, test_size=0.2, random_state=0)
            X_train_4, X_test_4, y_train_4, y_test_4 = train_test_split(
                X_4, y_4, test_size=0.2, random_state=0)
            X_train_5, X_test_5, y_train_5, y_test_5 = train_test_split(
                X_5, y_5, test_size=0.2, random_state=0)

            # Incase -- delete specific table
            # try:
            #     db.session.drop(PredictionModels)
            # except:
            #     pass

            # Incase -- delete all records
            # try:
            #     db.session.query(PredictionModels).delete()
            #     db.session.commit()
            # except:
            #     pass

            # Delete the prediction records for a saccos -- then populate with new records
            try:
                db.session.query(PredictionModels).filter(
                    PredictionModels.saccoss_id == saccos_id).delete()
                db.session.commit()
            except:
                pass

            # Delete the Actual_and_Predicited records for a saccos -- then populate with new records
            try:
                db.session.query(ActualAndPredicted).filter(
                    ActualAndPredicted.saccoss_id == saccos_id).delete()
                db.session.commit()
            except:
                pass

            # Delete the importances records for a saccos -- then populate with new records
            try:
                db.session.query(FeatureImportances).filter(
                    FeatureImportances.feature_saccos == saccos_id).delete()
                db.session.commit()
            except:
                pass

            model_1_process = loop_models(
                X_train_1, X_test_1, y_train_1, y_test_1, saccos_id, full_saccos.current_name.lower(), OUTCOME_NAMES.get(1))
            model_2_process = loop_models(
                X_train_2, X_test_2, y_train_2, y_test_2, saccos_id, full_saccos.current_name.lower(), OUTCOME_NAMES.get(2))
            model_3_process = loop_models(
                X_train_3, X_test_3, y_train_3, y_test_3, saccos_id, full_saccos.current_name.lower(), OUTCOME_NAMES.get(3))
            model_4_process = loop_models(
                X_train_4, X_test_4, y_train_4, y_test_4, saccos_id, full_saccos.current_name.lower(), OUTCOME_NAMES.get(4))
            model_5_process = loop_models(
                X_train_5, X_test_5, y_train_5, y_test_5, saccos_id, full_saccos.current_name.lower(), OUTCOME_NAMES.get(5))

            # ml_linear_1 = LinearRegression()
            # ml_linear_1.fit(X_train_1, y_train_1)
            # ml_linear_2 = LinearRegression()
            # ml_linear_2.fit(X_train_2, y_train_2)
            # ml_linear_3 = LinearRegression()
            # ml_linear_3.fit(X_train_3, y_train_3)
            # ml_linear_4 = LinearRegression()
            # ml_linear_4.fit(X_train_4, y_train_4)
            # ml_linear_5 = LinearRegression()
            # ml_linear_5.fit(X_train_5, y_train_5)

            # y_pred_1 = ml_linear_1.predict(X_test_1)
            # y_pred_2 = ml_linear_2.predict(X_test_2)
            # y_pred_3 = ml_linear_3.predict(X_test_3)
            # y_pred_4 = ml_linear_4.predict(X_test_4)
            # y_pred_5 = ml_linear_5.predict(X_test_5)

            # score_1 = round(r2_score(y_test_1, y_pred_1) * 100, 2)
            # score_2 = round(r2_score(y_test_2, y_pred_2) * 100, 2)
            # score_3 = round(r2_score(y_test_3, y_pred_3) * 100, 2)
            # score_4 = round(r2_score(y_test_4, y_pred_4) * 100, 2)
            # score_5 = round(r2_score(y_test_5, y_pred_5) * 100, 2)

            # Path(MODELS_FOLDER, full_saccos.current_name.lower()).mkdir(
            #     exist_ok=True)

            # model_path_1 = MODELS_FOLDER+"/" + \
            #     full_saccos.current_name.lower()+"/"+OUTCOME_NAMES.get(1)+'.joblib'
            # model_path_2 = MODELS_FOLDER+"/" + \
            #     full_saccos.current_name.lower()+"/"+OUTCOME_NAMES.get(2)+'.joblib'
            # model_path_3 = MODELS_FOLDER+"/" + \
            #     full_saccos.current_name.lower()+"/"+OUTCOME_NAMES.get(3)+'.joblib'
            # model_path_4 = MODELS_FOLDER+"/" + \
            #     full_saccos.current_name.lower()+"/"+OUTCOME_NAMES.get(4)+'.joblib'
            # model_path_5 = MODELS_FOLDER+"/" + \
            #     full_saccos.current_name.lower()+"/"+OUTCOME_NAMES.get(5)+'.joblib'

            # saving model into a file
            # dump(ml_linear_1, model_path_1)
            # dump(ml_linear_2, model_path_2)
            # dump(ml_linear_3, model_path_3)
            # dump(ml_linear_4, model_path_4)
            # dump(ml_linear_5, model_path_5)

            # data
            # pd.DataFrame(model.coef_, x.columns, columns = ['Coeff'])

            # Evaluation
            # Mean absolute error
            # Mean squared error
            # Root mean squared error

            # Saving info into the database
            # PredictionModels.query.delete()
            # insert_model_1 = PredictionModels(title='Generated Model 01', performance_criteria=OUTCOME_NAMES.get(
            #     1), model_used='Linear Regression', model_accuracy=score_1, saccoss_id=full_saccos.id)
            # insert_model_2 = PredictionModels(title='Generated Model 02', performance_criteria=OUTCOME_NAMES.get(
            #     2), model_used='Linear Regression', model_accuracy=score_2, saccoss_id=full_saccos.id)
            # insert_model_3 = PredictionModels(title='Generated Model 03', performance_criteria=OUTCOME_NAMES.get(
            #     3), model_used='Linear Regression', model_accuracy=score_3, saccoss_id=full_saccos.id)
            # insert_model_4 = PredictionModels(title='Generated Model 04', performance_criteria=OUTCOME_NAMES.get(
            #     4), model_used='Linear Regression', model_accuracy=score_4, saccoss_id=full_saccos.id)
            # insert_model_5 = PredictionModels(title='Generated Model 05', performance_criteria=OUTCOME_NAMES.get(
            #     5), model_used='Linear Regression', model_accuracy=score_5, saccoss_id=full_saccos.id)

            # db.session.add(insert_model_1)
            # db.session.add(insert_model_2)
            # db.session.add(insert_model_3)
            # db.session.add(insert_model_4)
            # db.session.add(insert_model_5)
            # db.session.commit()

            # cross_val_score(LinearRegression(), X, y)
            flash(Markup('Re-generation successed for '+full_saccos.current_name +
                  '. Please visit <a href="' + url_for('main.view_saccos', saccos_id=saccos_id) + '" class="alert-link"> here </a> for the detailed generation info'), category="success")
            # return str(score_1)
            return redirect(url_for('generate_model.generate'))
        else:
            flash("Please select the valid file format", "danger")
    return render_template(
        'generate_models.html', title=title,
        list_of_saccos=list_of_saccos
    )
