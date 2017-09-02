import tatsu
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
    measurement::Measurement = '(' reading:(power|current|temperature|voltage) ')';
    
    power::Power = 'p_' ch:channel w:decimal;
    current::Current = 'a_' ch:channel a:decimal;
    temperature::Temperature = 'temperature_' ch:channel t:('x'|decimal);
    voltage::Voltage = 'voltage' v:decimal;
    
    identifier = /[a-z0-9]+/;
    
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


if __name__ == '__main__':
    parser = tatsu.compile(GRAMMAR, asmodel=True)
    model = parser.parse(EXAMPLE2)

    print('# WALKER RESULT')
    result = GEMWalker().walk(model)
    print(result)
