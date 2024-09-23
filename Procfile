web: daphne -b 0.0.0.0 -p $PORT virtual_shelter.asgi:application
worker: celery -A virtual_shelter worker --loglevel=info --beat