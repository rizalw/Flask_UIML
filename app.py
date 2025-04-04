from flask import Flask, render_template, url_for, redirect, send_from_directory, request
from flask_migrate import Migrate
from flask_login import LoginManager, login_required, current_user
from flask_wtf.csrf import CSRFProtect

import os
import pandas as pd
import pickle

from auth import bcrypt, auth
from algorithms import algorithms
from admin import admin, UPLOAD_FOLDER
from models import db, User, Dataset, Model
from secret import SECRET_KEY

app = Flask(__name__)
app.register_blueprint(auth)
app.register_blueprint(admin)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = SECRET_KEY
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 160 * 1000 * 1000

migrate = Migrate(app, db)
csrf = CSRFProtect(app)
bcrypt.init_app(app)
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return db.one_or_404(db.select(User).filter_by(id = user_id))

with app.app_context():
    db.create_all()

@app.route("/")
def index():
    return render_template("index.html")

@app.get("/dashboard")
@login_required
def dashboard():
    if current_user.role != "customer":
        return redirect(url_for("auth.logout"))
    else:
        return render_template('dashboard.html')

@app.get("/dashboard/model")
@login_required
def model():
    if current_user.role != "customer":
        return redirect(url_for("auth.logout"))
    else:
        model_list = db.session.query(Model).filter_by(user_id = current_user.id).order_by(Model.date_created).all()
        return render_template('model.html', model_list = model_list, algorithms = algorithms)
    
@app.route("/dashboard/model/new", methods=['GET', 'POST'])
@login_required
def model_new():
    if current_user.role != "customer":
        return redirect(url_for("auth.logout"))
    else:
        if request.method == "POST":
            name = request.form['name']
            dataset = request.form['dataset']
            algorithm = request.form['algorithm']
            new_model = Model(user_id = current_user.id, dataset_id = dataset, algorithm_id = algorithm, name = name)
            db.session.add(new_model)
            db.session.commit()
            return redirect(url_for("model"))
        else:
            dataset_list = db.session.query(Dataset).order_by(Dataset.date_created).all()
            return render_template('model_new.html', dataset_list = dataset_list, algorithms = algorithms)

@app.route("/dashboard/model/delete/<int:id>")
@login_required
def model_delete(id):
    if current_user.role != "customer":
        return redirect(url_for("auth.logout"))
    else:
        delete_data = db.one_or_404(db.select(Model).filter_by(id = id))
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], delete_data.filepath)
        if os.path.exists(filepath):
            db.session.delete(delete_data)
            db.session.commit()
            os.remove(filepath)
        return redirect(url_for("model"))

@app.get("/dashboard/model/train/parameter/<int:id>")
@login_required
def model_train_parameter(id):
    if current_user.role != "customer":
        return redirect(url_for("auth.logout"))
    else:
        model = db.session.query(Model).filter(Model.id == id).first()
        return render_template("model_train_parameter.html", model = model, algorithm = algorithms[model.algorithm_id])

@app.post("/dashboard/model/train/process")
@login_required
def model_train_process():
    model_id = request.form["model_id"]
    dataset_id = request.form["dataset_id"]
    algorithm_name = request.form["algorithm_name"]
    parameters = {
        "categorical" : {},
        "int" : {},
        "float" : {},
        "boolean" : {}
    }
    
    # Get algorithm_id manually because algorithm data doesn't exist yet in DB
    for key, val in algorithms.items():
        if val["name"] == algorithm_name:
            algorithm_id = key
            break
    
    # Input every available parameters
    for key in algorithms[algorithm_id]["parameters"]["categorical"].keys():
        if request.form[key] == "None":
            parameters['categorical'][key] = None
        else:
            parameters['categorical'][key] = request.form[key]
    for key in algorithms[algorithm_id]["parameters"]["int"].keys():
        if request.form[key] == "" or request.form[key] == None:
            parameters['int'][key] = None
        else:
            parameters['int'][key] = int(request.form[key])
    for key in algorithms[algorithm_id]["parameters"]["float"].keys():
        parameters['float'][key] = float(request.form[key])
    for key in algorithms[algorithm_id]["parameters"]["boolean"].keys():
        parameters['boolean'][key] = bool(request.form[key])
    
    #Convert old dict structure to new one by erasing 'type' keys (categorical, number, boolean)
    new_parameters = {}
    for key, val in parameters.items():
        for key2, val2 in val.items():
            new_parameters[key2] = val2
    
    #Generate new model
    from sklearn.svm import LinearSVC
    from sklearn.tree import DecisionTreeClassifier
    
    if algorithm_id == 1:
        new_model = DecisionTreeClassifier(**new_parameters)    
    elif algorithm_id == 2:
        new_model = LinearSVC(**new_parameters)    

    #Get csv file
    dataset = db.one_or_404(db.select(Dataset).filter_by(id = dataset_id))
    df = pd.read_csv(os.path.join(app.config['UPLOAD_FOLDER'] , dataset.filepath))

    #Splitting data
    X = df.drop(columns=[dataset.label_name])
    y = df[dataset.label_name]

    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=1)
    
    #Train Model
    trained_model = new_model.fit(X_train, y_train)
    
    #Check accuracy
    score = trained_model.score(X_test, y_test)
    
    #Generate model and parameter file
    pickle_parameter = pickle.dumps(parameters, pickle.HIGHEST_PROTOCOL)

    filename = "{}_{}_{}".format(model_id, dataset_id, algorithm_name)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], "model/", filename)
    with open(filepath, "wb") as f:
        pickle.dump(trained_model, f)
    
    #Save the data to DB
    model = db.one_or_404(db.select(Model).filter_by(id = model_id))
    model.status = True
    model.accuracy = score
    model.parameter = pickle_parameter
    model.filepath = os.path.join("model/", filename)
    db.session.commit()
    
    return redirect(url_for("model"))

@app.get("/dashboard/model/download/<int:id>")
def model_download(id):
    model = db.one_or_404(db.select(Model).filter_by(id = id))
    return send_from_directory(app.config["UPLOAD_FOLDER"], model.filepath)

if __name__ == "__main__":
    app.run(debug=True)