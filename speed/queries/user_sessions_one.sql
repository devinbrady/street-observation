
select
user_session_id

from user_sessions

where user_id = :user_id
and session_id = :session_id