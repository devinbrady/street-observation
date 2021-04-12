
select
location_name
, local_timezone
, street_address
, city
, state_code
, zip_code
, location_description
, location_latitude
, location_longitude

from locations
where location_id = :location_id
