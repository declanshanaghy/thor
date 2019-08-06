import logging
import os
import collections
import constants
import json
import logging

import boto3
import botocore.exceptions
import requests
import requests.auth
import time


SPLUNK_HEC_URL = "http://thor.shanaghy.com:8088/services/collector"
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

    def _create_post_data(self):
        raise NotImplementedError(
            "Subclasses must implemement _create_post_data")

    def send(self, logger=None):
        if not logger:
            logger = logging

        data = self._create_post_data()
        if self.logger:
            self.logger.info("Ready to post events: %s", data)

        if constants.LOG_REQUESTS is not None and "post-data" in constants.LOG_REQUESTS:
            t = time.time()
            filename = "%s.post.txt" % time.strftime("%Y%m%dT%H%M%S%Z", time.gmtime(t))
            fspath = os.path.join(constants.REQ_DIR, filename)
            logger.info("Logging post-data to: %s", fspath)
            with open(fspath, "w") as f:
                f.write(data)

            if constants.S3_BUCKET is not None:
                objectname = os.path.join(constants.S3_DATAPATH, filename)
                logger.info({
                    "message": "Logging post-data to S3",
                    "fspath": fspath,
                    "S3_BUCKET": constants.S3_BUCKET,
                    "objectname": objectname,
                })

                # Upload the file
                s3_client = boto3.client('s3')
                try:
                    response = s3_client.upload_file(fspath, constants.S3_BUCKET,
                                                     objectname)
                    logger.info("Response from s3: %s", response)
                except botocore.exceptions.ClientError as e:
                    logging.error(e)

        logger.info("post to: %s", SPLUNK_HEC_URL)
        r = requests.post(SPLUNK_HEC_URL,
                          data=data, headers=DEFAULT_HEADERS)

        logger.info("response: %s", r)
        if r.status_code == 200:
            return r.json()
        else:
            raise StandardError("%s: %s" % (r.status_code, r.text))



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

    def _create_post_data(self):
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

        return "\n".join(events)


class SplunkMetricsHandler(SplunkHandler):
    def __init__(self, *args, **kwargs):
        super(SplunkMetricsHandler, self).__init__(index="thormetrics",
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

    def _create_post_data(self):
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

        return "\n".join(events)

def send(gem, type=None, source=None,
         sourcetype=None, logger=None):
    if not logger:
        logger = logging

    s = None

    if type == constants.SPLUNK_EVENTS:
        s = SplunkEventsHandler(gem, source=source,
                                 sourcetype=sourcetype, logger=logger)
    elif type == constants.SPLUNK_METRICS:
        s = SplunkMetricsHandler(gem, source=source,
                                 sourcetype=sourcetype, logger=logger)

    if s:
        try:
            if s.send(logger=logger):
                logger.info("Indexing succeeded, type=%s", type)
                return True
            else:
                logger.error("Indexing failed, type=%s", type)
                return False
        except StandardError as ex:
            logger.error("Indexing caused exception, ex=%s", ex)


