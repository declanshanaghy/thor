import os
import socket

import requests

import asciiwh
import constants
import gem
import seg
import logutil


DATA_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data')


def send_ascii():
    with open(os.path.join(DATA_DIR, 'ascii_wh',
                           '2017-11-13 11:02:40.281141.req.txt')) as f:
        data = f.read()

    a = asciiwh.ASCIIWH()
    a.set_data(data)

    g = gem.GEMProcessor()
    g.process(a)


def send_ascii_tcp():
    with open(os.path.join(DATA_DIR, 'ascii_wh',
                           '2017-11-13 11:02:40.281141.req.txt')) as f:
        data = f.read()

    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("127.0.0.1", 8888))
    # if not data[-1:] == "\n":
    #     data += "\n"

    l = len(data)
    pieces = [
        data[:l / 3],
        data[l / 3 : 2 * l / 3],
        data[2 * l / 3 : l]
    ]
    for piece in pieces:
        sock.send(piece)

    sock.close()


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
    # send_newseg()
    # send_ascii()
    send_ascii_tcp()
    # send_newseg_request()
    # send_ascii_request()
