# pip install flask-wtf
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from wtforms.widgets import TextArea
from flask_ckeditor import CKEditorField
from flask_wtf.file import  FileField

# create a form class
# https://flask.palletsprojects.com/en/2.2.x/patterns/wtforms/
# https://flask-wtf.readthedocs.io/en/1.0.x/api/#module-flask_wtf
# https://wtforms.readthedocs.io/en/3.0.x/fields/
class NameForm(FlaskForm):
    name = StringField("What is Your Name", validators=[DataRequired()])
    submit = SubmitField('Submit')


class PasswordForm(FlaskForm):
    email = StringField("What is Your Email", validators=[DataRequired()])
    password_hash = PasswordField("What is Your Password", validators=[DataRequired()])
    submit = SubmitField('Submit')

class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    favorite_color = StringField("Favorite Colore")
    about_author = TextAreaField("About Author")
    password_hash = PasswordField('Your password',
                                  validators=[DataRequired(), EqualTo('password_hash2', message='password must mach ')])
    password_hash2 = PasswordField('Confirm password', validators=[DataRequired()])
    profile_pic = FileField("Profile Pic")
    submit = SubmitField('Submit')


class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    # content = StringField("Content", validators=[DataRequired()], widget=TextArea())
    content = CKEditorField("Content", validators=[DataRequired()])
    author = StringField("Author")
    slug = StringField("Slug", validators=[DataRequired()])
    submit = SubmitField('Submit')


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField('Submit')

class SearchForm(FlaskForm):
    searched = StringField("Searched", validators=[DataRequired()])
    submit = SubmitField('Submit')