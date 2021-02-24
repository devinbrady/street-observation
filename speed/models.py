from . import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
import uuid


def generate_uuid():
    return str(uuid.uuid4())



class ObservationSession(db.Model):
    """Record info about a session of observations"""

    __tablename__ = 'sessions'
    session_id = db.Column(UUID(as_uuid=True), primary_key=True)
    session_mode = db.Column(db.String(20))
    full_name = db.Column(db.String(80))
    email = db.Column(db.String(120))
    speed_limit_mph = db.Column(db.Float)
    distance_miles = db.Column(db.Float)
    created_at = db.Column(db.DateTime)
    # updated_at

    # local timezone
    # location address
    # location lat lon
    # publish
    # description

    def __init__(self, session_id, session_mode, full_name=None, email=None, speed_limit_mph=None, distance_miles=None):

        self.session_id = session_id
        self.session_mode = session_mode
        self.full_name = full_name
        self.email = email
        self.speed_limit_mph = speed_limit_mph
        self.distance_miles = distance_miles
        self.created_at = datetime.utcnow()




class Observation(db.Model):
    """Record the start and stop time of each car"""

    __tablename__ = 'observations'
    observation_id = db.Column(UUID(as_uuid=True), primary_key=True)
    session_id = db.Column(UUID(as_uuid=True), db.ForeignKey('sessions.session_id'))
    valid = db.Column(db.Boolean, nullable=False) # todo: rename

    # observer_a_lat
    # observer_a_lon
    # observer_b_lat
    # observer_b_lon
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    elapsed_seconds = db.Column(db.Float)

    # updated_at
    # description


    def __init__(self, observation_id, session_id, valid=True, start_time=None, end_time=None, elapsed_seconds=None):

        self.observation_id = observation_id
        self.session_id = session_id
        self.valid = valid
        self.start_time = start_time
        self.end_time = end_time
        self.elapsed_seconds = elapsed_seconds
