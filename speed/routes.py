
import os

from flask import current_app as app
from flask import render_template, send_from_directory


@app.errorhandler(404)
@app.errorhandler(500)
def page_not_found(e):
    return render_template('problem.html', e=e), e.code

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico')

@app.route('/about', methods=['GET'])
def display_about():
    return render_template('about.html')

@app.route('/', methods=['GET'])
def display_index():
    return render_template('index.html')

# @app.route('/histogram', methods=['GET'])
# def display_histogram():
#     return render_template('histogram.html')

