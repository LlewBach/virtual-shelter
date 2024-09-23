web: daphne -b 0.0.0.0 -p $PORT virtual_shelter.asgi:application  # ASGI server for WebSockets
worker: celery -A virtual_shelter worker --loglevel=info  # Celery worker
beat: celery -A virtual_shelter beat --loglevel=info  # Celery Beat scheduler