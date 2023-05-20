import os
from MakeLog import MakeLog
from flask import Flask, render_template, flash, request, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash

HOME = os.path.expanduser("~")
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# create the extension
db = SQLAlchemy()
# for migrate
migrate = Migrate()
# create the flask instance
app = Flask(__name__)
# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///' + os.path.join(BASE_DIR, 'test.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# initialize the app with the extension
db.init_app(app)
# migration
migrate.init_app(app, db)

# Environment and Debug Features
# secret key
app.config['SECRET_KEY'] = "SECRET_KEY"
# Setting FLASK_ENV to development will enable debug mode
app.config['FLASK_ENV'] = 'development'
# name main flask file
app.config['FLASK_APP'] = 'app.py'

m_log = MakeLog.logger

# db create
with app.app_context():
    db.create_all()



# create a route decorator
@app.route('/')
# https://jinja.palletsprojects.com/en/3.1.x/templates/#list-of-builtin-filters
# upper - все большими
# lower - все маленькими
# capitalize - первая буква большая
# safe - сохраняет html теги
# striptags - удаляет html теги
# title - все будут с большой буквы
# trim - удаляет пробелы в начале и в конце строки
def index():
    m_log.info("open /")
    first_name = "John"
    stuff = "This is <strong>Bold</strong> text"

    favorite_pizza = ["pepperoni", "cheese", "mushhrooms", 41]
    return render_template("index.html",
                           first_name=first_name,
                           stuff=stuff,
                           favorite_pizza=favorite_pizza)

# localhost:5000/user/John
@app.route('/user/<name>')
def user(name):
    # https://jinja.palletsprojects.com/en/3.1.x/templates/#filters
    # https://jinja.palletsprojects.com/en/3.1.x/templates/#id11
    m_log.info("open /user")
    return  render_template("user.html", user_name=name)

# обработка ошибок
@app.errorhandler(404)
def page_not_found(e):
    return render_template("error_404.html"), 404


@app.errorhandler(500)
def server_die(e):
    return render_template("error_500.html"), 500


if __name__ == '__main__':
    m_log.info("start server")
    # app.run(host='0.0.0.0', port="5000", ssl_context='adhoc', threaded=True, debug=True)
    app.run(debug=True)
    m_log.info("stop server")
