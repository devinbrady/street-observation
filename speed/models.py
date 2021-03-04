from . import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
import uuid


def generate_uuid():
    return str(uuid.uuid4())



class Location(db.Model):
    """
    Store information about the physical location where an observation session occurs
    """

    __tablename__ = 'locations'
    location_id = db.Column(UUID(as_uuid=True), primary_key=True)
    location_name = db.Column(db.String, nullable=False)
    local_timezone = db.Column(db.String, nullable=False)
    street_address = db.Column(db.String)
    city = db.Column(db.String)
    state_code = db.Column(db.String(2))
    zip_code = db.Column(db.String(5))
    location_latitude = db.Column(db.Float)
    location_longitude = db.Column(db.Float)
    location_description = db.Column(db.String)
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)
    deleted_at = db.Column(db.DateTime)

    def __init__(
            self
            , location_id
            , location_name
            , local_timezone
            , street_address
            , city
            , state_code
            , zip_code
            , location_description
            , location_latitude=1.2
            , location_longitude=2.3
        ):

        self.location_id = location_id
        self.location_name = location_name
        self.local_timezone = local_timezone
        self.street_address = street_address
        self.city = city
        self.state_code = state_code
        self.zip_code = zip_code
        # self.location_latitude = location_latitude
        # self.location_longitude = location_longitude
        self.location_description = location_description

        # Defaults when record created
        utc_now = datetime.utcnow()
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
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)
    deleted_at = db.Column(db.DateTime)
    
    def __init__(
            self
            , session_id
            , location_id
            , session_mode
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

        # Defaults when record created
        self.publish = False

        utc_now = datetime.utcnow()
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
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime)
    elapsed_seconds = db.Column(db.Float)
    observation_description = db.Column(db.String)
    updated_at = db.Column(db.DateTime, nullable=False)

    def __init__(
            self
            , observation_id
            , session_id
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

        # Defaults when record created
        self.observation_valid = True
        self.updated_at = datetime.utcnow()



class User(db.Model):
    """
    Store information about the people using our site
    """

    __tablename__ = 'users'
    user_id = db.Column(UUID(as_uuid=True), primary_key=True)
    full_name = db.Column(db.String(80))
    email = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)
    deleted_at = db.Column(db.DateTime)



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