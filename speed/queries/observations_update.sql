
update speed_observations

set
    observation_valid = :valid_action
    , updated_at = :updated_at

where observation_id = :observation_id
