# for user registration and login

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField, FloatField, IntegerField
from wtforms.fields import DateField, TimeField  # Add this import
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.models import User


class RegistrationForm(FlaskForm):
    name = StringField('Full Name', validators=[
                       DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[
                        DataRequired(), Length(min=10, max=15)])
    role = SelectField(
        'Role', choices=[('attendee', 'Attendee'), ('organizer', 'Organizer'), ('admin', 'Admin')])
    password = PasswordField('Password', validators=[
                             DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError(
                'Email already registered. Please use a different email.')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = SelectField('Remember Me', choices=[
                           ('no', 'No'), ('yes', 'Yes')])
    submit = SubmitField('Login')


class EventForm(FlaskForm):
    title = StringField('Event Title', validators=[
                        DataRequired(), Length(max=200)])
    description = TextAreaField('Description', validators=[DataRequired()])
    date = DateField('Date', format='%Y-%m-%d', validators=[DataRequired()])
    time = TimeField('Time', format='%H:%M', validators=[DataRequired()])
    location = StringField('Location', validators=[
                           DataRequired(), Length(max=200)])
    address = StringField('Full Address', validators=[Length(max=300)])
    category = SelectField('Category', choices=[
        ('concert', 'Concert'),
        ('conference', 'Conference'),
        ('workshop', 'Workshop'),
        ('sports', 'Sports'),
        ('festival', 'Festival'),
        ('other', 'Other')
    ])  # Changed } to ]
    price = FloatField('Price per Ticket', default=0.0)
    capacity = IntegerField('Total Capacity', default=100)
    submit = SubmitField('Create Event')


class ProfileEditForm(FlaskForm):
    name = StringField('Full Name', validators=[
                       DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[
                        DataRequired(), Length(min=10, max=15)])
    submit = SubmitField('Update Profile')

    def __init__(self, original_email, *args, **kwargs):
        super(ProfileEditForm, self).__init__(*args, **kwargs)
        self.original_email = original_email

    def validate_email(self, email):
        if email.data != self.original_email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError(
                    'Email already registered. Please use a different email.')
