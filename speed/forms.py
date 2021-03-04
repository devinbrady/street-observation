
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
        , choices=['solo', 'pair', 'radar']
        , render_kw={'class': 'form-control'}
    )

    speed_limit_mph = IntegerField(
        'Speed Limit (mph)'
        , render_kw={'class': 'form-control'}
        )

    distance_value = DecimalField(
        'Distance'
        , [DataRequired()]
        , render_kw={'class': 'form-control'}
        )

    distance_units = SelectField(
        'Distance Units'
        , [DataRequired()]
        , choices=['feet', 'miles']
        , render_kw={'class': 'form-control'}
    )

    session_description = StringField(
        'Session Description'
        , render_kw={'class': 'form-control'}
        , description='A nearby street address for this location'
    )

    # publish = Boolean

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

