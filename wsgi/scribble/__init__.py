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
app.config['MONGOALCHEMY_SERVER'] = os.environ.get('OPENSHIFT_NOSQL_DB_HOST', 'localhost')
app.config['MONGOALCHEMY_PORT'] = int(os.environ.get('OPENSHIFT_NOSQL_DB_PORT', 27017))
app.config['MONGOALCHEMY_USER'] = os.environ.get('OPENSHIFT_NOSQL_DB_USERNAME')
app.config['MONGOALCHEMY_PASSWORD'] = os.environ.get('OPENSHIFT_NOSQL_DB_PASSWORD')
app.config['MONGOALCHEMY_DATABASE'] = os.environ.get('OPENSHIFT_APP_NAME', 'scribble')
app.config['MONGOALCHEMY_SERVER_AUTH'] = False

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

app.config['CELERY_BROKER_URL'] = 'mongodb://localhost:27017/celery_tasks'
app.config['CELERY_RESULT_BACKEND'] = 'mongodb://localhost:27017/celery_tasks'
celery = make_celery(app)

from scribble.views.scribbles import scribs
from scribble.views.security import auths
app.register_blueprint(scribs)
app.register_blueprint(auths)

if __name__ == '__main__':
    app.run('127.0.0.1', threaded=True)
