

import os
from celery import Celery

# Use CELERY_BROKER_URL env var if set, else default to Docker/deploy value

broker_url = os.environ.get("CELERY_BROKER_URL", "redis://redis:6379/0")
app = Celery('worker', broker=broker_url, backend=broker_url)

# For local development/testing, set:
#   export CELERY_BROKER_URL=redis://localhost:6379/0
# before running tests locally.


@app.task
def add(x, y):
    return x + y

@app.task
def multiply(x, y):
    return x * y

@app.task
def send_email(email_address, subject, body):
    # Logic to send an email
    pass

@app.task
def fetch_data_from_api(api_url):
    # Logic to fetch data from an API
    pass