
update locations
set 
    location_name = :location_name
    , local_timezone = :local_timezone
    , street_address = :street_address
    , city = :city
    , state_code = :state_code
    , zip_code = :zip_code
    , location_description = :location_description
    , updated_at = :updated_at

where location_id = :location_id
