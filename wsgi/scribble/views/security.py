__author__ = 'tresback'

from flask import Flask, request, url_for, session, flash,\
    render_template
from flask.ext.oauth import OAuth
from scribble import app

oauth = OAuth()

facebook = oauth.remote_app('facebook',
    base_url='https://graph.facebook.com/',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    consumer_key='305702342839641',
    consumer_secret='43534fcacd8e1fda402ab611e913ae27'
)

@app.route('/login')
def login():
    return facebook.authorize(
        callback=url_for('facebook_authorized',
            next=request.args.get('next') or 
            request.referrer or None,
            _external=True))


@app.route('/login/authorized')
@facebook.authorized_handler
def facebook_authorized(resp):
    if resp is None:
        flash('You were denied')
        return '401 Unauthorized'


    me = facebook.get('/me')
    flash('Successfully logged in')
    return str(me.data)
