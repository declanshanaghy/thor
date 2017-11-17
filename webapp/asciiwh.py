import logging
import os
import socket
import time

import gem
import constants
import logutil


CRS = ("\r", "\n", )


class ASCIIWH(object):
    data = None
    gem = None

    def set_data(self, data):
        logging.info('Full packet: %s', data)
        self.data = data

    def parse(self, gem):
        xyz = self.data
        self.data = {}
        for kvs in xyz.split("&"):
            kv = kvs.split("=")
            if len(kv) == 2:
                self.data[kv[0]] = kv[1]

        for k, v in self.data.items():
            if k[:3] == constants.GEM_WHP:
                # Dont allow this to be handled by the else case because a whp
                # field will accidentally be caught by the wh case (ENERGY)
                fltval = float(v)
                logging.info("UNKNOWN FIELD TYPE %s=%s", k, fltval)
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
                logging.info("UNKNOWN FIELD TYPE %s=%s", k, v)

        gem.finalize()

    def format_log(self):
        return self.data

    def _listen(self):
        tsleep = 10
        tries = 1
        max_tries = 10
        g = gem.GEMProcessor()

        # Create a TCP/IP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Bind the socket to the port
        server_address = ('0.0.0.0', constants.ASCII_WH_PORT)

        while tries <= max_tries:
            try:
                logging.info("Attempting to bind %s", str(server_address))
                sock.bind(server_address)
                break
            except socket.error:
                if tries >= max_tries:
                    raise
                else:
                    logging.warn("Failed to bind on %s. Attempt %d of %d",
                                 str(server_address), tries, max_tries)
                    tries += 1
                    logging.warn("Sleeping " + str(tsleep))
                    time.sleep(tsleep)

        # Listen for incoming connections
        logging.info("Bound to %s. Attempting listen", str(server_address))
        sock.listen(1)
        return sock


    def run(self):
        g = gem.GEMProcessor()

        while True:
            server = self._listen()

            # Wait for a connection
            logging.info('Waiting for accept')
            client, client_address = server.accept()

            try:
                started = False
                logging.info('Connection from %s', client_address)
                data = ""

                while True:
                    rx = client.recv(1024)
                    if not rx:
                        logging.info("Client closed")
                        break

                    logging.info('Received "%s"' % rx)
                    if not started and rx[0:2] == "n=":
                        logging.info("New packet started")
                        started = True
                    elif not started:
                        logging.info("Not started. rx=%s", rx)
                        continue

                    for c in CRS:
                        cr = rx.find(c)
                        if cr > 0:
                            data += rx[:cr]
                            self.set_data(data)
                            ret = g.process(self)
                            if ret:
                                logging.info(ret)
                            data = rx[cr+1:]
                            break
                    else:
                        data += rx
            except StandardError as ex:
                logging.exception(ex)
            finally:
                # Clean up the connection
                logging.info("Shutting down")
                client.close()
                server.close()


if __name__ == "__main__":
    logutil.setup_logging(stdout=True,
                          log_file=os.path.join(constants.LOG_DIR,
                                                constants.LOG_FILE_ASCIIWH))
    server = ASCIIWH()
    server.run()
