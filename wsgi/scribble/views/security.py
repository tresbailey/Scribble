__author__ = 'tresback'

from flask import Blueprint, request, url_for, session, flash,\
    render_template
from flask.ext.oauth import OAuth
from scribble import app

oauth = OAuth()

auths = Blueprint('security_pages', __name__,
        template_folder='templates', static_folder='static')

facebook = oauth.remote_app('facebook',
    base_url='https://graph.facebook.com/',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    consumer_key='305702342839641',
    consumer_secret='43534fcacd8e1fda402ab611e913ae27'
)

@auths.route('/login')
def login():
    return facebook.authorize(
        callback=url_for('facebook_authorized',
            next=request.args.get('next') or request.referrer or None,
            _external=True))


@auths.route('/facebook-authorized')
@facebook.authorized_handler
def facebook_authorized(resp):
    next_url = request.args.get('next')
    if resp is None:
        print 'Denied'
        flash('You were denied')
        return '401 Unauthorized'
    me = facebook.get('/me')
    print 'Success'
    flash('Successfully logged in')
    return str(me.data)

@facebook.tokengetter
def get_facebook_oauth_token():
        return session.get('oauth_token')

def external_url_handler(error, endpoint, **values):
    print "Endpoint is: %s" % endpoint

app.handle_url_build_error = external_url_handler
