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
    def process(self, parser, logger=None, kinds=None):
        if not logger:
            logger = logging

        logger.info({
            "message": "Processing GEM packet",
            "data": parser.data,
        })

        utils.log_data(parser.kind(), parser.format_log())

        g = GEM()
        parser.parse(g)
        g.finalize()

        logger.info("Parsed GEM: %s", g)
        if splunk.send(g, kinds=kinds, logger=logger, source=g.fq_node):
            return {
                constants.TIMESTAMP: g.time,
                constants.TIMESTAMP_MILLIS: g.time_millis,
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
    time_millis = None
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
        self.time_millis = int(round(self.time * 1000))
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
            reading = {constants.CHANNEL_NAME: ch}
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
            if isinstance(data[constants.CHANNEL_NAME], int) and \
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
                is_int = False
                try:
                    is_int = isinstance(int(ch), int)
                except:
                    is_int = False
                no_eandp = (data.get(constants.ENERGY, 0) == 0 and
                            data.get(constants.POWER, 0) == 0)
                no_candp = (data.get(constants.CURRENT, 0) == 0 and
                            data.get(constants.POWER, 0) == 0)
                no_eandc = (data.get(constants.ENERGY, 0) == 0 and
                            data.get(constants.CURRENT, 0) == 0)
                remove = is_int and (no_candp or no_eandc or no_eandp)
                if remove:
                    del self._electricity[ch]

    def set_node(self, node):
        mapped = self._nodes.get(node)
        logging.info({
            "message": "set_node",
            "node": node,
            "mapped": mapped,
        })
        if mapped:
            self.site = mapped['site']
            self.node = mapped['node']
            return True
        return False

    def set_temperature(self, channel, val):
        if val == constants.TEMPERATURE_UNKNOWN:
            val = 0

        channel_info = self._channels[constants.TEMPERATURE].get(
            str(channel), None)
        if channel_info is None:
            channel_info = {
                constants.CHANNEL_NAME: channel,
            }

        name = channel_info[constants.CHANNEL_NAME]
        self.temperature.append({
            constants.CHANNEL_NAME: name,
            constants.CHANNEL_NUMBER: channel,
            constants.TEMPERATURE: val
        })

    def set_channel(self, channel, type, val):
        channel_info = self._channels[constants.ELECTRICITY].get(
            str(channel), None)
        if channel_info is None:
            channel_info = {
                constants.CHANNEL_NAME: channel,
                constants.CHANNEL_NUMBER: channel,
            }

        name = channel_info[constants.CHANNEL_NAME]
        if not name in self._electricity:
            self._electricity[name] = {
                constants.CHANNEL_NUMBER: channel,
                constants.POWER: 0.0,
                constants.CURRENT: 0.0,
                constants.ENERGY: 0.0
            }
            self._electricity[name]["dimensions"] = channel_info
            self._electricity[name]["dimensions"][constants.CHANNEL_NUMBER] = channel

        self._electricity[name][type] = val
