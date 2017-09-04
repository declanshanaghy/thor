import collections
import json

import requests
import requests.auth


SPLUNK_URL = "http://35.166.45.189:8088/services/collector/event"
HEC_TOKEN = "B840C47D-FDF9-4C94-AD7F-EC92FD289204"
DEFAULT_HEADERS = {"Authorization": "Splunk " + HEC_TOKEN}


def send(records, time=None, source=None, sourcetype=None, logger=None):
    events = []
    for record in records:
        d = collections.OrderedDict()
        if time:
            d["time"] = time
        if source:
            d["source"] = source
        if sourcetype:
            d["sourcetype"] = sourcetype
        d["event"] = record

        events.append(json.dumps(d))

    data = "\n".join(events)

    if logger:
        logger.info("Ready to post: %s", data)

    r = requests.post(SPLUNK_URL, data=data, headers=DEFAULT_HEADERS)

    if r.status_code == 200:
        return r.json()
    else:
        raise StandardError("%s: %s" % (r.status_code, r.text))

