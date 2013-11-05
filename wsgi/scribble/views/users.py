import json
import requests
from flask import Blueprint, render_template, send_from_directory, request, jsonify, url_for, g, redirect, make_response
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask.ext.principal import identity_loaded, RoleNeed, UserNeed, Identity, identity_changed
from scribble import app, lm, oid, HOME_URL
from pymongo.objectid import ObjectId
from scribble.storage.models import Scruser

users = Blueprint('login_pages', __name__,
        template_folder='scribble/templates', static_folder='static')

def janrain_data():
    token = request.form['token']
    engage_api_params = dict(
        apiKey='f2e3e9fe58895c89a1bec0bd0d2326cf30ae4d5d', 
        token=token
    )
    user_data = requests.get("https://writeown.rpxnow.com/api/v2/auth_info", params=engage_api_params)
    return json.loads(user_data.text)


@users.route('/app_callback', methods=['POST'])
def app_callback():
    name = auth_info['profile']['name']['formatted']
    user = Scruser.query.filter(
            Scruser.open_id == {auth_info['profile']['providerSpecifier']: auth_info['profile']['identifier']}
        ).one()
    login_user(user, remember=True)
    g.user = user
    identity = Identity(user.mongo_id)
    identity_changed.send(app, identity=identity)
    return redirect(HOME_URL +'/'+ user.get_id())

@users.route('/create_user', methods=['POST'])
def create_user():
    scruser = Scruser(**request.form.to_dict())
    scruser.save()
    return json.dumps(scruser)

@lm.user_loader
def load_user(id):
    return  Scruser.query.filter(
        Scruser.mongo_id == ObjectId(id)
        ).one()


@users.route('/login', methods=['GET', 'POST'])
@oid.loginhandler
def login():
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('login_pages.index'))

    response = make_response(redirect(HOME_URL + '/static/register.html'))
    response.headers['Next'] = request.args['next']
    return response

@oid.after_login
def after_login(resp):
    if resp.email is None or resp.email == '':
        flash('Invalid login. Please try again.')
        return redirect( url_for('login') )
    user = Scruser.query.filter( 
        Scruser.email == resp.email ).first()
    login_user(user, remember=False)
    return redirect( request.args.get('next') or url_for('index') )


@app.before_request
def before_request():
    g.user = current_user
