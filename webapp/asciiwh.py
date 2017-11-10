import time

import constants
import utils


class ASCIIWH(object):
    data = None
    gem = None

    def __init__(self, data, gem):
        self.data = data
        self.gem = gem

    def parse(self):
        for k, v in self.data.items():
            if k[:1] == constants.GEM_CURRENT:
                ch = k[2:]
                self.gem.set_channel(ch, constants.CURRENT, v)
            elif k[:1] == constants.GEM_POWER:
                ch = k[2:]
                self.gem.set_channel(ch, constants.POWER, v)
            elif k[:2] == constants.GEM_ENERGY:
                ch = k[3:]
                self.gem.set_channel(ch, constants.ENERGY, v)
            elif k[:1] == constants.GEM_TEMPERATURE:
                ch = k[2:]
                self.gem.set_temperature(ch, v)
            elif k == constants.GEM_SERIAL:
                self.gem.set_node(v)
            elif k == constants.GEM_VOLTAGE:
                self.gem.voltage = v
            elif k == constants.GEM_ELAPSED:
                pass
            else:
                print("UNKNOWN FIELD %s=%s", k, v)

        self.gem.finalize()

def parse(data, gem):
    return ASCIIWH(data, gem).parse()
