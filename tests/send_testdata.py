import os

import requests

import asciiwh
import constants
import gem
import seg
import logutil
import splunk


DATA_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data')


def send_ascii():
    with open(os.path.join(DATA_DIR, 'ascii_wh',
                           '2017-11-13 11:02:40.281141.req.txt')) as f:
        data = f.read()

    a = asciiwh.ASCIIWH()
    a.set_data(data)

    g = gem.GEMProcessor()
    g.process(a)


def send_newseg():
    with open(os.path.join(DATA_DIR, 'newseg',
                           '2017-09-03 22:14:36.497417.req')) as f:
        data = f.read()

    p = seg.NEWSEGParser(data)

    g = gem.GEMProcessor()
    g.process(p)


def send_newseg_request():
    with open(os.path.join(DATA_DIR, 'seg', 'req1.txt')) as f:
        data = f.read()

    response = requests.put("http://localhost:8080/sites/local", data=data)
    print(response)


if __name__ == "__main__":
    logutil.setup_logging(stdout=True,
                          log_file=os.path.join(constants.LOG_DIR,
                                                'oneoff.log'))
    send_newseg()
    # send_ascii()
    # send_newseg_request()
    # send_ascii_request()
