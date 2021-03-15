
select
loc.location_id
, loc.location_name
, loc.city
, loc.state_code
, loc.local_timezone
, min(coalesce(so.start_time, co.created_at, loc.created_at)) as first_start
, greatest(max(so.start_time), max(co.created_at)) as most_recent_observation
, count(distinct s.session_id) as num_sessions
, count(distinct so.observation_id) as num_speed_observations
, count(distinct co.counter_id) as num_counter_observations

from locations loc
inner join sessions s using (location_id)
left join observations so on (
    so.session_id = s.session_id
    and so.observation_valid
    and so.end_time is not null
    )
left join counter_observations co on (
    co.session_id = s.session_id
    and co.observation_valid
    )

where s.publish

group by 1,2,3,4,5
order by first_start desc
