import time
import json

import tatsu.model
import tatsu.walkers

from chalicelib import examples
from chalicelib import utils


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

PRUNE_EMPTY = True


class SEGWalker(tatsu.model.NodeWalker):

    channels = None
    seg = {
        SITE: None,
        NODE: None,
        TIMESTAMP: None,
        VOLTAGE: None,
        ELECTRICITY: {
            ENERGY: {},
            POWER: {},
            CURRENT: {}
        },
        TEMPERATURE: {}
    }

    def __init__(self):
        self.channels = utils.load_yaml("channels.json")

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
        e = self.seg[ELECTRICITY][ENERGY]
        p = self.seg[ELECTRICITY][POWER]
        c = self.seg[ELECTRICITY][CURRENT]
        for ch, data in self.seg[ELECTRICITY][CURRENT].items():
            # Remove the reading if:
            # the channel is not mapped
            #   and
            # any 2 entries are zero
            if (isinstance(ch, int) and
                    (e.get(ch, 0) == 0 and p.get(ch, 0) == 0) or
                    (c.get(ch, 0) == 0 and p.get(ch, 0) == 0) or
                    (e.get(ch, 0) == 0 and c.get(ch, 0) == 0)):
                if ch in e:
                    del e[ch]
                if ch in p:
                    del p[ch]
                if ch in c:
                    del c[ch]

    def _prune_temperature(self):
        for channel, data in self.seg[TEMPERATURE].items():
            # Remove the reading if:
            # the channel is not mapped
            #   and
            # it's value is zero
            if isinstance(channel, int) and data == 0:
                del self.seg[TEMPERATURE][channel]

    def walk__measurement(self, node):
        return self.walk(node.reading)

    def _set_channel(self, node, type, val):
        ch = node.ch
        mapped_name = self.channels[ELECTRICITY].get(str(node.ch), ch)

        readings = self.seg[ELECTRICITY][type]
        if not mapped_name in readings:
            readings[mapped_name] = 0.0
        readings[mapped_name] = val

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
        self.seg[TEMPERATURE][mapped_name] = node.t
        return node

    def walk__voltage(self, node):
        self.seg[VOLTAGE] = node.v
        return node


def parse(data):
    grammar = utils.load_data("seg.ebnf")
    parser = tatsu.compile(grammar, asmodel=True)
    model = parser.parse(data)
    return SEGWalker().walk(model)


if __name__ == "__main__":
    seg = parse(examples.EXAMPLE1)
    print(json.dumps(seg, indent=4, sort_keys=True))
