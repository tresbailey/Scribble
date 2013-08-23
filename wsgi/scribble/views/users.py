import json
from flask import Blueprint, render_template, send_from_directory, request, jsonify, url_for, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from scribble import app, lm, oid
from pymongo.objectid import ObjectId
from scribble.storage.models import Scruser

users = Blueprint('login_pages', __name__,
        template_folder='scribble/templates', static_folder='static')


@users.route('/create_user', methods=['POST'])
def create_user():
    scruser = Scruser(**request.form.to_dict())
    scruser.save()
    return json.dumps(scruser)

@lm.user_loader
def load_user(id):
   return  Scruser.query.filter(
        Scruser.user_id == ObjectId(id)
        ).one()


@users.route('/login', methods=['GET', 'POST'])
@oid.loginhandler
def login_user():
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('login_pages.index'))
    #return oid.try_login(request.form.to_dict() )
    return oid.try_login( 'https://me.yahoo.com' )


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
