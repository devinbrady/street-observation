from . import DB
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
import uuid


def generate_uuid():
    return str(uuid.uuid4())



class Session(DB.Model):
    """Record info about a session of observations"""

    __tablename__ = 'sessions'
    session_id = DB.Column(UUID(as_uuid=True), primary_key=True)
    session_mode = DB.Column(DB.String(20))
    full_name = DB.Column(DB.String(80))
    email = DB.Column(DB.String(120))
    distance_miles = DB.Column(DB.Float)
    created_at = DB.Column(DB.DateTime)

    def __init__(self, session_id, session_mode, full_name=None, email=None, distance_miles=None):

        self.session_id = session_id
        self.session_mode = session_mode
        self.full_name = full_name
        self.email = email
        self.distance_miles = distance_miles
        self.created_at = datetime.utcnow()




class Obs(DB.Model):
    """Record the start and stop time of each car"""

    __tablename__ = 'obs'
    obs_id = DB.Column(UUID(as_uuid=True), primary_key=True)
    session_id = DB.Column(UUID(as_uuid=True))
    # valid = True

    # observer_a_lat
    # observer_a_lon
    # observer_b_lat
    # observer_b_lon
    distance_miles = DB.Column(DB.Float)
    start_time = DB.Column(DB.DateTime)
    end_time = DB.Column(DB.DateTime)
    elapsed_seconds = DB.Column(DB.Float)
    mph = DB.Column(DB.Float)


    def __init__(self, obs_id, session_id, distance_miles=None, start_time=None, end_time=None, elapsed_seconds=None, mph=None):

        self.obs_id = obs_id
        self.session_id = session_id
        self.distance_miles = distance_miles
        self.start_time = start_time
        self.end_time = end_time
        self.elapsed_seconds = elapsed_seconds
        self.mph = mph
