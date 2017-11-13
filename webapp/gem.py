import time

import constants
import utils


class GEM(object):
    def __init__(self, site = "Unknown", node = "Unknown"):
        self._nodes = utils.load_yaml("nodes.json")
        self._channels = utils.load_yaml("channels.json")
        self._electricity = {}

        self.site = "Unknown"
        self.node = "Unknown"
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
                if (isinstance(ch, int) and
                        (data.get(constants.ENERGY, 0) == 0 and data.get(constants.POWER, 0) == 0) or
                        (data.get(constants.CURRENT, 0) == 0 and data.get(constants.POWER, 0) == 0) or
                        (data.get(constants.ENERGY, 0) == 0 and data.get(constants.CURRENT, 0) == 0)):
                    del self._electricity[ch]

    def set_node(self, node):
        mapped_name = self._nodes.get(node, node)
        self.node = mapped_name

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
        if not mapped_name in self.electricity:
            self._electricity[mapped_name] = {
                constants.CHANNEL: channel,
                constants.POWER: 0.0,
                constants.CURRENT: 0.0,
                constants.ENERGY: 0.0
            }

        self._electricity[mapped_name][type] = val

