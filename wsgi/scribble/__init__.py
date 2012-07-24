__author__ = 'tresback'

import json
import uuid
from flaskext.mongoalchemy import MongoAlchemy
from flask import Flask, request, url_for, session, flash,\
    render_template
import os

app = Flask(__name__, static_url_path='/static')
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
    return response

#TODO move this back to storage.__init__
app.config['MONGOALCHEMY_SERVER'] = os.environ.get('OPENSHIFT_NOSQL_DB_HOST', 'localhost')
app.config['MONGOALCHEMY_PORT'] = int(os.environ.get('OPENSHIFT_NOSQL_DB_PORT', 27017))
app.config['MONGOALCHEMY_USER'] = os.environ.get('OPENSHIFT_NOSQL_DB_USERNAME')
app.config['MONGOALCHEMY_PASSWORD'] = os.environ.get('OPENSHIFT_NOSQL_DB_PASSWORD')
app.config['MONGOALCHEMY_DATABASE'] = os.environ.get('OPENSHIFT_APP_NAME', 'scribble')
app.config['MONGOALCHEMY_SERVER_AUTH'] = False

db = MongoAlchemy(app)

from scribble.views.scribbles import scribs
app.register_blueprint(scribs)

if __name__ == '__main__':
    app.run('127.0.0.1')
