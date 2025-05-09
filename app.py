from flask import Flask, flash, render_template, url_for, redirect, send_from_directory, send_file,request, session
from flask_migrate import Migrate
from flask_login import LoginManager, login_required, current_user
from flask_wtf.csrf import CSRFProtect

import os
import pandas as pd
import pickle
from io import BytesIO

from auth import bcrypt, auth
from algorithms import algorithms
from admin import admin, UPLOAD_FOLDER, ALLOWED_EXTENSIONS, allowed_file
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
login_manager.login_view = 'auth.login'

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
        model_list = db.session.query(Model).filter_by(user_id = current_user.id).order_by(Model.date_created).all()
        return render_template('dashboard.html', model_list = model_list, algorithms_dict = algorithms)

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
        try:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], delete_data.filepath)
        except:
            pass
        else:
            if os.path.exists(filepath):
                os.remove(filepath)
        finally:
            db.session.delete(delete_data)
            db.session.commit()
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
    if current_user.role != "customer":
        return redirect(url_for("auth.logout"))
    else:
        model_id = request.form["model_id"]
        dataset_id = request.form["dataset_id"]
        algorithm_id = int(request.form["algorithm_id"])
        algorithm_name = request.form["algorithm_name"]
        possible_parameter = ["categorical", "int", "float", "boolean"] # type: ignore
        parameters = {}
        
        # Input every available parameters 
        for param in possible_parameter:
            if param in algorithms[algorithm_id]["parameters"].keys():          
                for key in algorithms[algorithm_id]["parameters"][param].keys():
                    if param == "categorical":
                        if request.form[key] == "None":
                            parameters[key] = None
                        else:
                            parameters[key] = request.form[key]
                    elif param == "int":
                        if request.form[key] == "" or request.form[key] == None:
                            parameters[key] = None
                        else:
                            parameters[key] = int(request.form[key])
                    elif param == "float":
                        parameters[key] = float(request.form[key])
                    elif param == "boolean":
                        parameters[key] = bool(request.form[key])
        
        #Generate new model        
        if algorithm_id == 1:
            from sklearn.tree import DecisionTreeClassifier
            new_model = DecisionTreeClassifier(**parameters)    
        elif algorithm_id == 2:
            from sklearn.svm import LinearSVC
            new_model = LinearSVC(**parameters) 
        elif algorithm_id == 3:
            from sklearn.neighbors import KNeighborsClassifier
            new_model = KNeighborsClassifier(**parameters)

        #Get csv file
        dataset = db.one_or_404(db.select(Dataset).filter_by(id = dataset_id))
        df = pd.read_csv(os.path.join(app.config['UPLOAD_FOLDER'] , dataset.filepath))

        #Splitting data
        X = df.drop(columns=[dataset.label_name])
        y = df[dataset.label_name]

        test_size = float(request.form['test_size'])
        from sklearn.model_selection import train_test_split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=1)
        
        #Train Model
        trained_model = new_model.fit(X_train, y_train)
        
        #Check accuracy
        score = trained_model.score(X_test, y_test)
        
        #Generate model and parameter file
        pickle_parameter = pickle.dumps(parameters, pickle.HIGHEST_PROTOCOL)

        filename = "{}_{}_{}".format(model_id, dataset_id, algorithm_name)
        model_path = os.path.join(app.config['UPLOAD_FOLDER'], "model/")
        if not os.path.exists(model_path):
            os.mkdir(model_path)
        filepath = os.path.join(model_path, filename)
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

@app.route("/dashboard/model/predict/<int:id>", methods=['GET', 'POST'])
@login_required
def model_predict(id):
    if current_user.role != "customer":
        return redirect(url_for("auth.logout"))
    else:
        model = db.one_or_404(db.select(Model).filter_by(id = id))
        if request.method == "POST":
            pickle_file = os.path.join(app.config['UPLOAD_FOLDER'] , model.filepath)    
            
            with open(pickle_file, 'rb') as picklefile:
                model_pickle = pickle.load(picklefile)
            
            predict_data = {}
            predict_column = request.form["column_list"].split("-")
            for column_name in predict_column:
                predict_data[column_name] = float(request.form[column_name])
            
            result = model_pickle.predict([[ x for x in predict_data.values()]])
            flash("Model : {}".format(model.name))
            flash("Algorithm : {}".format(algorithms[model.algorithm_id]["name"]))
            flash("Output : {}".format(result[0]))
            return redirect(url_for("model"))
        else:
            label_name = model.dataset.label_name
            dataset_filepath = os.path.join(app.config['UPLOAD_FOLDER'] , model.dataset.filepath)
            df = pd.read_csv(dataset_filepath)
            column_list = df.columns.tolist()
            column_list.remove(label_name)
            value_example = df.iloc[0:3].drop(columns=[label_name]).values.tolist()
            return render_template("model_predict.html", column_list = column_list, value_example = value_example, id = id)

@app.post("/dashboard/model/predict/<int:id>/upload")
@login_required
def model_predict_csv(id):
    file = request.files['file']
    if file and allowed_file(file.filename):
        df = pd.read_csv(file)
        predict_column = df.columns.tolist()
        model = db.one_or_404(db.select(Model).filter_by(id = id))
        original_filepath = os.path.join(app.config['UPLOAD_FOLDER'], model.dataset.filepath)
        original_df = pd.read_csv(original_filepath)
        original_column = original_df.columns.tolist()
        original_column.remove(model.dataset.label_name)
        if original_column == predict_column:
            pickle_file = os.path.join(app.config['UPLOAD_FOLDER'] , model.filepath)    
            
            with open(pickle_file, 'rb') as picklefile:
                model_pickle = pickle.load(picklefile)
            
            result = model_pickle.predict(df)
            df[model.dataset.label_name] = result
            output = BytesIO()
            df.to_csv(output, index=False)
            output.seek(0)
            
            return send_file(output, mimetype="text/csv", download_name="result.csv", as_attachment=True)
        else:
            flash("The column from your file still not the sames as the required CSV structure")
            flash("Please update the file again after changing it")
        return redirect(url_for('model_predict', id = id)) 
    else:
        flash("This file extension is not supported. You need to upload csv file")
        flash("You need to upload csv file")
        return redirect(url_for('model_predict', id = id))

@app.get("/dashboard/model/download/<int:id>")
@login_required
def model_download(id):
    if current_user.role != "customer":
        return redirect(url_for("auth.logout"))
    else:
        model = db.one_or_404(db.select(Model).filter_by(id = id))
        return send_from_directory(app.config["UPLOAD_FOLDER"], model.filepath)

if __name__ == "__main__":
    app.run(debug=True)