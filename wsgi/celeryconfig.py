from scribble import app

## Broker settings.
BROKER_URL = 'mongodb://%s:%d/celery_tasks' % (app.config['MONGOALCHEMY_SERVER'], app.config['MONGOALCHEMY_PORT'])

# List of modules to import when celery starts.
CELERY_IMPORTS = ("scribble.views.scribbles", )

## Using the database to store task state and results.
CELERY_RESULT_BACKEND = "mongodb"
CELERY_RESULT_DBURI = 'mongodb://%s:%d/celery_tasks' % (app.config['MONGOALCHEMY_SERVER'], app.config['MONGOALCHEMY_PORT'])

CELERY_ANNOTATIONS = {"tasks.add": {"rate_limit": "10/s"}}
