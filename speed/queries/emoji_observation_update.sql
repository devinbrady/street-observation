
update counter_observations

set
    observation_valid = :valid_action
    , updated_at = :updated_at

where counter_id = :counter_id
