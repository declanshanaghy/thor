# Thor

When it comes to electricity in the Shanaghy household, 
Thor is the all knowing & all mighty of all things.

Thor receives data from the [GreenEye's](http://www.brultech.com/greeneye/) on 
the ground which are producing data using the [SmartEnergyGroup data format](webapp/data/example_in.seg) 
and translates their that into something [easily usable](webapp/data/example_out_splunk.json)
by an an analytics system.

Translation is achieved via the [EBNF](webapp/data/seg.ebnf) 
parser [tatsu](http://tatsu.readthedocs.io/)

After transformation the data can be sent to multiple sinks for long term 
storage and analytics.

