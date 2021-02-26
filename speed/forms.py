
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, TextField, IntegerField, DecimalField, SubmitField
from wtforms.validators import DataRequired, Length, Email


class SessionSettingsForm(FlaskForm):
    """
    Form to collect information about a session
    """

    session_mode = SelectField(
        'Session Mode'
        # , [DataRequired()]
        , choices=['solo', 'pair']
        , render_kw={'class': 'form-control'}
    )

    full_name = StringField(
        'Name'
        # , [DataRequired()]
        , render_kw={'class': 'form-control'}
    )

    email = StringField(
        'Email'
        # , [
        #     Email(message=('Not a valid email address.')),
        #     DataRequired()
        # ]
        , render_kw={'class': 'form-control'}
    )

    speed_limit_mph = IntegerField(
        'Speed Limit (mph)'
        , render_kw={'class': 'form-control'}
        )

    distance_miles = DecimalField(
        'Distance (miles)'
        , render_kw={'class': 'form-control'}
        )


    # body = TextField(
    #     'Message',
    #     [
    #         DataRequired(),
    #         Length(min=4,
    #         message=('Your message is too short.'))
    #     ]
    #     , render_kw={'class': 'form-control'}
    # )

    # recaptcha = RecaptchaField()
    submit = SubmitField('Submit', render_kw={'class': 'btn btn-primary'})

    # cancel = SubmitField('Cancel', render_kw={'class': 'btn btn-secondary', 'formnovalidate': True})
