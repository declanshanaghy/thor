import collections
import constants
import json
import logging

import requests
import requests.auth


SPLUNK_HEC_URL = "http://thor.shanaghy.com:8088/services"
SPLUNK_EVENT_ENDPOINT = SPLUNK_HEC_URL + "/collector"
SPLUNK_METRIC_ENDPOINT = SPLUNK_HEC_URL + "/collector"
HEC_TOKEN = "B840C47D-FDF9-4C94-AD7F-EC92FD289204"
DEFAULT_HEADERS = {"Authorization": "Splunk " + HEC_TOKEN}


class SplunkHandler(object):
    gem = None
    index = None
    source = None
    sourcetype = None
    records = []
    logger = None

    def __init__(self, gem, index="main",
                 source=None, sourcetype=None, logger=None):
        self.gem = gem
        self.index = index
        self.source = source
        self.sourcetype = sourcetype
        self.logger = logger
        self._create_records()

    def _create_records(self):
        raise NotImplementedError(
            "Subclasses must implemement _create_records")


class SplunkEventsHandler(SplunkHandler):
    gem = None
    records = None

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


    def send(self):
        events = []
        for record in self.records:
            d = collections.OrderedDict()
            if self.gem.time:
                d["time"] = self.gem.time
            if self.index:
                d["index"] = self.index
            if self.source:
                d["source"] = self.source
            if self.sourcetype:
                d["sourcetype"] = self.sourcetype
            d["event"] = record

            events.append(json.dumps(d))

        data = "\n".join(events)

        if self.logger:
            self.logger.info("Ready to post events: %s", data)

        r = requests.post(SPLUNK_EVENT_ENDPOINT,
                          data=data, headers=DEFAULT_HEADERS)

        if r.status_code == 200:
            return r.json()
        else:
            raise StandardError("%s: %s" % (r.status_code, r.text))


class SplunkMetricsHandler(SplunkHandler):
    def __init__(self, *args, **kwargs):
        super(SplunkMetricsHandler, self).__init__(index="main_metrics",
                                            *args, **kwargs)

    def _create_records(self):
        default_dimensions = {
            "site": self.gem.site,
            "node": self.gem.node,
        }
        m = {
            "metric_name": "voltage",
            "_value": self.gem.voltage,
        }
        m.update(default_dimensions)

        self.records = [ m ]

        for data in self.gem.electricity:
            for type in [ constants.CURRENT, constants.POWER,
                          constants.ENERGY ]:
                m = {
                    "metric_name": type,
                    "_value": data[type],
                    constants.CHANNEL: data.get(constants.CHANNEL, ""),
                    constants.NAME: data.get(constants.NAME, ""),
                }
                m.update(default_dimensions)
                self.records.append(m)

        for data in self.gem.temperature:
            m = {
                "metric_name": constants.TEMPERATURE,
                "_value": data[constants.TEMPERATURE],
                constants.CHANNEL: data.get(constants.CHANNEL, ""),
                constants.NAME: data.get(constants.NAME, ""),
            }
            m.update(default_dimensions)
            self.records.append(m)

    def send(self):
        events = []
        for record in self.records:
            d = collections.OrderedDict()
            if self.gem.time:
                d["time"] = self.gem.time
            if self.index:
                d["index"] = self.index
            if self.source:
                d["source"] = self.source
            if self.sourcetype:
                d["sourcetype"] = self.sourcetype
            d["event"] = "metric"
            d["fields"] = record

            events.append(json.dumps(d))

        data = "\n".join(events)

        if self.logger:
            self.logger.info("Ready to post metrics: %s", data)

        r = requests.post(SPLUNK_METRIC_ENDPOINT,
                          data=data, headers=DEFAULT_HEADERS)

        if r.status_code == 200:
            return True
        else:
            logging.error("%s: %s" % (r.status_code, r.text))
            return False


def send(gem, source=None, sourcetype=None, logger=None):
    if not logger:
        logger = logging

    s = SplunkMetricsHandler(gem, source=source,
                             sourcetype=sourcetype, logger=logger)
    if s.send():
        logger.info("Indexing succeeded")
        return True
    else:
        logger.error("Indexing failed")
        return False

