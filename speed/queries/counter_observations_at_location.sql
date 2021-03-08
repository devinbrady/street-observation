
select
loc.location_name
, s.session_id
, s.session_description
, co.counter_id
, co.emoji_id
, co.created_at
, co.local_timezone

from counter_observations co
inner join locations loc using (location_id)
inner join sessions s using (session_id)

where co.observation_valid
and loc.location_id = :location_id

order by co.created_at