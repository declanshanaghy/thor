import os
import json

import chalicelib.constants


def load_data(file):
    n = os.path.join(chalicelib.constants.DATADIR, file)
    with open(n) as f:
        return f.read()

def load_yaml(file):
    n = os.path.join(chalicelib.constants.DATADIR, file)
    with open(n) as f:
        return json.load(f)
