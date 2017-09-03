import json

import tatsu.model
import tatsu.walkers


EXAMPLE1 = "(site e3c762216d70d0a (node gem1 ? (p_1 -0)(a_1 0.08)(p_2 -0)(a_2 0)(p_3 6)(a_3 1.36)(p_4 10)(a_4 2.10)(p_5 2)(a_5 .44)(p_6 1)(a_6 .12)(p_7 0)(a_7 0)(p_8 0)(a_8 0)(p_9 -65)(a_9 10.74)(p_10 0)(a_10 0)(p_11 -0)(a_11 0)(p_12 -0)(a_12 0)(p_13 12)(a_13 2.20)(p_14 -0)(a_14 0)(p_15 0)(a_15 0)(p_16 7)(a_16 1.40)(p_17 0)(a_17 0)(p_18 16)(a_18 2.24)(p_19 -0)(a_19 0)(p_20 5)(a_20 1.48)(p_21 0)(a_21 0)(p_22 -0)(a_22 0)(p_23 -0)(a_23 0)(p_24 0)(a_24 0)(p_25 -0)(a_25 0)(p_26 -0)(a_26 0)(p_27 0)(a_27 0)(p_28 -0)(a_28 0)(p_29 2)(a_29 .30)(p_30 0)(a_30 0)(p_31 0)(a_31 0)(p_32 -0)(a_32 0)(p_34 0)(a_34 646.70)(p_35 0)(a_35 118.15)(p_36 0)(a_36 826.68)(p_37 0)(a_37 318.54)(p_38 0)(a_38 542.34)(p_39 0)(a_39 286.42)(p_40 0)(a_40 830.74)(temperature_1 0.0)(temperature_2 x)(temperature_3 x)(temperature_4 x)(temperature_5 x)(temperature_6 x)(temperature_7 x)(temperature_8 x)(voltage .0)))"
EXAMPLE2="""
(site e3c762216d70d0a
  (node gem1 ?
      (p_1 -0)(a_1 0.08)(p_2 -0)(a_2 .40)(p_3 6)(a_3 1.36)
      (temperature_1 0.0)(temperature_2 x)
      (voltage .0)
  )
)
"""
EXAMPLE3="(site e3c762216d70d0a (node 601-Kearney ? (p_1 0)(a_1 .16)(p_2 0)(a_2 0)(p_3 3)(a_3 .48)(p_4 5)(a_4 1.00)(p_5 0)(a_5 0.08)(p_6 1)(a_6 .12)(p_7 0)(a_7 0)(p_8 0)(a_8 0)(p_9 0)(a_9 0)(p_10 0)(a_10 0)(p_11 0)(a_11 0)(p_12 0)(a_12 0)(p_13 14)(a_13 2.48)(p_14 0)(a_14 0)(p_15 0)(a_15 0)(p_16 8)(a_16 1.54)(p_17 0)(a_17 0)(p_18 13)(a_18 2.02)(p_19 0)(a_19 0)(p_20 3)(a_20 1.30)(p_21 0)(a_21 0.02)(p_22 0)(a_22 0)(p_23 0)(a_23 0)(p_24 0)(a_24 0)(p_25 0)(a_25 0)(p_26 0)(a_26 0)(p_27 0)(a_27 0)(p_28 0)(a_28 0)(p_29 1)(a_29 .24)(p_30 0)(a_30 0)(p_31 0)(a_31 0)(p_32 0)(a_32 0)(p_34 0)(a_34 646.70)(p_35 0)(a_35 118.15)(p_36 0)(a_36 826.68)(p_37 0)(a_37 318.54)(p_38 0)(a_38 542.34)(p_39 0)(a_39 286.42)(p_40 0)(a_40 830.74)(temperature_1 87.5)(voltage .0)))"
EXAMPLE4="(site e3c762216d70d0a (node 601-Kearney ? (e_1 .00)(p_1 0)(a_1 .12)(e_2 .00)(p_2 0)(a_2 0)(e_3 .05)(p_3 2)(a_3 .46)(e_4 .08)(p_4 4)(a_4 .92)(e_5 .00)(p_5 0)(a_5 .10)(e_6 .02)(p_6 1)(a_6 .12)(e_7 .00)(p_7 0)(a_7 0)(e_8 .00)(p_8 0)(a_8 0)(e_9 .00)(p_9 0)(a_9 0)(e_10 .00)(p_10 0)(a_10 0)(e_11 .00)(p_11 0)(a_11 0)(e_12 .00)(p_12 0)(a_12 0)(e_13 .24)(p_13 14)(a_13 2.56)(e_14 .00)(p_14 0)(a_14 0)(e_15 .00)(p_15 0)(a_15 0)(e_16 .14)(p_16 8)(a_16 1.60)(e_17 .00)(p_17 0)(a_17 0)(e_18 .02)(p_18 0)(a_18 0)(e_19 .00)(p_19 0)(a_19 0)(e_20 .07)(p_20 4)(a_20 1.38)(e_21 .20)(p_21 10)(a_21 1.50)(e_22 .00)(p_22 0)(a_22 0)(e_23 .00)(p_23 0)(a_23 0)(e_24 .00)(p_24 0)(a_24 0)(e_25 .00)(p_25 0)(a_25 0)(e_26 .00)(p_26 0)(a_26 0)(e_27 .00)(p_27 0)(a_27 0)(e_28 .00)(p_28 0)(a_28 0)(e_29 .03)(p_29 1)(a_29 .28)(e_30 .00)(p_30 0)(a_30 0)(e_31 .00)(p_31 0)(a_31 0)(e_32 .00)(p_32 0)(a_32 0)(e_34 .00)(p_34 0)(a_34 646.70)(e_35 .00)(p_35 0)(a_35 118.15)(e_36 .00)(p_36 0)(a_36 826.68)(e_37 .00)(p_37 0)(a_37 318.54)(e_38 .00)(p_38 0)(a_38 542.34)(e_39 .00)(p_39 0)(a_39 286.42)(e_40 .00)(p_40 0)(a_40 830.74)(temperature_1 87.5)(voltage .0)))"

GRAMMAR = '''
    @@grammar::SEG
    
    start::Gem = 
        '(site' site:site_name 
            '(node' node:node_name 
                    ts:ts 
                    measurements:{measurement}+ 
            ')' 
        ')';

    site_name = identifier;
    node_name = identifier;
    ts = '?';
    measurement::Measurement = '(' reading:(energy|power|current|temperature|voltage) ')';
    
    energy::Energy = 'e_' ch:channel kwh:decimal;
    power::Power = 'p_' ch:channel w:decimal;
    current::Current = 'a_' ch:channel a:decimal;
    temperature::Temperature = 'temperature_' ch:channel t:('x'|decimal);
    voltage::Voltage = 'voltage' v:decimal;
    
    identifier = /[a-zA-Z0-9-_]+/;
    
    channel = integer;
    integer = /[0-9]+/;
    decimal = /(-?(0|[1-9]\d*)?(\.\d+)?(?<=\d)(e-?(0|[1-9]\d*))?|0x[0-9a-f]+)/;
'''

class GEMWalker(tatsu.model.NodeWalker):
    gem = {
        "site": None,
        "node": None,
        "ts": None,
        "voltage": None,
        "channels": {},
        "temperatures": {}
    }

    def walk_object(self, node):
        return node

    def walk__gem(self, node):
        self.gem["site"] = node.site
        self.gem["node"] = node.node
        self.gem["ts"] = node.ts
        for measurement in node.measurements:
            self.walk(measurement)
        return self.gem

    def walk__measurement(self, node):
        return self.walk(node.reading)

    def _get_channel(self, node):
        if node.ch in self.gem["channels"]:
            ch = self.gem["channels"][node.ch]
        else:
            ch = {}
            self.gem["channels"][node.ch] = ch
        return ch

    def walk__energy(self, node):
        self._get_channel(node)["e"] = node.kwh
        return node

    def walk__power(self, node):
        self._get_channel(node)["p"] = node.w
        return node

    def walk__current(self, node):
        self._get_channel(node)["c"] = node.a
        return node

    def walk__temperature(self, node):
        self.gem["temperatures"][node.ch] = node.t
        return node

    def walk__voltage(self, node):
        self.gem["voltage"] = node.v
        return node


def parse(data):
    parser = tatsu.compile(GRAMMAR, asmodel=True)
    model = parser.parse(data)
    return GEMWalker().walk(model)


if __name__ == '__main__':
    gem = parse(EXAMPLE4)
    print(json.dumps(gem, indent=4, sort_keys=True))
