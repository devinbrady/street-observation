
select
location_name
, local_timezone
, street_address
, city
, state_code
, zip_code
, location_description

from locations
where location_id = :location_id
