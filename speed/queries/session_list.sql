
select
s.session_id::varchar
, loc.location_id::varchar
, loc.location_name
, s.session_mode
, s.session_description
, s.created_at
, s.local_timezone
, s.publish

from sessions s
inner join locations loc using (location_id)
