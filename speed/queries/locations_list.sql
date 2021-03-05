-- List all locations

select
loc.location_id
, loc.location_name
, loc.local_timezone
, min(coalesce(o.start_time, loc.created_at)) as first_start
, max(o.start_time) as most_recent_observation
, count(distinct s.session_id) as num_sessions
, count(distinct o.observation_id) as num_observations

from locations loc
left join sessions s using (location_id)
left join observations o on (
    o.session_id = s.session_id
    and o.observation_valid
    and o.end_time is not null
    )

group by loc.location_id, loc.location_name
order by first_start desc
