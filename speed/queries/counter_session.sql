
select
e.emoji_id
, e.display_order
, coalesce(ec.counter,0) as num_observations
, case when ec.counter is null then 0 else 1 end as row_exists

from emoji e
left join emoji_counter ec on (
    ec.emoji_id = e.emoji_id
    and ec.session_id = :session_id
    )
    
order by e.display_order
