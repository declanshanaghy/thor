import os

import requests

import asciiwh
import gem
import splunk


DATA_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data')


def send_ascii_request():
    with open(os.path.join(DATA_DIR, 'ascii_wh', 'req1.txt')) as f:
        data = f.read()

    response = requests.get("http://localhost:8080/asciiwh/?" + data)
    print(response)


def send_ascii():
    with open(os.path.join(DATA_DIR, 'ascii_wh', 'req1.txt')) as f:
        data = f.read()

    items = data.split("&")
    dct = { i.split("=")[0]: i.split("=")[1] for i in items }
    g = gem.GEM()
    asciiwh.parse(dct, g)

    splunk.send(g)


def send_seg_request():
    with open(os.path.join(DATA_DIR, 'seg', 'req1.txt')) as f:
        data = f.read()

    response = requests.put("http://localhost:8080/sites/local", data=data)
    print(response)


if __name__ == "__main__":
    # send_seg_request()
    send_ascii_request()
    # send_ascii()
