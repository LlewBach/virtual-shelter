web: gunicorn virtual_shelter.wsgi:application
worker: celery -A virtual_shelter worker --loglevel=info
beat: celery -A virtual_shelter beat --loglevel=info