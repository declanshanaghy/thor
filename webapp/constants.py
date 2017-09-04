import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATADIR = os.path.join(BASE_DIR, 'data')

LOG_DIR = os.path.abspath(os.path.join(BASE_DIR, '..', 'logs'))
REQ_DIR = os.path.join(LOG_DIR, 'requests')

LOG_REQUESTS = os.environ.get('LOG_REQUESTS', False)
LOG_FILE = os.path.join(LOG_DIR, 'thor.log')

if not os.path.exists(REQ_DIR):
    os.makedirs(REQ_DIR)
