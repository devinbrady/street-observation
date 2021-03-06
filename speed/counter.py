
import os
import pandas as pd
from sqlalchemy import text
from flask import current_app as app
from flask import render_template, request, redirect

from . import db
from . import models
from . import utilities



@app.route('/counter', methods=['GET'])
def counter_handler():

    session_id = request.args.get('session_id')
    location_id = request.args.get('location_id')

    with open(os.path.join(app.root_path, 'queries/counter_session.sql'), 'r') as f:
        counter_obs = pd.read_sql(text(f.read()), db.session.bind, params={'session_id': session_id})

    return render_template(
        'counter.html'
        , counter_obs=counter_obs
        , session_id=session_id
        , location_id=location_id
        )



@app.route('/emoji', methods=['POST'])
def emoji_post():

    session_id = request.args.get('session_id')
    location_id = request.args.get('location_id')
    emoji_id = request.args.get('emoji_id')
    previous_count = int(request.args.get('previous_count'))
    action = request.args.get('action')
    row_exists = int(request.args.get('row_exists'))

    local_timezone = 'America/New_York' # todo: models.get_location_timezone(location_id)
    
    if previous_count == 0 and action == 'subtract_one':
        # Do nothing. We don't want to record a negative count
        pass

    else:

        if row_exists == 1:

            if action == 'add_one':
                increment_value = 1
            elif action == 'subtract_one':
                increment_value = -1

            with open(os.path.join(app.root_path, 'queries/update_emoji_counter.sql'), 'r') as f:
                result = db.engine.execute(
                    text(f.read())
                    , session_id=session_id
                    , emoji_id=emoji_id
                    , previous_count=previous_count
                    , increment_value=increment_value
                    , last_observed_at=utilities.now_utc()
                    )

        else:
            # row doesn't exist yet, insert it

            new_counter_observation = models.EmojiCounter(
                session_id=session_id
                , location_id=location_id
                , emoji_id=int(emoji_id)
                , local_timezone=local_timezone
                )

            db.session.add(new_counter_observation)
            db.session.commit()


    return redirect(f'/counter?location_id={location_id}&session_id={session_id}')

