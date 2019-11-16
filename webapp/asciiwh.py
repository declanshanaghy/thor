import logging
import os
import select
import socket
import time

import retrying

import gem
import constants
import logutil

CRS = ("\r", "\n",)
IDLE = 60 * 5


class ASCIIWH(object):
    data = ""
    g = gem.GEMProcessor()
    running = False
    started = False
    server = None
    rxs = {}
    inputs = []

    def parse(self, gem):
        d = {}
        for kvs in self.data.split("&"):
            kv = kvs.split("=")
            if len(kv) == 2:
                d[kv[0]] = kv[1]

        for k, v in d.items():
            if k[:3] == constants.GEM_WHP:
                # Dont allow this to be handled by the else case because a whp
                # field will accidentally be caught by the wh case (ENERGY)
                fltval = float(v)
                logging.info("UNKNOWN FIELD TYPE GEM_WHP %s=%s", k, fltval)
            elif k[:1] == constants.GEM_CURRENT:
                ch = k[2:]
                fltval = float(v)
                gem.set_channel(ch, constants.CURRENT, fltval)
            elif k[:1] == constants.GEM_POWER:
                ch = k[2:]
                fltval = float(v)
                gem.set_channel(ch, constants.POWER, fltval)
            elif k[:2] == constants.GEM_ENERGY:
                ch = k[3:]
                fltval = float(v)
                gem.set_channel(ch, constants.ENERGY, fltval)
            elif k[:1] == constants.GEM_TEMPERATURE:
                ch = k[2:]
                fltval = float(v)
                gem.set_temperature(ch, fltval)
            elif k == constants.GEM_SERIAL:
                gem.set_node(v)
            elif k == constants.GEM_VOLTAGE:
                fltval = float(v)
                gem.voltage = fltval
            elif k == constants.GEM_ELAPSED:
                pass
            else:
                logging.info("UNKNOWN FIELD TYPE k='%s' v='%s'", k, v)

        gem.finalize()

    def format_log(self):
        return self.data

    def kind(self):
        return "asciiwh"

    def shutdown(self):
        logging.info("Shutting down")
        for s in self.inputs:
            self._close(s)

    @retrying.retry(wait_fixed=5000, stop_max_attempt_number=24)
    def _listen(self):
        # Create a TCP/IP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Bind the socket to the port
        server_address = ('0.0.0.0', constants.ASCII_WH_PORT)

        try:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(server_address)
        except socket.error:
            logging.error("Bind failed on %s, will retry", str(server_address))
            raise

        # Listen for incoming connections
        sock.listen(1)
        logging.info("Listening on %s", str(server_address))

        self.server = sock
        self.inputs.append(self.server)

    def process_rx(self, rx):
        if not self.started and rx[0:2] == "n=":
            logging.info({
                "message": "First packet start found",
                "rx": rx,
            })
            self.started = True
        elif not self.started:
            logging.info({
                "message": "Not started",
                "rx": rx,
            })

        for c in CRS:
            cr = rx.find(c)
            if cr > 0:
                self.data += rx[:cr]
                self.data = self.data.strip() # Ensure all CRs are removed
                ret = self.g.process(
                    self,
                    kinds=(constants.SPLUNK_METRICS_SCS,)
                )
                logging.info({
                    "message": "Received result",
                    "result": ret,
                })
                self.data = rx[cr + 1:]
                break
        else:
            self.data += rx

    def _accept(self, s):
        client, client_address = s.accept()
        logging.info('Connection from %s', client_address)
        client.setblocking(0)
        self.inputs.append(client)
        self._rx(client)

    def _client_key(self, s):
        return "%s:%s" % s.getpeername()

    def _rx(self, s):
        k = self._client_key(s)
        logging.info({
            "message": "Received chunk",
            "client": k,
            # "len": len(s),
        })
        self.rxs[k] = (time.time(), s)

    def _close(self, s):
        k = self._client_key(s)
        logging.info('Closing %s', k)

        s.close()
        self.inputs.remove(s)

        if k in self.rxs:
            del self.rxs[k]

    def _process_idle(self):
        tnow = time.time()
        for peer, (t, s) in self.rxs.items():
            logging.info('%s is idle %d secs', peer, tnow - t)
            if t < tnow - IDLE:
                logging.info('%s surpassed idle period', peer)
                self._close(s)

    def run(self):
        self._listen()

        while True:
            try:
                readable, writable, exceptional = select.select(
                    self.inputs, [], [], IDLE)
            except select.error as e:
                logging.exception(e)
                break
            except socket.error as e:
                logging.exception(e)
                break
            except Exception as e:
                logging.exception(e)
                break

            if not readable and not writable and not exceptional:
                self._process_idle()
                continue

            # Handle inputs
            for s in readable:
                if s is self.server:
                    # A "readable" server socket is
                    # ready to accept a connection
                    self._accept(s)
                else:
                    rx = s.recv(2048)
                    self._rx(s)

                    if rx:
                        try:
                            # A readable client socket has data
                            self.process_rx(rx)
                        except:
                            logging.exception(
                                "Unhandled exception processing received data")
                    else:
                        # Interpret empty result as closed connection
                        logging.info("Client closed: %s", s.getpeername())
                        self._close(s)

            # Handle "exceptional conditions"
            for s in exceptional:
                logging.info("Exception from: %s", s.getpeername())
                # Stop listening for input on the connection
                self._close(s)

        self.shutdown()


if __name__ == "__main__":
    logutil.setup_logging(stdout=constants.LOG_STDOUT,
                          log_file=os.path.join(constants.LOG_DIR,
                                                constants.LOG_FILE_ASCIIWH))
    settings = {}
    for s in dir(constants):
        if not '__' in s:
            settings[s] = getattr(constants,s)
    logging.info({
        "settings": settings,
    })
    srv = ASCIIWH()
    try:
        srv.run()
    finally:
        srv.shutdown()
