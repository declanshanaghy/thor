import logging
import json
import os

import constants
import seg
import splunk



if __name__ == "__main__":
    for root, dirs, files in os.walk(constants.REQ_DIR):
        for name in files:
            n = os.path.join(root, name)
            with open(n) as f:
                data = f.read()
            print("Parsing " + n)
            s = seg.parse(data)
            print("Sending " + json.dumps(s.records, indent=4))
            r = splunk.send(s.records, time=s.time,
                            source="dshanaghy-mpb:local", logger=logging)
