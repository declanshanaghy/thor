import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATADIR = os.path.join(BASE_DIR, 'data')

LOG_DIR = os.path.abspath(os.path.join(BASE_DIR, '..', 'logs'))
REQ_DIR = os.path.join(LOG_DIR, 'requests')

LOG_REQUESTS = os.environ.get('LOG_REQUESTS', False)
LOG_FILE = os.path.join(LOG_DIR, 'thor.log')

if not os.path.exists(REQ_DIR):
    os.makedirs(REQ_DIR)

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

PRUNE_EMPTY = os.environ.get("PRUNE_EMPTY", False)
