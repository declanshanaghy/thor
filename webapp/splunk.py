import collections
import constants
import json

import requests
import requests.auth


SPLUNK_URL = "http://35.166.45.189:8088/services/collector/event"
HEC_TOKEN = "B840C47D-FDF9-4C94-AD7F-EC92FD289204"
DEFAULT_HEADERS = {"Authorization": "Splunk " + HEC_TOKEN}


class SplunkKVWalker():
    gem = None
    records = None

    def __init__(self, gem):
        self.gem = gem
        self._create_records()

    def _create_records(self):
        self.records = [
            ", ".join([
                'site="' + self.gem.site + '"',
                'node="' + self.gem.node + '"',
                'type="' + constants.VOLTAGE + '"',
                constants.VOLTAGE + '=' + str(self.gem.voltage),
            ])
        ]

        for data in self.gem.electricity:
            self.records.append(", ".join([
                'site="' + self.gem.site + '"',
                'node="' + self.gem.node + '"',
                'type="' + constants.ELECTRICITY + '"',
                constants.NAME + '="' + str(data[constants.NAME]) + '"',
                constants.CHANNEL + '=' + str(data[constants.CHANNEL]),
                constants.POWER + '=' + str(data[constants.POWER]),
                constants.CURRENT + '=' + str(data[constants.CURRENT]),
                constants.ENERGY + '=' + str(data[constants.ENERGY])
            ]))

        for data in self.gem.temperature:
            self.records.append(", ".join([
                'site="' + self.gem.site + '"',
                'node="' + self.gem.node + '"',
                'type="' + constants.TEMPERATURE + '"',
                constants.NAME + '="' + str(data[constants.NAME]) + '"',
                constants.TEMPERATURE + '=' + str(data[constants.TEMPERATURE]),
            ]))


def _send_events(records, time=None, source=None,
                 sourcetype=None, logger=None):
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


def send(gem, source=None, sourcetype=None, logger=None):
    w = SplunkKVWalker(gem)
    r = _send_events(w.records, time=gem.time,
                     source=source, sourcetype=sourcetype, logger=logger)
    logger.info("Splunk response: %s", r)

