
select
o.observation_id
, o.start_time
, o.end_time
, o.elapsed_seconds
, o.observation_valid
, s.distance_meters
, s.speed_limit_value
, s.speed_units
, o.local_timezone

from speed_observations o
inner join sessions s using (session_id)

where s.session_id = :session_id

order by o.start_time desc
