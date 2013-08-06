## Broker settings.
BROKER_URL = 'mongodb://localhost:27017/celery_tasks'

# List of modules to import when celery starts.
CELERY_IMPORTS = ("scribble.views.scribbles", )

## Using the database to store task state and results.
CELERY_RESULT_BACKEND = "mongodb"
CELERY_RESULT_DBURI = 'mongodb://localhost:27017/celery_tasks'

CELERY_ANNOTATIONS = {"tasks.add": {"rate_limit": "10/s"}}
