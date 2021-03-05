-- build_db.sql

-- Database's timezone should always be UTC
set time zone 'UTC';


drop table if exists locations cascade;

CREATE TABLE locations (
    location_id uuid PRIMARY KEY,
    location_name character varying NOT NULL,
    street_address character varying,
    city character varying,
    state_code character varying(2),
    zip_code character varying(5),
    location_latitude double precision,
    location_longitude double precision,
    location_description character varying,
    local_timezone character varying NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    deleted_at timestamp with time zone
);



drop table if exists sessions cascade;

CREATE TABLE sessions (
    session_id uuid PRIMARY KEY,
    location_id uuid NOT NULL REFERENCES locations(location_id),
    session_mode character varying(20),
    speed_limit_value double precision,
    speed_units character varying NOT NULL,
    distance_meters double precision NOT NULL,
    distance_value double precision NOT NULL,
    distance_units character varying NOT NULL,
    session_description character varying,
    publish boolean NOT NULL,
    local_timezone character varying NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    deleted_at timestamp with time zone
);


drop table if exists observations;

CREATE TABLE observations (
    observation_id uuid PRIMARY KEY,
    session_id uuid NOT NULL REFERENCES sessions(session_id),
    observation_valid boolean NOT NULL,
    elapsed_seconds double precision,
    observation_description character varying,
    local_timezone character varying NOT NULL,
    start_time timestamp with time zone NOT NULL,
    end_time timestamp with time zone,
    updated_at timestamp with time zone NOT NULL
);
