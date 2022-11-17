import os
from flask import Flask, url_for, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
#login information
from flask_login import LoginManager, UserMixin
from flask_login import logout_user, login_user, login_required, current_user
# used to create form objects such as the search bar
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, TextAreaField
from wtforms.validators import length, InputRequired, ValidationError, NumberRange

app = Flask(__name__)

# database declaration / login declaration
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

database = SQLAlchemy(app)

@login_manager.user_loader
def load_user(user_id):
    """used by login manager to load user based on their id"""
    return Person.query.get(int(user_id))

class Person(database.Model, UserMixin):
    '''Person class that will be used to store the email'''
    id = database.Column(database.Integer, primary_key=True)
    email = database.Column(database.String(30), unique=True, nullable=False)
    hashed_password = database.Column(database.String(20), unique=True, nullable=False)

# database creation
with app.app_context():
    database.create_all()


# app routes
#base route
@app.route("/")
def home():
    return

@login_manager.unauthorized_handler
def unauthorized_callback():
    """function to handle attempted unauthorized access, will redirect
    to homepage
    Parameters(none)
    Returns: redirect to home"""
    return redirect(url_for("home"))

