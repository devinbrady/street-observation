
select
us.session_id
, loc.location_id
, loc.location_name
, s.session_mode
, s.session_description
, s.local_timezone
, greatest(max(coalesce(so.start_time, s.created_at)), max(coalesce(co.created_at, s.created_at))) as most_recent_observation
, count(distinct coalesce(so.observation_id, co.counter_id)) as num_observations


from user_sessions us
inner join sessions s using (session_id)
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


where us.user_id = :user_id

group by 1,2,3,4,5,6

order by most_recent_observation desc