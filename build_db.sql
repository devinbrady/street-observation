-- build_db.sql

-- Database's timezone should always be UTC
set time zone 'UTC';


drop table if exists sessions;

CREATE TABLE sessions (
    session_id uuid PRIMARY KEY,
    session_mode character varying(20),
    full_name character varying(80),
    email character varying(120),
    speed_limit_mph double precision,
    distance_miles double precision,
    created_at timestamp without time zone
);

-- CREATE UNIQUE INDEX sessions_pkey ON sessions(session_id uuid_ops);


drop table if exists observations;

CREATE TABLE observations (
    observation_id uuid PRIMARY KEY,
    session_id uuid REFERENCES sessions(session_id),
    valid boolean NOT NULL,
    start_time timestamp without time zone,
    end_time timestamp without time zone,
    elapsed_seconds double precision
);

-- CREATE UNIQUE INDEX observations_pkey ON observations(observation_id uuid_ops);
