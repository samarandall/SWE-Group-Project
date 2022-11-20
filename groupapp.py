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
from wtforms import EmailField, StringField, SubmitField, PasswordField
from wtforms.validators import email, length, InputRequired, ValidationError
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

    user_email = EmailField(
        validators=[InputRequired(), email(message="Invalid. Please enter a valid email", allow_empty_local=True),length(min=3, max=30)],
        render_kw={"placeholder": "Your Email"},
    )
    user_password = PasswordField(
        validators=[InputRequired(), length(min=9, max=30)],
        render_kw={"placeholder": "Password"},
    )
    username = StringField( "Username",
        validators=[InputRequired(), length(min=3, max=30)],
        render_kw={"placeholder": "Your Username"},
    )
    submit = SubmitField("Register User")

    def validate_email(self, user_email):
        """function used in Registration form to determine if the username
        pre-exists raising an error
        Parameters: (string-username)
        Returns: Error"""
        existing_user = Person.query.filter_by(email=user_email.data).first()
        if existing_user:
            raise ValidationError(
                "Email already on file, please login via link or register a different one."
            )


class LoginForm(FlaskForm):
    """Class that will be utilized by login.html to create the user entry field
    objects that will transfer the data"""

    user_email = EmailField( "Email",
        validators=[InputRequired("Please enter your email here"), email(message="Invalid. Please enter a valid email", allow_empty_local=True), length(min=3, max=30)],
        render_kw={"placeholder": "Your Email"},
    )

    user_password = PasswordField( "Password",
        validators=[InputRequired("Please enter your password here"), length(min=9, max=30)],
        render_kw={"placeholder": "Password"},
    )
    submit = SubmitField("Login User")

    # to do: how to validate if something is an email? What requires a string to be an email
    def validate_email(self, user_email):
        """Function used by Loginform that checks to see if the email is valid and
        that the email exists in our database
        Parameters: (email entered by user)
        Returns: Validation Error"""
        existing_email = Person.query.filter_by(email=user_email.data).first()
        if not existing_email:
            raise ValidationError(
                "This email is not in our records. Please sign up with your email."
            )


class Person(database.Model, UserMixin):
    """Person class that will be used to store the email and password information"""

    id = database.Column(database.Integer, primary_key=True)
    username = database.Column(database.String(30), unique=True, nullable=False)
    email = database.Column(database.String(30), unique=True, nullable=False)
    hashed_password = database.Column(database.String(), nullable=False)

class UserRecipes(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    recipe_id = database.Column(database.Integer, unique=False, nullable=False)
    email = database.Column(database.String(30), unique=False, nullable=False)

# database creation
with app.app_context():
    database.create_all()


# app routes
# base route - NEEDS TO BE BUILT
@app.route("/")
def title():
    """renders a base page that allows user to be redirected to login or signup
    Parameters: (none)
    Returns: html file for display"""
    return render_template("title.html")

@app.route("/home")
#@login_required
def home():
    '''render the home template'''
    return flask.render_template('home.html')

@app.route('/display')
@app.route('/display/<meal_id>')
#@login_required
def display(meal_id=None): #reroute to display
    if meal_id is None:
        meal = api.get_random_meal()
    else:
        meal = api.get_meal(meal_id)
    return flask.render_template(
        'display.html',
        name=meal[0],
        category=meal[1],
        instructions=meal[2],
        ingredients=meal[3],
        id=meal[4]
    )

@app.route("/save_recipe", methods=["POST"])
#@login_required
def save_recipe():
    form_data = flask.request.form
    recipe_id = form_data['recipe_id']
    email = current_user.email
    save_recipe = UserRecipes(recipe_id=recipe_id,email=email)
    database.session.add(save_recipe)
    database.session.commit()
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
        bcrypt_hashed_password = bcrypt.generate_password_hash(form.user_password.data)
        new_user = Person(
            email=form.user_email.data, hashed_password=bcrypt_hashed_password, username=form.username.data)
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
