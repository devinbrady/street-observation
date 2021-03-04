
update sessions
set 
    distance_miles = :distance_miles
    , speed_limit_mph = :speed_limit_mph
    , session_mode = :session_mode
    , session_description = :session_description

where session_id = :session_id
