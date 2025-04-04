from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import db, Dataset
from algorithms import algorithms
import os
import pandas as pd

UPLOAD_FOLDER = 'static/upload/'
ALLOWED_EXTENSIONS = {'csv', 'xlsx'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


admin = Blueprint('admin', __name__)

@admin.get("/admin")
@login_required
def index():
    if current_user.role != "admin":
        return redirect(url_for('auth.logout'))
    else:
        dataset_list = db.session.query(Dataset).order_by(Dataset.date_created).all()
        return render_template("/admin/index.html", dataset_list = dataset_list, algorithms_dict = algorithms)
    
@admin.route("/admin/dataset", methods=['GET', 'POST'])
@login_required
def dataset():
    if current_user.role != "admin":
        return redirect(url_for("auth.logout"))
    else:
        if request.method == "POST":
            # Check if the post request has the file part
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)
            file = request.files['file']
            # If the user does not select a file, the browser submits an 
            # empty file without a filename.
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            # Checking the file extension
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                name = request.form['name']
                type = request.form['type']
                label_name = request.form['label_name']
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'],"dataset/" ,filename)
                file.save(filepath)
                new_dataset = Dataset(name = name, type = type, label_name = label_name, filepath = os.path.join("dataset/", filename))
                db.session.add(new_dataset)
                db.session.commit()
                return redirect(url_for("admin.dataset"))
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
    return render_template("admin/algorithm.html", algorithms_dict = algorithms)