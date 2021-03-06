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


drop table if exists counter_observations;

CREATE TABLE counter_observations (
    counter_id uuid PRIMARY KEY,
    session_id uuid NOT NULL REFERENCES sessions(session_id),
    location_id uuid NOT NULL REFERENCES locations(location_id),
    emoji_id integer NOT NULL,
    observation_valid boolean NOT NULL,
    local_timezone character varying NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL
);


drop table if exists emoji;

CREATE TABLE emoji (
    emoji_id SERIAL PRIMARY KEY,
    emoji_name character varying NOT NULL,
    glyph character varying,
    display_order integer,
    emoji_description character varying    
);



insert into emoji (emoji_id, emoji_name, glyph, display_order, emoji_description)
    values 
    (128694, 'person-walking', '????', 0, 'A person walking or running, of any age or gender, including babies in strollers')
    , (9855, 'wheelchair-symbol', '??????', 1, 'A wheelchair, whether motorized or not')
    , (128021, 'dog', '????', 2, 'A dog')
    , (128690, 'bicycle', '????', 3, 'A bicycle or e-bike')
    , (128756, 'kick-scooter', '????', 4, 'A kick scooter or skateboard, whether electric or not')
    , (127949, 'motorcycle', '????', 5, 'A motorcycle or moped')
    , (128652, 'bus', '????', 6, 'A bus')
    , (128663, 'automobile', '????', 7, 'A car, van, SUV, or pickup truck')
    , (128666, 'delivery-truck', '????', 8, 'A delivery truck or semi truck')
    ;


drop table if exists users cascade;

CREATE TABLE users (
    user_id uuid PRIMARY KEY,
    full_name character varying(80),
    username character varying(120),
    password_hash character varying(128),
    local_timezone character varying NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    deleted_at timestamp with time zone
);
