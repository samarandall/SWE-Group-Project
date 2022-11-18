import os
from flask import Flask, url_for, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
#login information
from flask_login import LoginManager, UserMixin
from flask_login import logout_user, login_user, login_required, current_user
# used to create form objects such as the search bar
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import length, InputRequired, ValidationError
# used for hashing/encrypting password
from flask_bcrypt import Bcrypt


app = Flask(__name__)

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

# database declaration / login declaration
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

database = SQLAlchemy(app)

@login_manager.user_loader
def load_user(user_id):
    """used by login manager to load user based on their id"""
    return Person.query.get(int(user_id))

class RegisterForm(FlaskForm):
    user_email = StringField(validators=[InputRequired(), length(min=3, max=30)], render_kw={"placeholder": "Your Email"})
    user_password = PasswordField(validators=[InputRequired(), length(min=9, max=30)], render_kw={"placeholder": "Password"})
    submit = SubmitField("Register User")

class LoginForm(FlaskForm):
    user_email = StringField(validators=[InputRequired(), length(min=3, max=30)], render_kw={"placeholder": "Your Email"})
    user_password = PasswordField(validators=[InputRequired(), length(min=9, max=30)], render_kw={"placeholder": "Password"})
    submit = SubmitField("Login User")

    #to do: how to validate if something is an email? What requires a string to be an email
    def validate_email(self, email):
        """Function used by Loginform that checks to see if the email is valid and
        that the email exists in our database
        Parameters: (email entered by user)
        Returns: Validation Error"""
        existing_email = Person.query.filter_by(email=email.data).first()
        if not existing_email:
            raise ValidationError("This email is not in our records. Please sign up with your email.")

class Person(database.Model, UserMixin):
    '''Person class that will be used to store the email and password information'''
    id = database.Column(database.Integer, primary_key=True)
    email = database.Column(database.String(30), unique=True, nullable=False)
    hashed_password = database.Column(database.String(30), nullable=False)

# database creation
with app.app_context():
    database.create_all()


# app routes
#base route
@app.route("/")
def home():
    return

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():


    return render_template("register.html", form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user_email = Person.query.filter_by(email=form.username.data).first()
        if user_email:
            login_user(user_email)
            return redirect(url_for("route function here"))
    return render_template("login.html", form=form)

@login_manager.unauthorized_handler
def unauthorized_callback():
    """function to handle attempted unauthorized access, will redirect
    to homepage
    Parameters(none)
    Returns: redirect to home ie '/' route"""
    return redirect(url_for("home"))

