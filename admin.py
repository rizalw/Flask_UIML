from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import db, Dataset, Model
from algorithms import algorithms
import os
import pandas as pd

UPLOAD_FOLDER = 'static/upload/'
ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


admin = Blueprint('admin', __name__)

@admin.get("/admin")
def index():
    if current_user.role != "admin":
        return redirect(url_for('auth.logout'))
    else:
        dataset_list = db.session.query(Dataset).order_by(Dataset.date_created).all()
        model_list = db.session.query(Model).order_by(Model.date_created).all()
        return render_template("/admin/index.html", dataset_list = dataset_list, model_list = model_list,algorithms_dict = algorithms)
    
@admin.route("/admin/dataset", methods=['GET', 'POST'])
@login_required
def dataset():
    if current_user.role != "admin":
        return redirect(url_for("auth.logout"))
    else:
        if request.method == "POST":
            file = request.files['file']
            # Checking the file extension
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                name = request.form['name']
                type = request.form['type']
                label_name = request.form['label_name']
                dataset_path = os.path.join(current_app.config['UPLOAD_FOLDER'],"dataset/")
                if not os.path.exists(dataset_path):
                    os.mkdir(dataset_path)
                filepath = os.path.join(dataset_path,filename)
                file.save(filepath)
                new_dataset = Dataset(name = name, type = type, label_name = label_name, filepath = os.path.join("dataset/", filename))
                db.session.add(new_dataset)
                db.session.commit()
                return redirect(url_for("admin.dataset"))
            else:
                flash("The uploaded file extension is not supported")
                flash("The supported extension is csv")
                return redirect(request.url)
        else:
            dataset_list = db.session.query(Dataset).order_by(Dataset.date_created).all()
            return render_template("/admin/dataset.html", dataset_list = dataset_list)

@admin.get("/admin/dataset/<int:id>")
@login_required
def dataset_view(id):
    if current_user.role != "admin":
        return redirect(url_for("auth.logout"))
    else:
        dataset_data = db.one_or_404(db.select(Dataset).filter_by(id = id))
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], dataset_data.filepath)
        df = pd.read_csv(filepath)
        columns = df.columns.tolist()
        values = df.values.tolist()
        return render_template("/admin/dataset_detail.html", dataset_data = dataset_data, columns = columns, values = values)

@admin.get("/admin/dataset/delete/<int:id>")
@login_required
def dataset_delete(id):
    delete_data = db.one_or_404(db.select(Dataset).filter_by(id = id))
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], delete_data.filepath)
    if os.path.exists(filepath):
        db.session.delete(delete_data)
        db.session.commit()
        os.remove(filepath)
        return redirect(url_for("admin.dataset"))

@admin.get("/admin/algorithm")
@login_required
def algorithm():
    if current_user.role != "admin":
        return redirect(url_for('auth.logout'))
    else:
        return render_template("admin/algorithm.html", algorithms_dict = algorithms)

@admin.get("/admin/model")
@login_required
def model():
    if current_user.role != "admin":
        return redirect(url_for('auth.logout'))
    else:
        model_list = db.session.query(Model).order_by(Model.date_created).all()
        return render_template("/admin/model.html", model_list = model_list, algorithms_dict = algorithms)