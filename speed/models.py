
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

import pandas as pd
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import UUID
import uuid

from . import db
from . import utilities



def generate_uuid():
    return str(uuid.uuid4())



def get_session_timezone(session_id):

    query = text('select local_timezone from sessions where session_id = :session_id')
    df = pd.read_sql(query, db.session.bind, params={'session_id': session_id})

    return df['local_timezone'].values[0]



def user_is_admin(user_id):
    """
    Return boolean indicating whether the user is an admin
    """

    query = text('select is_admin from users where user_id = :user_id')
    df = pd.read_sql(query, db.session.bind, params={'user_id': user_id})

    return df['is_admin'].values[0]



class ObservationSession(db.Model):
    """
    Record info about a session of observations
    """

    __tablename__ = 'sessions'
    session_id = db.Column(UUID(as_uuid=True), primary_key=True)
    session_mode = db.Column(db.String(20))
    speed_limit_value = db.Column(db.Float)
    speed_units = db.Column(db.String, nullable=False)
    distance_meters = db.Column(db.Float, nullable=False)
    distance_value = db.Column(db.Float, nullable=False)
    distance_units = db.Column(db.String, nullable=False)
    session_latitude = db.Column(db.Float)
    session_longitude = db.Column(db.Float)
    session_description = db.Column(db.String)
    publish = db.Column(db.Boolean, nullable=False)
    local_timezone = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False)
    deleted_at = db.Column(db.DateTime(timezone=True))
    
    def __init__(
            self
            , session_id
            , session_mode
            , local_timezone
            , distance_value
            , distance_units
            , speed_units
            , publish
            # , session_latitude
            # , session_longitude
            , speed_limit_value=None
            , distance_meters=None
            , session_description=None
        ):

        self.session_id = session_id
        self.session_mode = session_mode
        self.speed_limit_value = speed_limit_value
        self.speed_units = speed_units
        self.distance_meters = distance_meters
        self.distance_value = distance_value
        self.distance_units = distance_units
        # self.session_latitude = session_latitude
        # self.session_longitude = session_longitude
        self.session_description = session_description
        self.local_timezone = local_timezone
        self.publish = publish
        
        # Defaults when record created
        utc_now = utilities.now_utc()
        self.created_at = utc_now
        self.updated_at = utc_now
        self.deleted_at = None



class SpeedObservation(db.Model):
    """
    Record the start and stop time of each vehicle
    """

    __tablename__ = 'speed_observations'
    observation_id = db.Column(UUID(as_uuid=True), primary_key=True)
    session_id = db.Column(UUID(as_uuid=True), db.ForeignKey('sessions.session_id'), nullable=False)
    observation_valid = db.Column(db.Boolean, nullable=False)
    elapsed_seconds = db.Column(db.Float)
    observation_description = db.Column(db.String)
    local_timezone = db.Column(db.String, nullable=False)
    start_time = db.Column(db.DateTime(timezone=True), nullable=False)
    end_time = db.Column(db.DateTime(timezone=True))
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False)

    def __init__(
            self
            , observation_id
            , session_id
            , local_timezone
            , start_time=None
            , end_time=None
            , elapsed_seconds=None
            , observation_description=None
        ):

        self.observation_id = observation_id
        self.session_id = session_id
        self.start_time = start_time
        self.end_time = end_time
        self.elapsed_seconds = elapsed_seconds
        self.observation_description = observation_description
        self.local_timezone = local_timezone

        # Defaults when record created
        self.observation_valid = True
        self.updated_at = utilities.now_utc()



class User(UserMixin, db.Model):
    """
    Store information about the people using our site
    """

    __tablename__ = 'users'
    user_id = db.Column(UUID(as_uuid=True), primary_key=True)
    full_name = db.Column(db.String(80))
    username = db.Column(db.String(120))
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, nullable=False)
    # email = db.Column(db.String(120))
    # phone_number = db.Column(db.String(120))
    local_timezone = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False)
    deleted_at = db.Column(db.DateTime(timezone=True))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return self.user_id

    def get_admin_status(self):
        return self.is_admin

    def __init__(self, username, local_timezone):

        self.user_id = generate_uuid()
        self.username = username
        self.local_timezone = local_timezone

        utc_now = utilities.now_utc()
        self.created_at = utc_now
        self.updated_at = utc_now
        self.is_admin = False



class UserSession(db.Model):
    """
    Store information connecting a user to an observation session
    """

    __tablename__ = 'user_sessions'

    # todo: maybe this ID should be a concat of user and session, data type of string, not UUID
    user_session_id = db.Column(UUID(as_uuid=True), primary_key=True)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.user_id'), nullable=False)
    session_id = db.Column(UUID(as_uuid=True), db.ForeignKey('sessions.session_id'), nullable=False)
    user_latitude = db.Column(db.Float)
    user_longitude = db.Column(db.Float)
    local_timezone = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False)
    deleted_at = db.Column(db.DateTime(timezone=True))

    def __init__(self, user_id, session_id, local_timezone):

        self.user_session_id = generate_uuid()
        self.user_id = user_id
        self.session_id = session_id
        self.local_timezone = local_timezone

        utc_now = utilities.now_utc()
        self.created_at = utc_now
        self.updated_at = utc_now



class CounterObservation(db.Model):
    """
    Record info about one counter observation
    """

    __tablename__ = 'counter_observations'
    counter_id = db.Column(UUID(as_uuid=True), primary_key=True)
    session_id = db.Column(UUID(as_uuid=True), db.ForeignKey('sessions.session_id'), nullable=False)
    emoji_id = db.Column(db.Integer, db.ForeignKey('emoji.emoji_id'), nullable=False)
    observation_valid = db.Column(db.Boolean, nullable=False)
    local_timezone = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False)

    def __init__(
            self
            , counter_id
            , session_id
            , emoji_id
            , local_timezone
            ):

        self.counter_id = counter_id
        self.session_id = session_id
        self.emoji_id = emoji_id
        self.local_timezone = local_timezone

        # Defaults when record created
        utc_now = utilities.now_utc()
        self.created_at = utc_now
        self.updated_at = utc_now
        self.observation_valid = True



class Emoji(db.Model):
    """
    Each emoji that can be displayed
    """

    __tablename__ = 'emoji'
    emoji_id = db.Column(db.Integer, primary_key=True)
    emoji_name = db.Column(db.String, nullable=False)
    glyph = db.Column(db.String)
    display_order = db.Column(db.Integer)
    emoji_description = db.Column(db.String)

