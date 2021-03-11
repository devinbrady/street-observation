
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, PasswordField, TextField, IntegerField, DecimalField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email

from . import models


class LoginForm(FlaskForm):

    email = StringField('Email', render_kw={'class': 'form-control'})
    password = PasswordField('Password', render_kw={'class': 'form-control'})
    submit = SubmitField('Sign In', render_kw={'class': 'btn btn-primary'})



class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()], render_kw={'class': 'form-control'})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={'class': 'form-control'})
    local_timezone = SelectField(
        'Local Timezone'
        , choices=['America/New_York', 'America/Chicago', 'America/Denver', 'America/Los_Angeles']
        , render_kw={'class': 'form-control'}
    )
    submit = SubmitField('Register', render_kw={'class': 'btn btn-primary'})

    # def validate_username(self, username):
    #     user = models.User.query.filter_by(username=username.data).first()
    #     if user is not None:
    #         raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = models.User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class SessionSettingsForm(FlaskForm):
    """
    Form to collect information about a session
    """

    session_mode = SelectField(
        'Session Mode'
        , [DataRequired()]
        , choices=[
            'speed timer'
            # , 'speed radar'
            , 'counter'
            ]
        , render_kw={'class': 'form-control'}
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
        , [DataRequired()]
        , places=None
        , render_kw={'class': 'form-control'}
        )

    distance_units = SelectField(
        'Distance Units'
        , [DataRequired()]
        , choices=['feet', 'miles', 'meters', 'kilometers']
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

    # delete

    # recaptcha = RecaptchaField()
    submit = SubmitField('Submit', render_kw={'class': 'btn btn-primary'})

    # cancel = SubmitField('Cancel', render_kw={'class': 'btn btn-secondary', 'formnovalidate': True})




class LocationSettingsForm(FlaskForm):
    """
    Form to collect information about a location
    """

    location_name = StringField(
        'Location Name'
        , render_kw={'class': 'form-control'}
        , description='A descriptive name for this location'
    )

    local_timezone = SelectField(
        'Local Timezone'
        , choices=['America/New_York', 'America/Chicago', 'America/Denver', 'America/Los_Angeles']
        , render_kw={'class': 'form-control'}
    )

    street_address = StringField(
        'Street Address'
        , render_kw={'class': 'form-control'}
        , description='A nearby street address for this location'
    )

    city = StringField(
        'City'
        , render_kw={'class': 'form-control'}
    )

    state_code = SelectField(
        'State'
        , choices=['AK', 'AL', 'AR', 'AZ', 'CA', 'CO', 'CT', 'DC', 'DE', 'FL', 'GA', 'HI', 'IA', 'ID', 'IL', 'IN', 'KS', 'KY', 'LA', 'MA', 'MD', 'ME', 'MI', 'MN', 'MO', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH', 'NJ', 'NM', 'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VA', 'VT', 'WA', 'WI', 'WV', 'WY']
        , render_kw={'class': 'form-control'}
    )

    zip_code = StringField(
        'ZIP'
        , render_kw={'class': 'form-control'}
    )

    # location_latitude
    # location_longitude

    location_description = StringField(
        'Location Description'
        , render_kw={'class': 'form-control'}
    )

    # delete

    submit = SubmitField('Submit', render_kw={'class': 'btn btn-primary'})

