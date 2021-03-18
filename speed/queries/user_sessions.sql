
select distinct session_id::varchar

from user_sessions

where user_id = :user_id