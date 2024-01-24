# Celery Settings 
broker_url = 'redis://127.0.0.1:6379/0' # URL for the message broker,
result_backend = 'redis://127.0.0.1:6379/0'
task_serializer = 'json'
accept_content = ['json']  # Content type accepted
bind = '0.0.0.0'
timezone = 'UTC'
enable_utc = True