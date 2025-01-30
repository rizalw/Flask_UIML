from flask import Flask, render_template, url_for, redirect, request
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from flask_bcrypt import Bcrypt
from wtforms.validators import ValidationError
from models import db, User, Algorithm, Dataset
from forms import RegisterForm, LoginForm

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'VT-qEOniyKzogQFKeWpPqQ'

db.init_app(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()
    
@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        existing_user_username = User.query.filter_by(username=form.username.data).first()
        if existing_user_username:
            raise ValidationError("The username already exists. Please choose a different one.")
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password, role ="Customer")
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    elif request.method == "POST":
        return redirect(url_for('register'))
    else:
        return render_template("customer/register.html", form = form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == "POST":
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user:
                if bcrypt.check_password_hash(user.password, form.password.data):
                    login_user(user)
                    return redirect(url_for('dashboard'))
    else:
        return render_template("customer/login.html", form = form)

@app.get("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route("/admin", methods=['GET', 'POST'])
def admin():
    form = LoginForm()
    if form.validate_on_submit():
        admin = User.query.filter_by(username=form.username.data).first()
        if admin:
            if bcrypt.check_password_hash(admin.password, form.password.data):
                login_user(admin)
                return redirect(url_for('dashboard_admin'))
        else:
            raise ValidationError("The account do not exist.")
    else:
        return render_template("admin/admin.html", form = form)

@app.route("/register_admin", methods=['GET', 'POST'])
def register_admin():
    form = RegisterForm()
    if form.validate_on_submit():
        existing_user_username = User.query.filter_by(username=form.username.data).first()
        if existing_user_username:
            raise ValidationError("The username already exists. Please choose a  different one.")
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password, role="Admin")
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('admin'))
    elif request.method == "POST":
        return redirect(url_for('register_admin'))
    else:
        return render_template("admin/register_admin.html", form = form)

@app.get("/")
def index():
    return render_template("customer/home.html")

@app.get("/dashboard")
@login_required
def dashboard():
    return render_template("customer/dashboard.html")

@app.get('/model_creation')
@login_required
def model_creation():
    algorithm_list = Algorithm.query.all()
    return render_template('customer/model_creation.html', algorithm_list = algorithm_list)

@app.get("/dashboard_admin")
@login_required
def dashboard_admin():
    if current_user.role == "Admin":
        return render_template("admin/dashboard_admin.html")
    else:
        return redirect(url_for("dashboard"))

@app.route("/algorithm_data", methods=['GET', 'POST'])
@login_required
def algorithm_data():
    if request.method == "POST":
        algorithm_name = request.form.get("name")
        algorithm_type = ",".join(request.form.getlist("type"))
        new_algorithm = Algorithm(name=algorithm_name, methods=algorithm_type)
        db.session.add(new_algorithm)
        db.session.commit()
        return redirect(url_for('algorithm_data'))
    else:
        algorithm_list = Algorithm.query.order_by(Algorithm.id).all()
        return render_template("admin/algorithm_data.html", algorithm_list = algorithm_list)
    
@app.route("/algorithm_data/update/<int:id>", methods=['GET', 'POST'])
@login_required
def update_algorithm_data(id):
    if request.method == "POST":
        algorithm_id = request.form.get("algorithm_id")
        algorithm_name = request.form.get("algorithm_name")
        algorithm_data = Algorithm.query.filter_by(id=algorithm_id).first()
        algorithm_data.name = algorithm_name
        db.session.commit()
        return redirect(url_for('algorithm_data'))
    else:
        algorithm_data = Algorithm.query.get_or_404(id)
        return render_template("admin/algorithm_data_update.html", algorithm_data = algorithm_data)

@app.get("/algorithm_data/delete/<int:id>")
@login_required
def delete_algorithm_data(id):
    delete_data = Algorithm.query.get_or_404(id)
    db.session.delete(delete_data)
    db.session.commit()
    return redirect(url_for('algorithm_data'))

@app.route("/dataset_data", methods=['GET', 'POST'])
@login_required
def dataset_data():
    if request.method == "POST":
        dataset_name = request.form.get("dataset_name")
        new_dataset = Dataset(name=dataset_name)
        db.session.add(new_dataset)
        db.session.commit()
        return redirect(url_for('dataset_data'))
    else:
        dataset_list = Dataset.query.order_by(Dataset.id).all()
        return render_template("admin/dataset_data.html", dataset_list = dataset_list)
    
@app.route("/dataset_data/update/<int:id>", methods=['GET', 'POST'])
@login_required
def update_dataset_data(id):
    if request.method == "POST":
        dataset_id = request.form.get("dataset_id")
        dataset_name = request.form.get("dataset_name")
        dataset_data = Dataset.query.filter_by(id=dataset_id).first()
        dataset_data.name = dataset_name
        db.session.commit()
        return redirect(url_for('dataset_data'))
    else:
        dataset_data = Dataset.query.get_or_404(id)
        return render_template("admin/dataset_data_update.html", dataset_data = dataset_data)
    

@app.get("/dataset_data/delete/<int:id>")
@login_required
def delete_dataset_data(id):
    delete_data = Dataset.query.get_or_404(id)
    db.session.delete(delete_data)
    db.session.commit()
    return redirect(url_for('dataset_data'))

if __name__ == "__main__":
    app.run(debug=True)