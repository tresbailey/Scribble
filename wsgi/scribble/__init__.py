__author__ = 'tresback'

from celery import Celery
import json
import uuid
from flaskext.mongoalchemy import MongoAlchemy
from flask import Flask, request, url_for, session, flash,\
    render_template
from gridfs import GridFS
import os
from scribble import celeryconfig

app = Flask(__name__)
app.debug = True
app.secret_key = str(uuid.uuid1())


@app.before_request
def convert_json():
    if request.data and request.data is not None:
        request.data = json.loads(request.data)


@app.after_request
def add_headers(response):
    if isinstance(response.data, dict) or isinstance(response.data, list):
        response.headers['Content-Type'] = 'application/json'
    response.headers.add_header('Access-Control-Allow-Origin', '*')
    response.headers.add_header('Access-Control-Allow-Headers', 'Content-Type')
    print 'response headers are %s' % response.headers
    return response

#TODO move this back to storage.__init__
app.config['MONGOALCHEMY_SERVER'] = os.environ.get('OPENSHIFT_MONGODB_DB_HOST', 'localhost')
app.config['MONGOALCHEMY_PORT'] = int(os.environ.get('OPENSHIFT_MONGODB_DB_PORT', 27017))
app.config['MONGOALCHEMY_DATABASE'] = os.environ.get('MONGO_DB', 'scribble')
app.config['MONGOALCHEMY_USER'] = os.environ.get('OPENSHIFT_MONGODB_DB_USERNAME')
app.config['MONGOALCHEMY_PASSWORD'] = os.environ.get('OPENSHIFT_MONGODB_DB_PASSWORD')
app.config['MONGOALCHEMY_SERVER_AUTH'] = True

db = MongoAlchemy(app)

scrib_shots = db.session.db.connection.scribble_shots
scrib_grid = GridFS(scrib_shots)

def make_celery(app):
    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    """
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            import pdb
            pdb.set_trace()
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    """
    return celery

app.config['CELERY_BROKER_URL'] = 'mongodb://%s:%d/celery_tasks' % (app.config['MONGOALCHEMY_SERVER'], app.config['MONGOALCHEMY_PORT'])
app.config['CELERY_RESULT_BACKEND'] = 'mongodb://%s:%d/celery_tasks' % (app.config['MONGOALCHEMY_SERVER'], app.config['MONGOALCHEMY_PORT'])
celery = make_celery(app)

HOME_URL = os.getenv('OPENSHIFT_GEAR_DNS', 'http://localhost')

import os
from flask.ext.login import LoginManager
from flask.ext.openid import OpenID

lm = LoginManager()
lm.init_app(app)
oid = OpenID( app, os.path.join('', 'tmp'))


if 'http' not in HOME_URL:
    HOME_URL = "https://%s" % HOME_URL

from scribble.views.scribbles import scribs
from scribble.views.users import users
#from scribble.views.security import auths
app.register_blueprint(scribs)
app.register_blueprint(users)
#app.register_blueprint(auths)

if __name__ == '__main__':
    app.run('127.0.0.1', threaded=True)
