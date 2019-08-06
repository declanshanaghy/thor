import time
import logging
import os
import time

import constants
import splunk
import utils

import boto3
import botocore.exceptions


class GEMProcessor(object):
    def process(self, parser, logger=None, type=None):
        if not logger:
            logger = logging

        logger.info("Received data: %s", parser.data)

        if constants.LOG_REQUESTS is not None and "raw-data" in constants.LOG_REQUESTS:
            t = time.time()
            filename = "%s.post.txt" % time.strftime("%Y%m%dT%H%M%S%Z", time.gmtime(t))
            fspath = os.path.join(constants.REQ_DIR, filename)
            logger.info("Logging post-data to: %s", fspath)
            with open(fspath, "w") as f:
                f.write(parser.format_log())

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

        g = GEM()
        parser.parse(g)
        g.finalize()

        logger.info("Parsed GEM: %s", g)
        if splunk.send(g, type=type, logger=logger, source=g.fq_node):
            return {
                constants.TIMESTAMP: g.timestamp,
                constants.SITE: g.site,
                constants.NODE: g.node,
                constants.FQ_NODE: g.fq_node,
                constants.VOLTAGE: g.voltage,
                constants.ELECTRICITY: len(g.electricity),
                constants.TEMPERATURE: len(g.temperature),
            }
        else:
            return None


class GEM(object):
    site = None
    node = None
    time = None
    timestamp = None
    voltage = 0
    electricity = None
    temperature = None

    def __init__(self, site="Unknown", node="Unknown"):
        self._nodes = utils.load_yaml("nodes.json")
        self._channels = utils.load_yaml("channels.json")
        self._electricity = {}

        self.site = "Site"
        self.node = "Node"
        self.time = time.time()
        self.timestamp = time.time()
        self.voltage = 0
        self.electricity = []
        self.temperature = []

    @property
    def fq_node(self):
        return self.site + ':' + self.node


    def finalize(self):
        if constants.PRUNE_EMPTY:
            self._prune_electricity()
            self._prune_temperature()

        self._format_electricity()

    def _format_electricity(self):
        for ch, data in self._electricity.items():
            reading = {constants.NAME: ch}
            reading.update(data)
            self.electricity.append(reading)

    def _prune_temperature(self):
        todel = []
        for i in range(len(self.temperature)):
            # Remove the reading if:
            # the channel is not mapped
            #   and
            # it's value is zero
            data = self.temperature[i]
            if isinstance(data[constants.NAME], int) and \
                            data[constants.TEMPERATURE] == 0.0:
                todel.append(data)

        for data in todel:
            self.temperature.remove(data)


    def _prune_electricity(self):
        if constants.PRUNE_EMPTY:
            for ch, data in self._electricity.items():
                # Remove the reading if:
                # the channel is not mapped
                #   and
                # any 2 entries are zero
                no_eandp = (data.get(constants.ENERGY, 0) == 0 and
                            data.get(constants.POWER,0) == 0)
                no_candp = (data.get(constants.CURRENT, 0) == 0 and
                            data.get(constants.POWER, 0) == 0)
                no_eandc = (data.get(constants.ENERGY, 0) == 0 and
                            data.get(constants.CURRENT, 0) == 0)
                remove = isinstance(ch, int) and (no_candp or no_eandc or no_eandp)
                if remove:
                    del self._electricity[ch]

    def set_node(self, node):
        mapped = self._nodes.get(node)
        if mapped:
            self.site = mapped['site']
            self.node = mapped['node']
            return True
        return False

    def set_temperature(self, channel, val):
        mapped_name = self._channels[constants.TEMPERATURE].get(
            str(channel), channel)
        if val == constants.TEMPERATURE_UNKNOWN:
            val = 0
        self.temperature.append({constants.NAME: mapped_name,
                                 constants.TEMPERATURE: val})

    def set_channel(self, channel, type, val):
        mapped_name = self._channels[constants.ELECTRICITY].get(
            str(channel), channel)
        if not mapped_name in self._electricity:
            self._electricity[mapped_name] = {
                constants.CHANNEL: channel,
                constants.POWER: 0.0,
                constants.CURRENT: 0.0,
                constants.ENERGY: 0.0
            }

        self._electricity[mapped_name][type] = val

