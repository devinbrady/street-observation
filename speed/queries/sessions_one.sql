-- Return information about one session

select
s.location_id
, s.session_mode
, s.distance_meters
, s.distance_value
, s.distance_units
, s.speed_limit_value
, s.speed_units
, s.session_description
, loc.location_name

from sessions s
inner join locations loc using (location_id)

where s.session_id = :session_id