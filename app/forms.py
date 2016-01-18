from flask.ext.wtf import Form
from wtforms import StringField, BooleanField, TextAreaField, SubmitField, SelectField, PasswordField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Optional
from flask.ext.babel import gettext
from app.models import User, Role

class LoginForm(Form):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

class RegisterForm(Form):
    username = StringField(
        'username',
        validators=[DataRequired(), Length(min=3, max=25)])
    email = StringField(
        'email',
        validators=[Optional(),Email(message=None), Length(min=0, max=40)])
    password = PasswordField(
        'password',
        validators=[DataRequired(), Length(min=6, max=25)])
    confirm = PasswordField(
        'Repeat password',
        validators=[DataRequired(), EqualTo('password', message='Passwords must match.')])

    def validate(self):
        initial_validation = super(RegisterForm, self).validate()
        if not initial_validation:
            return False
        user = User.query.filter_by(username=self.username.data).first()
        if user:
            self.username.errors.append("Username is already used.")
            return False
        return True

class UpdateForm(Form):
    username = StringField(
        'username',
        validators=[DataRequired(), Length(min=3, max=25)])

class ChangePasswordForm(Form):
    password = PasswordField(
        'password',
        validators=[DataRequired(), Length(min=6, max=25)])
    confirm = PasswordField(
        'Repeat password',
        validators=[
            DataRequired(),
            EqualTo('password', message='Passwords must match.')])

class ServiceLoginForm(Form):
    openid = StringField('openid', validators=[DataRequired()])
    remember_me = BooleanField('remember_me', default=False)

class EditForm(Form):
    username = StringField('username', validators=[DataRequired()])
    about_me = TextAreaField('about_me', validators=[Length(min=0, max=140)])

    def __init__(self, original_username, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.original_username = original_username

    def validate(self):
        if not Form.validate(self):
            return False
        if self.username.data == self.original_username:
            return True
        if self.username.data != User.make_valid_username(self.username.data):
            self.username.errors.append(gettext('This username has invalid characters. Please use letters, numbers, dots and underscores only.'))
            return False
        user = User.query.filter_by(username=self.username.data).first()
        if user is not None:
            self.username.errors.append(gettext('This username is already in use. Please choose another one.'))
            return False
        return True

class EditFormAdmin(Form):
    username = StringField('username', validators=[DataRequired()])
    about_me = TextAreaField('about_me', validators=[Length(min=0, max=140)])
    role = SelectField('Role', coerce=int)
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super(EditFormAdmin, self).__init__(*args, **kwargs)
        self.original_username = user.username
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate(self):
        if not Form.validate(self):
            return False
        if self.username.data == self.original_username:
            return True
        if self.username.data != User.make_valid_username(self.username.data):
            self.username.errors.append(gettext('This username has invalid characters. Please use letters, numbers, dots and underscores only.'))
            return False
        user = User.query.filter_by(username=self.username.data).first()
        if user is not None:
            self.username.errors.append(gettext('This username is already in use. Please choose another one.'))
            return False
        return True

class PostForm(Form):
    title = StringField('title', validators=[DataRequired()])
    body = StringField('body', validators=[DataRequired()])

class SearchForm(Form):
    search = StringField('search', validators=[DataRequired()])

class CommentForm(Form):
    body = StringField('Enter your comment', validators=[DataRequired()])
    submit = SubmitField('Submit')

class ReplyForm(Form):
    body = StringField('Enter your comment', validators=[DataRequired()])
    submit = SubmitField('Submit')