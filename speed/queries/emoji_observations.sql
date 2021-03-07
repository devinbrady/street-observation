
select *
from counter_observations
where session_id = :session_id
order by created_at desc