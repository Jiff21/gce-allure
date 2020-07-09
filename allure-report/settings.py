import os
import logging
import google.cloud.logging


PROJECT_ID=os.getenv('PROJECT_ID', 'sf-qa-reports')
ZONE=os.getenv('ZONE', 'us-west2-b')
_ENV=os.getenv('_ENV', 'test')
INSTANCE_NAME=os.getenv('INSTANCE_NAME', 'allure-hub')

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# Switch to use env name?
UPLOAD_FOLDER = os.path.join(
    ROOT_DIR,
    'projects'
)

FLASK_SECRET = os.environ.get('FLASK_SECRET', 'fake-secret')

# Setup Loger
log_format = 'p%(process)s {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s'
logging.basicConfig(
    format=log_format,
    filename='/tmp/test-unstructured-log.log',
    level=os.environ.get('LOG_LEVEL', 'INFO')
)
client = google.cloud.logging.Client()
client.get_default_handler()
client.setup_logging()
