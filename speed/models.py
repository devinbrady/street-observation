
import pandas as pd
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import UUID
import uuid

from . import db
from . import utilities


def generate_uuid():
    return str(uuid.uuid4())


def get_location_timezone(location_id):

    query = text('select local_timezone from locations where location_id = :location_id')
    df = pd.read_sql(query, db.session.bind, params={'location_id': location_id})

    return df['local_timezone'].values[0]



def get_session_timezone(session_id):

    query = text('select local_timezone from sessions where session_id = :session_id')
    df = pd.read_sql(query, db.session.bind, params={'session_id': session_id})

    return df['local_timezone'].values[0]



class Location(db.Model):
    """
    Store information about the physical location where an observation session occurs
    """

    __tablename__ = 'locations'
    location_id = db.Column(UUID(as_uuid=True), primary_key=True)
    location_name = db.Column(db.String, nullable=False)
    street_address = db.Column(db.String)
    city = db.Column(db.String)
    state_code = db.Column(db.String(2))
    zip_code = db.Column(db.String(5))
    location_latitude = db.Column(db.Float)
    location_longitude = db.Column(db.Float)
    location_description = db.Column(db.String)
    local_timezone = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False)
    deleted_at = db.Column(db.DateTime(timezone=True))

    def __init__(
            self
            , location_id
            , location_name
            , street_address
            , city
            , state_code
            , zip_code
            , location_description
            , local_timezone
        ):

        self.location_id = location_id
        self.location_name = location_name
        self.street_address = street_address
        self.city = city
        self.state_code = state_code
        self.zip_code = zip_code
        self.location_latitude = None
        self.location_longitude = None
        self.location_description = location_description
        self.local_timezone = local_timezone

        # Defaults when record created
        utc_now = utilities.now_utc()
        self.created_at = utc_now
        self.updated_at = utc_now
        self.deleted_at = None



class ObservationSession(db.Model):
    """
    Record info about a session of observations
    """

    __tablename__ = 'sessions'
    session_id = db.Column(UUID(as_uuid=True), primary_key=True)
    location_id = db.Column(UUID(as_uuid=True), db.ForeignKey('locations.location_id'), nullable=False)
    session_mode = db.Column(db.String(20))
    speed_limit_mph = db.Column(db.Float)
    distance_miles = db.Column(db.Float, nullable=False)
    session_description = db.Column(db.String)
    publish = db.Column(db.Boolean, nullable=False)
    local_timezone = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False)
    deleted_at = db.Column(db.DateTime(timezone=True))
    
    def __init__(
            self
            , session_id
            , location_id
            , session_mode
            , local_timezone
            , speed_limit_mph=None
            , distance_miles=None
            , session_description=None
        ):

        self.session_id = session_id
        self.location_id = location_id
        self.session_mode = session_mode
        self.speed_limit_mph = speed_limit_mph
        self.distance_miles = distance_miles
        self.session_description = session_description
        self.local_timezone = local_timezone

        # Defaults when record created
        self.publish = False

        utc_now = utilities.now_utc()
        self.created_at = utc_now
        self.updated_at = utc_now
        self.deleted_at = None



class Observation(db.Model):
    """
    Record the start and stop time of each vehicle
    """

    __tablename__ = 'observations'
    observation_id = db.Column(UUID(as_uuid=True), primary_key=True)
    session_id = db.Column(UUID(as_uuid=True), db.ForeignKey('sessions.session_id'), nullable=False)
    # location_id = db.Column(UUID(as_uuid=True), db.ForeignKey('locations.location_id'), nullable=False)
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



class User(db.Model):
    """
    Store information about the people using our site
    """

    __tablename__ = 'users'
    user_id = db.Column(UUID(as_uuid=True), primary_key=True)
    full_name = db.Column(db.String(80))
    email = db.Column(db.String(120))
    local_timezone = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False)
    deleted_at = db.Column(db.DateTime(timezone=True))



class UserSessions(db.Model):
    """
    Store information connecting a user to an observation session
    """

    __tablename__ = 'user_sessions'
    session_user_id = db.Column(UUID(as_uuid=True), primary_key=True)
    session_id = db.Column(UUID(as_uuid=True), db.ForeignKey('sessions.session_id'), nullable=False)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.user_id'), nullable=False)
    user_latitude = db.Column(db.Float)
    user_longitude = db.Column(db.Float)
    local_timezone = db.Column(db.String, nullable=False)
