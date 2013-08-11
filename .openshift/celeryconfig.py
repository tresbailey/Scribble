import os

print 'Configuring celery cartridge with client override'

## Broker settings.
BROKER_URL = "%s/celery_tasks" % os.environ.get('OPENSHIFT_MONGODB_DB_URL')

# List of modules to import when celery starts.
CELERY_IMPORTS = ("scribble.views.scribbles", )

## Using the database to store task state and results.
CELERY_RESULT_BACKEND = "mongodb"
CELERY_RESULT_DBURI = "%s/celery_tasks" % os.environ.get('OPENSHIFT_MONGODB_DB_URL')

CELERY_ANNOTATIONS = {"tasks.add": {"rate_limit": "10/s"}}
