
# Thor

![When it comes to electricity in the Shanaghy household, 
Thor is the all knowing & all mighty of all things](img/thor.jpg)

## Overview

Thor receives data from the [Brultech GreenEye's](http://www.brultech.com/greeneye/) on 
the ground which are producing data using the [ASCII-WH data format](src/data/example_in_tcp_asciiwh.txt) 
and translates that into something [easily usable](src/data/example_out_splunk_metrics.json)
by an an analytics system.

Translation is achieved via the [EBNF](src/data/seg.ebnf) 
parser [tatsu](http://tatsu.readthedocs.io/) using a custom 
[NodeWalker](src/seg.py).

After transformation the data can be sent to multiple sinks for long term 
storage and analytics. 

## Active Data Sinks

 * S3 bucket (Splunk metrics HEC format)
 * Local splunk metrics index

---
### Reference Material
 * [GEM Packet Format Manual](https://www.brultech.com/software/files/getsoft/1/1#man)
   * ASCII-WH details on page 12

# Dependencies

* python 2.7.16