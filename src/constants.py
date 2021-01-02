import os
import tempfile


CREDS_DIR = os.environ.get('CREDS_DIR', tempfile.gettempdir())
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
DEFAULT_LOG_DIR = os.path.abspath(os.path.join(BASE_DIR, '..', 'logs'))

LOG_DIR = os.environ.get('LOG_DIR', DEFAULT_LOG_DIR)
REQ_DIR = os.path.join(LOG_DIR, 'requests')

LOG_LEVEL = os.environ.get('LOG_LEVEL', "info")
LOG_STDOUT = os.environ.get('LOG_STDOUT', False) == 'True'
LOG_DATA_STDOUT = os.environ.get('LOG_DATA_STDOUT', False) == 'True'
LOG_REQUESTS = os.environ.get('LOG_REQUESTS', None)
LOG_FILE_ASCIIWH = os.path.join(LOG_DIR, 'thor-asciiwh.log')

LOG_FS_ENABLED = os.environ.get('LOG_FS_ENABLED', False) == 'True'
LOG_S3_BUCKET = os.environ.get('S3_BUCKET', None)
LOG_S3_DATAPATH = os.environ.get('S3_DATAPATH', 'thordata')

if not os.path.exists(REQ_DIR):
    os.makedirs(REQ_DIR)

ASCII_WH_PORT = 8467

SITE = "site"
NODE = "node"
FQ_NODE = "fq_node"
TIME = "time"
TIMESTAMP = "timestamp"
TIMESTAMP_MILLIS = "timestamp_millis"
TIMESTAMP_CURRENT = "?"
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S %z"
VOLTAGE = "voltage"
ELECTRICITY = "electricity"
TEMPERATURE = "temperature"
FAHRENHEIT_UNIT = "F"
TEMPERATURE_UNKNOWN = "x"

CHANNEL_NUMBER = "channel_number"
CHANNEL_NAME = "channel_name"
BIAS = "bias"
UNKNOWN = "unknown"
CATEGORY = "category"
FUNCTION = "function"
POWER = "power"
CURRENT = "current"
ENERGY = "energy"

UNITS = {
    TEMPERATURE: "Fahrenheit",
    VOLTAGE: "Volts",
    POWER: "Watts",
    CURRENT: "Amps",
    ENERGY: "Watt Hours"
}

GEM_POWER = "p"
GEM_CURRENT = "a"
GEM_WHP = "whp"
GEM_ENERGY = "wh"
GEM_TEMPERATURE = "t"
GEM_SERIAL = "n"
GEM_SERIAL_EXT = "\\n"  # Subsequent packets come through
GEM_SERIAL_EXTENDED = "n="
GEM_VOLTAGE = "v"
GEM_ELAPSED = "m"

SPLUNK_EVENTS = "events"
SPLUNK_METRICS = "metrics"
SPLUNK_METRICS_SCS = "metrics-scs"

PRUNE_EMPTY = os.environ.get("PRUNE_EMPTY", True) == 'True'

STAGING_IDP_HOST = "https://splunk-ciam.okta.com"
STAGING_IDP_AUTHSERVER = "aus1rarj6tQPJfJlz2p7"
PRODUCTION_IDP_HOST = "https://splunk-ext.okta.com"
PRODUCTION_IDP_AUTHSERVER = "aus1vigjbbW3KwZJ72p7"
