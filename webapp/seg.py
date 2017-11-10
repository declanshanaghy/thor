import time

import tatsu.model
import tatsu.walkers

import constants
import utils


class SEGWalker(tatsu.model.NodeWalker):
    electricity = {}
    gem = None

    def __init__(self, gem):
        self.gem = gem

    def walk_object(self, node):
        return node

    def walk__gem(self, node):
        self.gem.site = node.site
        self.gem.node = node.node

        if node.ts == constants.TIMESTAMP_CURRENT:
            node.ts = time.strftime(constants.TIMESTAMP_FORMAT)

        self.gem.timestamp = node.ts
        self.gem.time = time.time()

        for measurement in node.measurements:
            self.walk(measurement)

        self.gem.finalize()

        return self

    def walk__measurement(self, node):
        return self.walk(node.reading)

    def walk__energy(self, node):
        self.gem.set_channel(node.ch, constants.ENERGY, node.kwh)
        return node

    def walk__power(self, node):
        self.gem.set_channel(node.ch, constants.POWER, node.w)
        return node

    def walk__current(self, node):
        self.gem.set_channel(node.ch, constants.CURRENT, node.a)
        return node

    def walk__temperature(self, node):
        self.gem.set_temperature(node.ch, node.t)
        return node

    def walk__voltage(self, node):
        self.gem.voltage = node.v
        return node



def parse(data, gem):
    grammar = utils.load_data("seg.ebnf")
    parser = tatsu.compile(grammar, asmodel=True)
    model = parser.parse(data)
    return SEGWalker(gem).walk(model)
