
select
e.emoji_id
, e.display_order
, count(distinct co.counter_id) as num_observations

from emoji e
left join counter_observations co on (
    co.emoji_id = e.emoji_id
    and co.session_id = :session_id
    )
    
group by e.emoji_id, e.display_order
order by e.display_order