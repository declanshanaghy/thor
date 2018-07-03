import logging
import os
import random
import socket
import time

import requests

import asciiwh
import constants
import gem
import seg
import logutil


DATA_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data')


def ascii_data():
    fname = ""
    p = os.path.join(DATA_DIR, 'ascii_wh')
    # for root, dirs, files in os.walk(p):
    #     fname = random.choice(files)

    fname = "2018-02-25 14:49:42.057508.req.txt"
    with open(os.path.join(p, fname)) as f:
        return f.read()


def newseg_data():
    p = os.path.join(DATA_DIR, 'newseg')
    for root, dirs, files in os.walk(p):
        fname = random.choice(files)

    fname = "x.req"
    with open(os.path.join(p, fname)) as f:
        return f.read()


def send_ascii():
    data = ascii_data()
    a = asciiwh.ASCIIWH()
    a.data = data

    g = gem.GEMProcessor()
    g.process(a, type=constants.SPLUNK_METRICS)


def send_ascii_tcp():
    data = ascii_data()

    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    addr = (os.environ.get("ASCII_WH_HOST", "127.0.0.1"),
            constants.ASCII_WH_PORT)

    try:
        sock.connect(addr)
        logging.info("Connected to: %s", addr)

        logging.info("Send: %s", data)
        sock.sendall(data)

        time.sleep(99999)
    finally:
        sock.close()


def send_newseg():
    data = newseg_data()
    p = seg.NEWSEGParser(data)

    g = gem.GEMProcessor()
    g.process(p)


def send_newseg_request():
    data = newseg_data()
    response = requests.put("http://localhost:8080/sites/local", data=data)
    print(response)


if __name__ == "__main__":
    logutil.setup_logging(stdout=True,
                          log_file=os.path.join(constants.LOG_DIR,
                                                'oneoff.log'))
    # send_newseg()
    # send_ascii()
    send_ascii_tcp()
    # send_newseg_request()
    # send_ascii_request()
