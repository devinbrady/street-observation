
select
s.session_id
, s.distance_meters
, s.distance_value
, s.distance_units
, s.session_description
, min(o.start_time) as first_start
, count(o.*) as num_observations

from speed_observations o
inner join sessions s using (session_id)

where o.observation_valid
and o.end_time is not null

group by 1,2,3
order by first_start desc
