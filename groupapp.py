'''Main APP file, instantiates the app, database, encryptor, as
well as contains the definitions for the table models and the
flask forms documentation'''

import os
from flask import Flask, url_for, redirect, render_template
import flask
from flask_sqlalchemy import SQLAlchemy
# login information
from flask_login import LoginManager, UserMixin
from flask_login import logout_user, login_user, login_required, current_user
# used to create form objects such as the search bar
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import length, InputRequired, ValidationError
# used for hashing/encrypting password
from flask_bcrypt import Bcrypt
import api

app = Flask(__name__)

# bcrypt object is utilized in password hashing/encryption
bcrypt = Bcrypt(app)

# fetches session key and Database URI from .env file
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("SQLALCHEMY_DATABASE_URI")

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
    """Class that will be utilized by register.html to create the user entry field
    objects that will transfer the data"""

    user_email = StringField(
        validators=[InputRequired(), length(min=3, max=30)],
        render_kw={"placeholder": "Your Email"},
    )
    user_password = PasswordField(
        validators=[InputRequired(), length(min=9, max=30)],
        render_kw={"placeholder": "Password"},
    )
    submit = SubmitField("Register User")


class LoginForm(FlaskForm):
    """Class that will be utilized by login.html to create the user entry field
    objects that will transfer the data"""

    user_email = StringField(
        validators=[InputRequired(), length(min=3, max=30)],
        render_kw={"placeholder": "Your Email"},
    )
    user_password = PasswordField(
        validators=[InputRequired(), length(min=9, max=30)],
        render_kw={"placeholder": "Password"},
    )
    submit = SubmitField("Login User")

    # to do: how to validate if something is an email? What requires a string to be an email
    def validate_email(self, email):
        """Function used by Loginform that checks to see if the email is valid and
        that the email exists in our database
        Parameters: (email entered by user)
        Returns: Validation Error"""
        existing_email = Person.query.filter_by(email=email.data).first()
        if not existing_email:
            raise ValidationError(
                "This email is not in our records. Please sign up with your email."
            )


class Person(database.Model, UserMixin):
    """Person class that will be used to store the email and password information"""

    id = database.Column(database.Integer, primary_key=True)
    email = database.Column(database.String(30), unique=True, nullable=False)
    hashed_password = database.Column(database.String(30), nullable=False)


# database creation
with app.app_context():
    database.create_all()


# app routes
# base route - NEEDS TO BE BUILT
@app.route("/")
def index():
    """DOCSTRING TEMPLATE HOLDER"""
    #needs to return a base render_template to a .html file
    if current_user.is_authenticated:
        return flask.redirect(flask.url_for('home'))
    return flask.redirect(flask.url_for('login'))

@app.route("/home")
#@login_required
def home():
    '''call api, give things to template'''
    return flask.render_template('home.html')

@app.route('/display')
@app.route('/display/<meal_id>')
#@login_required
def display(meal_id=None): #reroute to display
    if meal_id is None:
        random_meal = api.get_random_meal()
        return flask.render_template(
            'display.html',
            name=random_meal[0], 
            category=random_meal[1], 
            instructions=random_meal[2], 
            ingredients=random_meal[3], 
            id=random_meal[4]
        )
    else:
        specific_meal = api.get_meal(meal_id)
        return flask.render_template(
            'display.html',
            name=specific_meal[0], 
            category=specific_meal[1], 
            instructions=specific_meal[2], 
            ingredients=specific_meal[3], 
            id=specific_meal[4]
        )

@app.route("save_recipe", methods=["POST"])
def save_recipe():
    movie_id = flask.request.form
    return

@app.route("/user_saved_recipes")
#@login_required
def user_saved_recipes():
    return "user_saved_recipes"

@app.route("/register", methods=["GET", "POST"])
def register():
    """DOCSTRING TEMPLATE HOLDER"""
    form = RegisterForm()
    if form.validate_on_submit():
        # generates a hashed password based on created bcrypt object
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        # adds user to database and commits them
        new_user = Person(
            email=form.user_email.data, hashed_password=hashed_password.data
        )
        database.session.add(new_user)
        database.session.commit()
        # redirects to login
        return redirect(url_for("login"))
    # renders path page based on .html form (need to set up)
    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    """loads login form and querys the database to search for valid user based
    on email,if valid, the password from the form is compared to the hashed
    password of the database and if those match then the user is taken to main.
    Parameters: (none)
    Returns: redirects to either movieinfo or login"""
    form = LoginForm()
    if form.validate_on_submit():
        user = Person.query.filter_by(email=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.hashed_password, form.user_password.data):
                login_user(user)
                return redirect(url_for("main"))
    return render_template("login.html", form=form)


@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    """logs out user from app and redirects app to login screen
    reauthentication
    Parameters: (none)
    Returns: redirect to login"""
    logout_user()
    return redirect(url_for("user_login"))


@app.route("/main", methods=["Get", "POST"])
@login_required
def main():
    """DOCSTRING TEMPLATE HOLDER"""
    return render_template("mainpage.html")


@login_manager.unauthorized_handler
def unauthorized_callback():
    """function to handle attempted unauthorized access, will redirect
    to homepage
    Parameters(none)
    Returns: redirect to home ie '/' route"""
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)