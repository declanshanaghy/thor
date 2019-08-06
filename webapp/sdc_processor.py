import logging
import requests
import os

import constants
import logutil
import oidc


DATA_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'logs', 'requests')


class SDCProcessor(object):

    def get_token(self):
        pass

    def get_data(self):
        fname = ""
        p = os.path.join(DATA_DIR)
        # for root, dirs, files in os.walk(p):
        #     fname = random.choice(files)

        fname = "20181002T003847UTC.req.txt"
        with open(os.path.join(p, fname)) as f:
            yield f.read()

    def shutdown(self):
        logging.info("Shutting down")

    def send_metrics(self, tenant, event, token):
        headers = {"Authorization": "Bearer " + token}
        data = [
            {
                "body"
            }
        ]
        r = requests.post('https://api.splunkbeta.com/' + tenant + '/ingest/v1beta1/metrics',
                          data=data, headers=headers)
        if r.status_code != 200:
            raise StandardError("Error %s: %s" % (r.status_code, r.text))

    def run(self):
        cid = os.environ['CLIENT_ID']
        csecret = os.environ['CLIENT_SECRET']
        tenant = os.environ['TENANT']

        logging.info("Starting up")
        client = oidc.OIDCClient(constants.STAGING_IDP_HOST,
                                 constants.STAGING_IDP_AUTHSERVER)
        while True:
            try:
                token = client.client_credentials(cid, csecret)
                for data in self.get_data():
                    logging.info("Read %s", data)
                    self.send_metrics(data, tenant, token)
            except Exception as e:
                logging.exception(e)
                break


        self.shutdown()


if __name__ == "__main__":
    logutil.setup_logging(stdout=True,
                          log_file=os.path.join(constants.LOG_DIR,
                                                constants.LOG_FILE_ASCIIWH))
    srv = SDCProcessor()
    try:
        srv.run()
    finally:
        srv.shutdown()
