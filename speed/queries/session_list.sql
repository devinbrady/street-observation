
select
s.session_id::varchar
, s.session_mode
, s.session_description
, s.created_at
, s.local_timezone
, s.publish

from sessions s
