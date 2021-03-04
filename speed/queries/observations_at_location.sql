
select
loc.location_name
, s.session_id
, s.distance_miles
, o.observation_id
, o.elapsed_seconds
, o.start_time

from observations o
inner join sessions s using (session_id)
inner join locations loc using (location_id)

where o.observation_valid
and o.end_time is not null
and loc.location_id = :location_id

order by start_time
