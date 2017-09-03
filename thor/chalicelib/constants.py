import os

DATADIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))

REQ_DIR = os.path.join(DATADIR, '..', '..', 'requests')
LOG_REQUESTS = os.environ.get('LOG_REQUESTS', False)
if LOG_REQUESTS == 'true':
    if not os.path.exists(REQ_DIR):
        os.makedirs(REQ_DIR)


