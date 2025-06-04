# artproject/app/features/account/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Regexp
from app.models.account import Account # To check if email already exists

class RegistrationForm(FlaskForm):
    name = StringField('Full Name',
                           validators=[DataRequired(message="Full name is required."),
                                       Length(min=2, max=100)])
    email = StringField('Email Address',
                        validators=[DataRequired(message="Email is required."),
                                    Email(message="Invalid email address.")])
    phoneNumber = StringField('Phone Number',
                              validators=[DataRequired(message="Phone number is required."),
                                          Regexp(r'^\+?1?\d{9,15}$', # Basic phone number regex
                                                 message="Invalid phone number format.")])
    password = PasswordField('Password',
                             validators=[DataRequired(message="Password is required."),
                                         Length(min=8, message="Password must be at least 8 characters long.")])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(message="Please confirm your password."),
                                                 EqualTo('password', message="Passwords must match.")])
    submit = SubmitField('Create Account')

    def validate_email(self, email_field):
        """ Custom validator to check if email already exists """
        if Account.get_by_email(email_field.data):
            raise ValueError('That email address is already registered. Please choose a different one or login.')
