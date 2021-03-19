
select
s.session_id::varchar
, s.session_description
, co.counter_id
, co.emoji_id
, co.created_at
, co.local_timezone
, e.display_order
, e.glyph

from counter_observations co
inner join sessions s using (session_id)
inner join emoji e using (emoji_id)

where co.observation_valid
and s.session_id in :counter_sessions
