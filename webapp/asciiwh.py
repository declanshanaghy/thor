import logging
import os
import select
import socket
import time

import gem
import constants
import logutil


CRS = ("\r", "\n", )


class ASCIIWH(object):
    data = ""
    g = gem.GEMProcessor()
    running = False
    started = False

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
        sock.listen(1)
        logging.info("Listening on %s", str(server_address))
        return sock


    def run_simple(self):
        while True:
            server = self._listen()

            # Wait for a connection
            logging.info('Waiting for accept')
            client, client_address = server.accept()

            try:
                logging.info('Connection from %s', client_address)
                while True:
                    rx = client.recv(1024)
                    if rx:
                        self.process_rx(rx)
                    else:
                        logging.info("Client closed")
                        client.close()
                        break
            except StandardError as ex:
                logging.exception(ex)
            finally:
                # Clean up the connection
                logging.info("Shutting down")
                client.close()
                server.close()


    def process_rx(self, rx):
        logging.info('Received "%s"' % rx)
        if not self.started and rx[0:2] == "n=":
            logging.info("New packet started")
            self.started = True
        elif not self.started:
            logging.info("Not started. rx=%s", rx)

        for c in CRS:
            cr = rx.find(c)
            if cr > 0:
                self.data += rx[:cr]
                ret = self.g.process(
                    self, type=constants.SPLUNK_METRICS)
                if ret:
                    logging.info(ret)
                self.data = rx[cr + 1:]
                break
        else:
            self.data += rx

    def run(self):
        while True:
            server = self._listen()
            inputs = [server]

            while True:
                try:
                    readable, writable, exceptional = select.select(
                        inputs, [], [], 0.25)
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
                    logging.debug("timeout")
                    continue

                # Handle inputs
                for s in readable:
                    if s is server and len(inputs) > 1:
                        logging.warn('Ignoring subsequent connection')
                    elif s is server and len(inputs) == 1:
                        # A "readable" server socket is ready to accept a connection
                        connection, client_address = s.accept()
                        logging.info('Connection from %s', client_address)
                        connection.setblocking(0)
                        inputs.append(connection)
                    else:
                        rx = s.recv(1024)
                        if rx:
                            # A readable client socket has data
                            self.process_rx(rx)
                        else:
                            # Interpret empty result as closed connection
                            logging.info("Client closed: %s", s.getpeername())
                            inputs.remove(s)
                            s.close()

                # Handle "exceptional conditions"
                for s in exceptional:
                    logging.info("Exception from: %s", s.getpeername())
                    # Stop listening for input on the connection
                    inputs.remove(s)
                    s.close()


if __name__ == "__main__":
    logutil.setup_logging(stdout=True,
                          log_file=os.path.join(constants.LOG_DIR,
                                                constants.LOG_FILE_ASCIIWH))
    server = ASCIIWH()
    server.run()
