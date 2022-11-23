"""Main APP file, instantiates the app, database, encryptor, as
well as contains the definitions for the table models and the
flask forms documentation"""

import os
from flask import Flask, url_for, redirect, render_template
import flask
from flask_sqlalchemy import SQLAlchemy

# login information
from flask_login import LoginManager, UserMixin
from flask_login import logout_user, login_user, login_required, current_user

# used to create form objects such as the search bar
from flask_wtf import FlaskForm
from wtforms import EmailField, SubmitField, PasswordField
from wtforms.validators import email, length, InputRequired, ValidationError

# used for hashing/encrypting password
from flask_bcrypt import Bcrypt
import api

app = Flask(__name__)

# bcrypt object is utilized in password hashing/encryption
bcrypt = Bcrypt(app)

# fetches session key and Database URI from .env file
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")

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
        validators=[
            InputRequired(),
            email(
                message="Invalid. Please enter a valid email", allow_empty_local=True
            ),
            length(min=3, max=30),
        ],
        render_kw={"placeholder": "Your Email"},
    )
    user_password = PasswordField(
        validators=[InputRequired(), length(min=9, max=30)],
        render_kw={"placeholder": "Password"},
    )
    submit = SubmitField("Register User")

    def validate_user_email(self, user_email):
        """function used in Registration form to determine if the user email
        pre-exists raising an error
        Parameters: (string-user email)
        Returns: Error"""
        existing_user = Person.query.filter_by(email=user_email.data).first()
        if existing_user:
            raise ValidationError(
                "Email already on file, please login via the link below or register a different one."
            )


class LoginForm(FlaskForm):
    """Class that will be utilized by login.html to create the user entry field
    objects that will transfer the data"""

    user_email = EmailField(
        "Email",
        validators=[
            InputRequired("Please enter your email here"),
            email(
                message="Invalid. Please enter a valid email", allow_empty_local=True
            ),
            length(min=3, max=30),
        ],
        render_kw={"placeholder": "Your Email"},
    )

    user_password = PasswordField(
        "Password",
        validators=[
            InputRequired("Please enter your password here"),
            length(min=9, max=30),
        ],
        render_kw={"placeholder": "Password"},
    )
    submit = SubmitField("Login User")

    # to do: how to validate if something is an email? What requires a string to be an email
    def validate_user_email(self, user_email):
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
    email = database.Column(database.String(30), unique=True, nullable=False)
    hashed_password = database.Column(
        database.LargeBinary(60), unique=False, nullable=False
    )


class UserRecipes(database.Model):
    """User based Recipes that are saved to be accessed to the user"""

    id = database.Column(database.Integer, primary_key=True)
    recipe_id = database.Column(database.Integer, unique=False, nullable=False)
    # foreign key to link recipes to person(user)
    # maybe add more stuff to database?
    user_id = database.Column(
        database.Integer,
        # database.ForeignKey("person.id"),
        unique=False,
        nullable=False,
    )


# database creation
with app.app_context():
    database.create_all()


# app routes
@app.route("/")
def title():
    """renders a base page that allows user to be redirected to login or signup
    Parameters: (none)
    Returns: html file for display"""
    return render_template("title.html")


@app.route("/display")
@app.route("/display/<meal_id>")
@login_required
def display(meal_id=None):
    """This route displayes either a random or given meal"""
    user = current_user.email
    if meal_id is None:
        meal = api.get_random_meal()
    else:
        meal = api.get_meal(meal_id)
    return flask.render_template(
        "display.html",
        name=meal[0],
        category=meal[1],
        instructions=meal[2],
        ingredients=meal[3],
        id=meal[4],
        img=meal[5],
        user=user,
    )


@app.route("/handle_display", methods=["POST"])
@login_required
def handle_display():
    """this route handles a display reroute"""
    form_data = flask.request.form
    recipe_id = form_data["recipe_id"]
    return flask.redirect(f"/display/{recipe_id}")


@app.route("/save_recipe", methods=["POST"])
@login_required
def save_recipe():
    """this route handles when the user wants to save a recipe and adds it to the database"""
    form_data = flask.request.form
    recipe_id = form_data["recipe_id"]
    id = current_user.id
    save_recipe = UserRecipes(recipe_id=recipe_id, user_id=current_user.id)
    database.session.add(save_recipe)
    database.session.commit()
    return flask.redirect(f"/display/{recipe_id}")


@app.route("/user_saved_recipes")
@login_required
def user_saved_recipes():
    """this route displayes the recipes a user has previously saved"""
    user = current_user.email
    recipes = UserRecipes.query.filter_by(user_id=current_user.id)
    recipes_list = []
    for recipe in recipes:
        recipes_list.append((recipe.recipe_id, api.get_meal_name(recipe.recipe_id)))
    return flask.render_template(
        "userSavedRecipes.html", recipes_list=recipes_list, user=user
    )


@app.route("/register", methods=["GET", "POST"])
def register():
    """this route allows a user to create a user and saves it the the database"""
    form = RegisterForm()
    if form.validate_on_submit():
        # generates a hashed password based on created bcrypt object
        bcrypt_hashed_password = bcrypt.generate_password_hash(form.user_password.data)
        new_user = Person(
            email=form.user_email.data, hashed_password=bcrypt_hashed_password
        )
        database.session.add(new_user)
        database.session.commit()
        # redirects to login
        return redirect(url_for("title"))
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
    password_error = ""
    if form.validate_on_submit():
        user = Person.query.filter_by(email=form.user_email.data).first()
        if user:
            if bcrypt.check_password_hash(
                user.hashed_password, form.user_password.data
            ):
                login_user(user)
                return redirect(url_for("display"))
            else:
                password_error = "The password you have entered does not match"
    return render_template("login.html", error=password_error, form=form)


@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    """logs out user from app and redirects app to login screen
    reauthentication
    Parameters: (none)
    Returns: redirect to login"""
    logout_user()
    return redirect(url_for("login"))


@login_manager.unauthorized_handler
def unauthorized_callback():
    """function to handle attempted unauthorized access, will redirect
    to homepage
    Parameters(none)
    Returns: redirect to beginning route ie '/' route"""
    return redirect(url_for("title"))


if __name__ == "__main__":
    app.run(debug=True)
