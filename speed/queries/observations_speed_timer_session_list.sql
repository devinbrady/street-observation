
select
s.session_id::varchar
, s.distance_meters
, s.distance_value
, s.distance_units
, s.speed_units
, s.session_description
, o.observation_id
, o.elapsed_seconds
, o.start_time
, o.local_timezone

from speed_observations o
inner join sessions s using (session_id)

where o.observation_valid
and o.end_time is not null
and s.session_id in :speed_timer_sessions
