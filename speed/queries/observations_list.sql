
select
o.observation_id
, o.start_time
, o.end_time
, o.elapsed_seconds
, o.observation_valid
, s.distance_miles
, s.speed_limit_mph
, loc.location_id

from observations o
inner join sessions s using (session_id)
inner join locations loc using (location_id)

where s.session_id = :session_id

order by o.start_time desc
