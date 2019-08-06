import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
DEFAULT_LOG_DIR = os.path.abspath(os.path.join(BASE_DIR, '..', 'logs'))

LOG_DIR = os.environ.get('LOG_DIR', DEFAULT_LOG_DIR)
REQ_DIR = os.path.join(LOG_DIR, 'requests')

LOG_REQUESTS = os.environ.get('LOG_REQUESTS', None)
LOG_FILE_WEB = os.path.join(LOG_DIR, 'thor-web.log')
LOG_FILE_ASCIIWH = os.path.join(LOG_DIR, 'thor-asciiwh.log')

if not os.path.exists(REQ_DIR):
    os.makedirs(REQ_DIR)

ASCII_WH_PORT = 8467

SITE = "site"
NODE = "node"
FQ_NODE = "fq_node"
TIME = "time"
TIMESTAMP = "timestamp"
TIMESTAMP_CURRENT = "?"
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S %z"
VOLTAGE = "voltage"
ELECTRICITY = "electricity"
TEMPERATURE = "temperature"
TEMPERATURE_UNKNOWN = "x"

CHANNEL = "channel"
POWER = "power"
CURRENT = "current"
ENERGY = "energy"

GEM_POWER = "p"
GEM_CURRENT = "a"
GEM_WHP = "whp"
GEM_ENERGY = "wh"
GEM_TEMPERATURE = "t"
GEM_SERIAL = "n"
GEM_VOLTAGE = "v"
GEM_ELAPSED = "m"

NAME = "name"
SPLUNK_EVENTS = "events"
SPLUNK_METRICS = "metrics"

PRUNE_EMPTY = os.environ.get("PRUNE_EMPTY", True)

STAGING_IDP_HOST = "https://splunk-ciam.okta.com"
STAGING_IDP_AUTHSERVER = "aus1rarj6tQPJfJlz2p7"
PRODUCTION_IDP_HOST = "https://splunk-ext.okta.com"
PRODUCTION_IDP_AUTHSERVER = "aus1vigjbbW3KwZJ72p7"
