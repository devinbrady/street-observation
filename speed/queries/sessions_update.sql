
update sessions
set 
    distance_meters = :distance_meters
    , distance_value = :distance_value
    , distance_units = :distance_units
    , speed_limit_value = :speed_limit_value
    , speed_units = :speed_units
    , session_mode = :session_mode
    , session_description = :session_description
    , updated_at = :updated_at

where session_id = :session_id
