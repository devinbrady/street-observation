
select
o.start_time
, o.end_time
, o.elapsed_seconds
, o.observation_valid
, s.session_id
, s.distance_meters
, s.distance_value
, s.distance_units
, s.speed_units
, s.speed_limit_value
, s.location_id
, o.local_timezone

from observations o
inner join sessions s using (session_id)

where o.observation_id = :observation_id
