import os
from MakeLog import MakeLog
# pip install flask
from flask import Flask, render_template, flash, request, redirect, jsonify
# pip install flask-wtf
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from wtforms.widgets import TextArea
from datetime import datetime, date
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


# Create a Blog Post model
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(255), nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.now())
    slug = db.Column(db.String(255), nullable=False)


# Create Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    favorite_color = db.Column(db.String(100))
    date_added = db.Column(db.DateTime, default=datetime.now())
    # DO SOME user stuff
    password_hash = db.Column(db.String(100), nullable=False)

    @property
    def password(self):
        raise AttributeError('password not readable')

    @password.setter
    def password(self, p):
        self.password_hash = generate_password_hash(p)

    def verify_password(self, p):
        return check_password_hash(self.password_hash, p)

    def __init__(self, name, email, favorite_color, password_hash):
        self.name = name
        self.email = email
        self.favorite_color = favorite_color
        self.password_hash = password_hash

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
    password_hash = PasswordField('Your password',
                                  validators=[DataRequired(), EqualTo('password_hash2', message='password must mach ')])
    password_hash2 = PasswordField('Confirm password', validators=[DataRequired()])
    submit = SubmitField('Submit')


class PasswordForm(FlaskForm):
    email = StringField("What is Your Email", validators=[DataRequired()])
    password_hash = PasswordField("What is Your Password", validators=[DataRequired()])
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


# create password test page
@app.route('/test_pw', methods=["GET", "POST"])
def test_pw():
    m_log.info("open /test_pw")
    email = None
    password = None
    pw_to_check = None
    passed = None
    form = PasswordForm()
    # Validate Form
    if form.validate_on_submit():
        email = form.email.data
        password = form.password_hash.data
        form.email.data = ''
        form.password_hash.data = ''

        # look up user by email
        pw_to_check = User.query.filter_by(email=email).first()

        # check hashed password
        passed = check_password_hash(pw_to_check.password_hash, password)

        # flash('Form Submit Successfully!')
    return render_template("test_pw.html",
                           email=email,
                           password=password,
                           pw_to_check=pw_to_check,
                           passed=passed,
                           form=form)


@app.route('/user/add', methods=["GET", "POST"])
def add_user():
    m_log.info("open /user/add")
    name = None
    form = UserForm()
    # Validate Form
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first() is None:
            # hash password
            hashed_PW = generate_password_hash(form.password_hash.data, "sha256")
            user = User(name=form.name.data, email=form.email.data, favorite_color=form.favorite_color.data,
                        password_hash=hashed_PW)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.email.data = ''
        form.favorite_color.data = ''
        form.password_hash.data = ''
        form.password_hash2.data = ''
        flash('User Added Successfully!')
    our_users = User.query.order_by(User.date_added)
    return render_template("add_user.html",
                           name=name,
                           form=form,
                           our_users=our_users)


# Update DataBase Record
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


# Create Post Form
class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    content = StringField("Content", validators=[DataRequired()], widget=TextArea())
    author = StringField("Author", validators=[DataRequired()])
    slug = StringField("Slug", validators=[DataRequired()])
    submit = SubmitField('Submit')


# Add Posts Page
@app.route('/add_post', methods=["GET", "POST"])
def add_post():
    m_log.info(f"open /add-post")
    form = PostForm()

    if form.validate_on_submit():
        post = Posts(title=form.title.data, content=form.content.data, author=form.author.data, slug=form.slug.data)
        # clear the form
        form.title.data = ''
        form.content.data = ''
        form.author.data = ''
        form.slug.data = ''
        # add post to db
        db.session.add(post)
        db.session.commit()

        flash("Blog Post submit success")
    # Redirect to the wevpage
    return render_template("add_post.html", form=form)


# обработка ошибок
# Invalid URL
@app.errorhandler(404)
def page_not_found(e):
    return render_template("error_404.html"), 404


# Internal Server Error
@app.errorhandler(500)
def server_die(e):
    return render_template("error_500.html"), 500


# Json Thin
@app.route('/date')
def get_current_date():
    favorite_pizza = {
        "John": "Pepperoni",
        "Merry": "Cheese",
        "Tim": "Mushroom"
    }
    return jsonify(favorite_pizza)
    # return {"Date": date.today()}


if __name__ == '__main__':
    m_log.info("start server")
    # app.run(host='0.0.0.0', port="5000", ssl_context='adhoc', threaded=True, debug=True)
    app.run(debug=True)
    m_log.info("stop server")
