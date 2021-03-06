
update emoji_counter
    set 
    counter = :previous_count + :increment_value
    , last_observed_at = :last_observed_at

where session_id = :session_id
and emoji_id = :emoji_id