

select
loc.location_id
, loc.location_name
, loc.local_timezone
, s.session_id
, s.session_mode
, s.session_description
, least(min(so.start_time), min(co.created_at)) as earliest_observation
, greatest(max(so.start_time), max(co.created_at)) as most_recent_observation
, count(distinct coalesce(so.observation_id, co.counter_id)) as num_observations

from sessions s
inner join locations loc using (location_id)
left join observations so on (
    so.session_id = s.session_id
    and so.observation_valid
    and so.end_time is not null
    )
left join counter_observations co on (
    co.session_id = s.session_id
    and co.observation_valid
    )


where loc.location_id = :location_id

group by 1,2,3,4,5,6

order by most_recent_observation desc

