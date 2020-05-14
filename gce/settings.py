import os

PROJECT_ID=os.getenv('PROJECT_ID', 'sf-qa-reports')
ZONE=os.getenv('ZONE', 'us-west2-b')
_ENV=os.getenv('_ENV', 'test')

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

UPLOAD_FOLDER = os.path.join(
    ROOT_DIR,
    _ENV
)

FLASK_SECRET = os.environ.get('FLASK_SECRET', 'fake-secret')
CLOUD_STORAGE_BUCKET = os.environ.get('CLOUD_STORAGE_BUCKET', 'fake-bucket-name')
