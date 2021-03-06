
import os
import pandas as pd
from sqlalchemy import text
from flask import current_app as app
from flask import render_template, request, redirect

from . import db
from . import models



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

    local_timezone = 'America/New_York' # todo: models.get_location_timezone(location_id)
    
    new_counter_observation = models.CounterObservation(
        counter_id=models.generate_uuid()
        , session_id=session_id
        , location_id=location_id
        , emoji_id=int(emoji_id)
        , local_timezone=local_timezone
        )

    db.session.add(new_counter_observation)
    db.session.commit()

    return redirect(f'/counter?location_id={location_id}&session_id={session_id}')
