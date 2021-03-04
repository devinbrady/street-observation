-- Return information about one session

select
location_id
, session_mode
, speed_limit_mph
, distance_miles
, session_description

from sessions
where session_id = :session_id