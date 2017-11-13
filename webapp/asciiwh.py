import socket

import app
import constants

class ASCIIWH(object):
    data = None
    gem = None

    def set_data(self, data):
        print('Full packet:', data)
        self.data = data

    def parse(self, gem):
        xyz = self.data
        self.data = {}
        for kvs in xyz.split("&"):
            kv = kvs.split("=")
            if len(kv) == 2:
                self.data[kv[0]] = kv[1]

        for k, v in self.data.items():
            fltval = float(v)
            if k[:3] == constants.GEM_WHP:
                # Dont allow this to be handled by the else case because a whp
                # field will accidentally be caught by the wh case (ENERGY)
                print("UNKNOWN FIELD TYPE %s=%s", k, fltval)
            elif k[:1] == constants.GEM_CURRENT:
                ch = k[2:]
                gem.set_channel(ch, constants.CURRENT, fltval)
            elif k[:1] == constants.GEM_POWER:
                ch = k[2:]
                gem.set_channel(ch, constants.POWER, fltval)
            elif k[:2] == constants.GEM_ENERGY:
                ch = k[3:]
                gem.set_channel(ch, constants.ENERGY, fltval)
            elif k[:1] == constants.GEM_TEMPERATURE:
                ch = k[2:]
                gem.set_temperature(ch, fltval)
            elif k == constants.GEM_SERIAL:
                gem.set_node(v)
            elif k == constants.GEM_VOLTAGE:
                gem.voltage = fltval
            elif k == constants.GEM_ELAPSED:
                pass
            else:
                print("UNKNOWN FIELD TYPE %s=%s", k, fltval)

    def format_log(self):
        return self.data
        # return "&".join("%s=%s" % (k, v) for k, v in self.data.items())

    def run(self):
        # Create a TCP/IP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Bind the socket to the port
        server_address = ('0.0.0.0', 8080)
        print('starting up on %s port %s' % server_address)
        sock.bind(server_address)

        # Listen for incoming connections
        sock.listen(1)

        gem = app.GEMReceiver()

        while True:
            # Wait for a connection
            print('waiting for a connection')
            connection, client_address = sock.accept()
            started = False

            try:
                print('connection from', client_address)
                data = ""

                while True:
                    rx = connection.recv(1024)
                    print('received "%s"' % rx)
                    if not started and rx[0:2] == "n=":
                        print("Started")
                        started = True
                    elif not started:
                        print("Not started. Not n=")
                        continue

                    cr = rx.find("\n")
                    if cr > 0:
                        data += rx[:cr]
                        self.set_data(data)
                        ret = gem.proc(self)
                        print(ret)
                        data = rx[cr+1:]
                    else:
                        data += rx
            finally:
                # Clean up the connection
                connection.close()

if __name__ == "__main__":
    server = ASCIIWH()
    server.run()
