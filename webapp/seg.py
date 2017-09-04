import os
import time

import tatsu.model
import tatsu.walkers

import utils


SITE = "site"
NODE = "node"
FQ_NODE = "fq_node"
TIME = "time"
TIMESTAMP = "timestamp"
TIMESTAMP_CURRENT = "?"
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S %z"
VOLTAGE = "voltage"
ELECTRICITY = "electricity"
TEMPERATURE = "temperature"
TEMPERATURE_UNKNOWN = "x"

CHANNEL = "channel"
POWER = "power"
CURRENT = "current"
ENERGY = "energy"

NAME = "name"

PRUNE_EMPTY = os.environ.get("PRUNE_EMPTY", False)


class JSONWalker(tatsu.model.NodeWalker):

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
            TIME: None,
            TIMESTAMP: None,
            VOLTAGE: None,
            ELECTRICITY: [],
            TEMPERATURE: []
        }

    @property
    def fq_node(self):
        return self.site + ':' + self.node

    @property
    def site(self):
        return self.seg[SITE]

    @property
    def node(self):
        return self.seg[NODE]

    @property
    def timestamp(self):
        return self.seg[TIMESTAMP]

    @property
    def time(self):
        return self.seg[TIME]

    @property
    def voltage(self):
        return self.seg[VOLTAGE]

    def walk_object(self, node):
        return node

    def walk__gem(self, node):
        self.seg[SITE] = node.site
        self.seg[NODE] = node.node

        if node.ts == TIMESTAMP_CURRENT:
            node.ts = time.strftime(TIMESTAMP_FORMAT)

        self.seg[TIMESTAMP] = node.ts
        self.seg[TIME] = time.time()

        for measurement in node.measurements:
            self.walk(measurement)

        if PRUNE_EMPTY:
            self._prune_electricity()
            self._prune_temperature()

        self._format_electricity()

        return self

    def _prune_electricity(self):
        if PRUNE_EMPTY:
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

    def _format_electricity(self):
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
                CHANNEL: ch,
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


class SplunkKVWalker(JSONWalker):
    records = None

    def walk__gem(self, node):
        super(SplunkKVWalker, self).walk__gem(node)
        self._create_records()
        return self

    def _create_records(self):
        self.records = [
            ", ".join([
                'site="' + self.seg[SITE] + '"',
                'node="' + self.seg[NODE] + '"',
                'type="' + VOLTAGE + '"',
                VOLTAGE + '=' + str(self.seg[VOLTAGE]),
            ])
        ]

        for data in self.seg[ELECTRICITY]:
            self.records.append(", ".join([
                'site="' + self.seg[SITE] + '"',
                'node="' + self.seg[NODE] + '"',
                'type="' + ELECTRICITY + '"',
                NAME + '="' + str(data[NAME]) + '"',
                CHANNEL + '=' + str(data[CHANNEL]),
                POWER + '=' + str(data[POWER]),
                CURRENT + '=' + str(data[CURRENT]),
                ENERGY + '=' + str(data[ENERGY])
            ]))

        for data in self.seg[TEMPERATURE]:
            self.records.append(", ".join([
                'site="' + self.seg[SITE] + '"',
                'node="' + self.seg[NODE] + '"',
                'type="' + TEMPERATURE + '"',
                NAME + '="' + str(data[NAME]) + '"',
                TEMPERATURE + '=' + str(data[TEMPERATURE]),
            ]))


def parse(data):
    grammar = utils.load_data("seg.ebnf")
    parser = tatsu.compile(grammar, asmodel=True)
    model = parser.parse(data)
    return SplunkKVWalker().walk(model)
