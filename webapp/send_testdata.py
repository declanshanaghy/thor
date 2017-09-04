import json
import os

import constants
import seg
import splunk


if __name__ == "__main__":
    for root, dirs, files in os.walk(constants.REQ_DIR):
        for name in files:
            n = os.path.join(root, name)
            print("Reading " + n)
            with open(n) as f:
                data = f.read()
            print("Parsing")
            s = seg.parse(data)
            print("Sending " + json.dumps(s, indent=2))
            splunk.send(s)
