-- Return information about one session

select
location_id
, session_mode
, distance_meters
, distance_value
, distance_units
, speed_limit_value
, speed_units
, session_description

from sessions
where session_id = :session_id