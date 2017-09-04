import time

import tatsu.model
import tatsu.walkers

import utils


SITE = "site"
NODE = "node"
TIMESTAMP = "timestamp"
TIMESTAMP_CURRENT = "?"
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S %z"
VOLTAGE = "voltage"
ELECTRICITY = "electricity"
TEMPERATURE = "temperature"
TEMPERATURE_UNKNOWN = "x"

POWER = "power"
CURRENT = "current"
ENERGY = "energy"

NAME = "name"

PRUNE_EMPTY = True


class SEGWalker(tatsu.model.NodeWalker):

    channels = None
    electricity = None
    seg = None

    def __init__(self):
        self.channels = utils.load_yaml("channels.json")
        self.electritiy = {}
        self.temperature = {}
        self.seg = {
            SITE: None,
            NODE: None,
            TIMESTAMP: None,
            VOLTAGE: None,
            ELECTRICITY: [],
            TEMPERATURE: []
        }

    def walk_object(self, node):
        return node

    def walk__gem(self, node):
        self.seg[SITE] = node.site
        self.seg[NODE] = node.node

        if node.ts == TIMESTAMP_CURRENT:
            node.ts = time.strftime(TIMESTAMP_FORMAT)

        self.seg[TIMESTAMP] = node.ts
        for measurement in node.measurements:
            self.walk(measurement)

        if PRUNE_EMPTY:
            self._prune_electricity()
            self._prune_temperature()

        return self.seg

    def _prune_electricity(self):
        for ch, data in self.electritiy.items():
            # Remove the reading if:
            # the channel is not mapped
            #   and
            # any 2 entries are zero
            if (isinstance(ch, int) and
                    (data.get(ENERGY, 0) == 0 and data.get(POWER, 0) == 0) or
                    (data.get(CURRENT, 0) == 0 and data.get(POWER, 0) == 0) or
                    (data.get(ENERGY, 0) == 0 and data.get(CURRENT, 0) == 0)):
                del self.electritiy[ch]


        for ch, data in self.electritiy.items():
            reading = {NAME: ch}
            reading.update(data)
            self.seg[ELECTRICITY].append(reading)

    def _prune_temperature(self):
        todel = []
        for i in range(len(self.seg[TEMPERATURE])):
            # Remove the reading if:
            # the channel is not mapped
            #   and
            # it's value is zero
            data = self.seg[TEMPERATURE][i]
            if isinstance(data[NAME], int) and data[TEMPERATURE] == 0.0:
                todel.append(data)

        for data in todel:
            self.seg[TEMPERATURE].remove(data)

    def walk__measurement(self, node):
        return self.walk(node.reading)

    def _set_channel(self, node, type, val):
        ch = node.ch
        mapped_name = self.channels[ELECTRICITY].get(str(node.ch), ch)
        if not mapped_name in self.electritiy:
            self.electritiy[mapped_name] = {
                POWER: 0.0,
                CURRENT: 0.0,
                ENERGY: 0.0
            }

        self.electritiy[mapped_name][type] = val

    def walk__energy(self, node):
        self._set_channel(node, ENERGY, node.kwh)
        return node

    def walk__power(self, node):
        self._set_channel(node, POWER, node.w)
        return node

    def walk__current(self, node):
        self._set_channel(node, CURRENT, node.a)
        return node

    def walk__temperature(self, node):
        mapped_name = self.channels[TEMPERATURE].get(str(node.ch), node.ch)
        if node.t == TEMPERATURE_UNKNOWN:
            node.t = 0
        self.seg[TEMPERATURE].append({NAME: mapped_name, TEMPERATURE: node.t})
        return node

    def walk__voltage(self, node):
        self.seg[VOLTAGE] = node.v
        return node


def parse(data):
    grammar = utils.load_data("seg.ebnf")
    parser = tatsu.compile(grammar, asmodel=True)
    model = parser.parse(data)
    return SEGWalker().walk(model)
