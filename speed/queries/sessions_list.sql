
select
s.session_id
, s.distance_miles
, s.session_description
, loc.location_id
, loc.location_name
, loc.local_timezone
, min(o.start_time) as first_start
, count(o.*) as num_observations

from observations o
inner join sessions s using (session_id)
inner join locations loc using (location_id)

where o.observation_valid
and o.end_time is not null

group by 1,2,3,4,5,6
order by first_start desc
