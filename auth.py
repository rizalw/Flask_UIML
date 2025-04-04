from flask import Blueprint, render_template, redirect, url_for, request
from flask_bcrypt import Bcrypt
from flask_login import login_user, login_required, logout_user
from models import db, User
from forms import RegisterForm, LoginForm

bcrypt = Bcrypt()

auth = Blueprint('auth', __name__)

@auth.route("/register", methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if request.method == "POST":
        if form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(form.password.data)
            new_user = User(username=form.username.data, password=hashed_password, role="customer")
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('auth.login'))
    else:
        return render_template("register.html", form = form)

@auth.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == "POST":
        if form.validate_on_submit():
            user = db.session.query(User).filter_by(username=form.username.data).first()
            # user = User.query.filter_by(username=form.username.data).first()
            if user:
                if bcrypt.check_password_hash(user.password, form.password.data):
                    login_user(user)
                    if user.role == "customer":
                        return redirect(url_for('dashboard'))
                    elif user.role == "admin":
                        return redirect(url_for("admin"))
                    else:
                        return redirect(url_for('logout'))
    else:
        return render_template("login.html", form = form)

@auth.get("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
