-- build_db.sql


drop table if exists obs;

create table obs (
    obs_id uuid primary key
    , session_id uuid
    , distance_miles float
    , start_time timestamp
    , end_time timestamp
    , elapsed_seconds float
    , mph float
);


drop table if exists sessions;

create table sessions (
    session_id uuid primary key
    , session_mode varchar
    , full_name varchar
    , email varchar
    , distance_miles float
    , created_at timestamp
    );
