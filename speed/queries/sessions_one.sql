-- Return information about one session

select
s.session_id::varchar
, s.session_mode
, s.distance_meters
, s.distance_value
, s.distance_units
, s.speed_limit_value
, s.speed_units
, s.session_description
, s.publish
, s.local_timezone
, s.created_at

from sessions s

where s.session_id = :session_id