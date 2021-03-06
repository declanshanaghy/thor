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
    for root, dirs, files in os.walk(p):
        fname = random.choice(files)

    # fname = "2019-11-15 18:25:22.038.req.txt"
    # fname = "2019-11-13 temp and voltage.req.txt"
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
    """Load ascii data from file, parse it and send directly to a final destination"""
    data = ascii_data()
    a = asciiwh.ASCIIWH()
    a.data = data

    g = gem.GEMProcessor()
    g.process(a, kinds=(constants.SPLUNK_METRICS,))


def send_ascii_tcp():
    """Sends raw ascii data to a TCP socket. The server will send it on to it's final destination"""
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
        # time.sleep(1)
        # sock.sendall(data)

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
    while True:
        # send_newseg()
        # send_ascii()
        send_ascii_tcp()
        # send_newseg_request()
        # send_ascii_request()

        time.sleep(.6)
