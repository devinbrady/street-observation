
select
o.elapsed_seconds
, s.distance_miles

from observations o
inner join sessions s using (session_id)

where s.session_id = :session_id
and o.end_time is not null
and o.observation_valid
