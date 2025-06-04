# artproject/app/features/login/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo

class LoginForm(FlaskForm):
    email = StringField('Email Address', 
                        validators=[DataRequired(message="Email is required."), 
                                    Email(message="Invalid email address.")])
    password = PasswordField('Password', 
                             validators=[DataRequired(message="Password is required.")])
    submit = SubmitField('Login')
