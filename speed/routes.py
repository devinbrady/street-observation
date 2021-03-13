
import os

from flask import current_app as app
from flask import render_template, send_from_directory, redirect, url_for
from flask_login import login_required, current_user, login_user, logout_user

from . import login_manager, db
from . import models
from .forms import LoginForm, RegistrationForm


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
# @app.route('/index', methods=['GET'])
def get_index():
    return render_template('index.html')


@login_manager.user_loader
def load_user(user_id):
    return models.User.query.get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('get_index'))

    form = LoginForm()

    if form.validate_on_submit():
        user = models.User.query.filter_by(username=form.username.data).first()

        if user is None or not user.check_password(form.password.data):
            print('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user)
        
        return redirect(url_for('get_index'))
    
    return render_template('login.html', form=form)



# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if current_user.is_authenticated:
#         return redirect('/')  # redirect(url_for('index'))
#     form = RegistrationForm(local_timezone='America/New_York')
#     if form.validate_on_submit():
#         user = models.User(username=form.username.data, local_timezone=form.local_timezone.data)
#         user.set_password(form.password.data)
#         db.session.add(user)
#         db.session.commit()
#         return redirect(url_for('login'))
#     return render_template('register.html', form=form)



@login_manager.unauthorized_handler
def unauthorized():
    """
    Show a friendly page when a logged-out user attempted to access a login_required page
    """
    return render_template('unauthorized.html')



@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')
