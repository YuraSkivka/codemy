import os
from MakeLog import MakeLog
# pip install flask
from flask import Flask, render_template, flash, request, redirect
# pip install flask-wtf
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from datetime import datetime
# pip install flask-sqlalchemy
from flask_sqlalchemy import SQLAlchemy
# pip install Flask-Migrate
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash

HOME = os.path.expanduser("~")
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
m_log = MakeLog.logger

# create the flask instance
# https://flask.palletsprojects.com/en/1.1.x/config/
app = Flask(__name__)
# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///' + os.path.join(BASE_DIR, 'flask.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# secret key, used like token in wtf
app.config['SECRET_KEY'] = "chang it in your project"
# Environment and Debug Features
# Setting FLASK_ENV to development will enable debug mode
app.config['FLASK_ENV'] = 'development'
# name main flask file
app.config['FLASK_APP'] = 'app.py'

# create the extension
db = SQLAlchemy()
# initialize the app with the extension
db.init_app(app)
# for migrate
migrate = Migrate()
# migration
migrate.init_app(app, db)


# Create Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    favorite_color = db.Column(db.String(100))
    date_added = db.Column(db.DateTime, default=datetime.now())

    def __init__(self, name, email, favorite_color):
        self.name = name
        self.email = email
        self.favorite_color = favorite_color

    # Create a String
    def __repr__(self):
        return '<Name %r>' % self.name

# db create
with app.app_context():
    db.create_all()


# create a form class
# https://flask.palletsprojects.com/en/2.2.x/patterns/wtforms/
# https://flask-wtf.readthedocs.io/en/1.0.x/api/#module-flask_wtf
# https://wtforms.readthedocs.io/en/3.0.x/fields/
class NameForm(FlaskForm):
    name = StringField("What is Your Name", validators=[DataRequired()])
    submit = SubmitField('Submit')

class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    favorite_color = StringField("Favorite Colore")
    submit = SubmitField('Submit')

# Bootstrap
# https://getbootstrap.com/docs/5.3/getting-started/introduction/
# https://getbootstrap.com/docs/5.3/components/navbar/

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
    m_log.info(f"open /user/{name}")
    return render_template("user.html", user_name=name)

# create name page
@app.route('/name', methods=["GET", "POST"])
def name():
    m_log.info("open /name")
    name = None
    form = NameForm()
    # Validate Form
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
        flash('Form Submit Successfully!')
    return render_template("name.html",
                           name=name,
                           form=form)

@app.route('/user/add', methods=["GET", "POST"])
def add_user():
    m_log.info("open /user/add")
    name = None
    form = UserForm()
    # Validate Form
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first() is None:
            user = User(name=form.name.data, email=form.email.data, favorite_color=form.favorite_color.data)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.email.data = ''
        form.favorite_color.data = ''
        flash('User Added Successfully!')
    our_users = User.query.order_by(User.date_added)
    return render_template("add_user.html",
                           name=name,
                           form=form,
                           our_users=our_users)


#Update DataBase Record
@app.route("/update/<int:id>", methods=["GET", "POST"])
def update(id):
    m_log.info(f"open /update/{id}")
    form = UserForm()
    user_to_update = User.query.get_or_404(id)
    if request.method == "POST":
        user_to_update.name = request.form['name']
        user_to_update.email = request.form['email']
        user_to_update.favorite_color = request.form['favorite_color']
        try:
            db.session.commit()
            flash('Form Update Successfully!')
            return render_template("update.html",
                                   form=form,
                                   user_to_update=user_to_update,
                                   id=id)
        except:
            flash('Form Update Error!')
            return render_template("update.html",
                                   form=form,
                                   user_to_update=user_to_update)

    else:
        return render_template("update.html",
                               form=form,
                               user_to_update=user_to_update,
                               id=id)


@app.route("/delete/<int:id>", methods=["GET", "POST"])
def delete(id):
    m_log.info(f"open /delete {id}")

    name = None
    user_to_delete = User.query.get_or_404(id)
    form = UserForm()
    try:
        db.session.delete(user_to_delete)
        db.session.commit()

        our_users = User.query.order_by(User.date_added)
        flash('Form Delete Successfully!')
        return render_template("add_user.html",
                               name=name,
                               form=form,
                               our_users=our_users)

    except:
        flash('Form Delete Error!')
        return render_template("add_user.html",
                               name=name,
                               form=form,
                               our_users=our_users)


# обработка ошибок
# Invalid URL
@app.errorhandler(404)
def page_not_found(e):
    return render_template("error_404.html"), 404

# Internal Server Error
@app.errorhandler(500)
def server_die(e):
    return render_template("error_500.html"), 500


if __name__ == '__main__':
    m_log.info("start server")
    # app.run(host='0.0.0.0', port="5000", ssl_context='adhoc', threaded=True, debug=True)
    app.run(debug=True)
    m_log.info("stop server")
