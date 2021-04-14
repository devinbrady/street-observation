
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, PasswordField, TextField, IntegerField, DecimalField, BooleanField, RadioField, SubmitField
from wtforms.validators import DataRequired, Length, Email

from . import models


class LoginForm(FlaskForm):

    username = StringField('Username', render_kw={'class': 'form-control'})
    password = PasswordField('Password', render_kw={'class': 'form-control'})
    submit = SubmitField('Log In', render_kw={'class': 'btn btn-primary'})



class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()], render_kw={'class': 'form-control'})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={'class': 'form-control'})
    local_timezone = SelectField(
        'Local Timezone'
        , choices=['America/New_York', 'America/Chicago', 'America/Denver', 'America/Los_Angeles']
        , render_kw={'class': 'form-control'}
    )
    submit = SubmitField('Register', render_kw={'class': 'btn btn-primary'})

    def validate_username(self, username):
        user = models.User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')


class SessionSettingsForm(FlaskForm):
    """
    Form to collect information about a session
    """

    session_mode = RadioField(
        'Session Mode'
        , [DataRequired()]
        , choices=[
            'speed timer'
            # , 'speed radar'
            , 'counter'
            ]
        , render_kw={'class': 'form-check'}
    )

    speed_limit_value = IntegerField(
        'Speed Limit Value'
        , render_kw={'class': 'form-control'}
        )

    speed_units = SelectField(
        'Speed Units'
        , [DataRequired()]
        , choices=[
            'miles per hour'
            , 'kilometers per hour'
            , 'feet per second'
            , 'meters per second'
            ]
        , render_kw={'class': 'form-control'}
    )

    distance_value = DecimalField(
        'Distance'
        , places=None
        , render_kw={'class': 'form-control'}
        )

    distance_units = SelectField(
        'Distance Units'
        , [DataRequired()]
        , choices=['feet', 'miles', 'meters', 'kilometers']
        , render_kw={'class': 'form-control'}
    )

    local_timezone = SelectField(
        'Local Timezone'
        , choices=['America/New_York', 'America/Chicago', 'America/Denver', 'America/Los_Angeles']
        , render_kw={'class': 'form-control'}
    )

    session_description = StringField(
        'Session Description'
        , render_kw={'class': 'form-control'}
        , description='A nearby street address for this location'
    )

    publish = BooleanField(
        'Publish Observation Session'
        , render_kw={'class': 'form-check-input'}
        , description='Check this box if you want to publish this observation session for public viewing.'
        )

    geolocate_observers = BooleanField(
        'Determine Coordinates'
        , render_kw={'class': 'form-check-input'}
        , description='Use the location of the observers to determine the distance of the street segment.'
        )

    # delete

    # recaptcha = RecaptchaField()
    submit = SubmitField('Submit', render_kw={'class': 'btn btn-primary'})

    # cancel = SubmitField('Cancel', render_kw={'class': 'btn btn-secondary', 'formnovalidate': True})



class DistanceForm(FlaskForm):
    """
    Form to collect information about the distance between two users
    """


    user_a_latitude = DecimalField(
        'User A Latitude'
        , places=6
        , render_kw={'class': 'form-control', 'id': 'user_a_lat'}
        )

    user_a_longitude = DecimalField(
        'User A Longitude'
        , places=6
        , render_kw={'class': 'form-control', 'id': 'user_a_lon'}
        )

    user_b_latitude = DecimalField(
        'User B Latitude'
        , places=6
        , render_kw={'class': 'form-control', 'id': 'user_b_lat'}
        )

    user_b_longitude = DecimalField(
        'User B Longitude'
        , places=6
        , render_kw={'class': 'form-control', 'id': 'user_b_lon'}
        )

    submit = SubmitField('Calculate Distance', render_kw={'class': 'btn btn-primary'})

