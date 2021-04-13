
update sessions
set 
    distance_meters = :distance_meters
    , distance_value = :distance_value
    , updated_at = :updated_at

where session_id = :session_id
