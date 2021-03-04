
select
o.start_time
, o.end_time
, o.elapsed_seconds
, o.observation_valid
, s.session_id
, s.distance_miles
, s.speed_limit_mph
, s.location_id
, o.local_timezone

from observations o
inner join sessions s using (session_id)

where o.observation_id = :observation_id
