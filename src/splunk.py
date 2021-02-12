import os
import collections
import constants
import glob
import json
import logging
import time

import requests
import requests.auth
import utils
import scs_auth

# SPLUNK_HEC_URL = "http://thor.shanaghy.com:8088/services/collector"
SPLUNK_HEC_URL = "http://" + os.getenv("HEC_HOST", "cribl") + ":10080/services/collector"

# HEC_TOKEN = "B840C47D-FDF9-4C94-AD7F-EC92FD289204"
# DEFAULT_HEADERS = {"Authorization": "Splunk " + HEC_TOKEN}
DEFAULT_HEADERS = {}

CREDSFILE_RAW = os.path.join(constants.CREDS_DIR, "credentials.raw")
CREDSFILE_TOKEN = os.path.join(constants.CREDS_DIR, "credentials.token")


class SplunkHandler(object):
    knd = None
    gem = None
    index = None
    source = None
    sourcetype = None
    records = []
    logger = None

    def __init__(self, gem, kind="unknown", index="main",
                 source=None, sourcetype=None, logger=None):
        self.kind = kind
        self.gem = gem
        self.index = index
        self.source = source
        self.sourcetype = sourcetype
        self.logger = logger
        self._create_records()

    def _create_records(self):
        raise NotImplementedError(
            "Subclasses must implemement _create_records")

    def _create_post_data(self):
        raise NotImplementedError(
            "Subclasses must implemement _create_post_data")

    def _get_api_data(self):
        return {
            "url": SPLUNK_HEC_URL,
            "headers": DEFAULT_HEADERS,
        }

    def send(self, logger=None):
        if not logger:
            logger = logging

        hostdata = self._get_api_data()

        data = self._create_post_data()
        utils.log_data(self.kind, data)

        logger.info({
            "message": "posting for " + self.__class__.__name__,
            "hec_url": hostdata['url'],
            "index": self.index,
            "source": self.source,
            "sourcetype": self.sourcetype,
        })
        r = requests.post(hostdata['url'],
                          data=data, headers=hostdata['headers'])

        logger.info("response: %s", r)
        if r.status_code == 200:
            body = r.text
            logger.info({
                "message": "splunk post succeeded",
                "response": body
            })
            return r.json()
        else:
            request_id = r.headers["x-request-id"]
            raise StandardError("request_id=%s, status_code=%s, body=%s" % (request_id, r.status_code, r.text))


class SplunkEventsHandler(SplunkHandler):
    gem = None
    records = None

    def __init__(self, gem, *args, **kwargs):
        super(SplunkEventsHandler, self).__init__(gem,
                                                  kind=constants.SPLUNK_EVENTS,
                                                  index="thorevents",
                                                  *args, **kwargs)

    def _create_records(self):
        self.records = [
            ", ".join([
                'site="' + self.gem.site + '"',
                'node="' + self.gem.node + '"',
                'type="' + constants.VOLTAGE + '"',
                constants.VOLTAGE + '=' + str(self.gem.voltage),
            ])
        ]

        for data in self.gem.electricity:
            self.records.append(", ".join([
                'site="' + self.gem.site + '"',
                'node="' + self.gem.node + '"',
                'type="' + constants.ELECTRICITY + '"',
                constants.CHANNEL_NAME + '="' + str(
                    data[constants.CHANNEL_NAME]) + '"',
                constants.CHANNEL_NUMBER + '=' + str(
                    data[constants.CHANNEL_NUMBER]),
                constants.POWER + '=' + str(data[constants.POWER]),
                constants.CURRENT + '=' + str(data[constants.CURRENT]),
                constants.ENERGY + '=' + str(data[constants.ENERGY])
            ]))

        for data in self.gem.temperature:
            self.records.append(", ".join([
                'site="' + self.gem.site + '"',
                'node="' + self.gem.node + '"',
                'type="' + constants.TEMPERATURE + '"',
                constants.CHANNEL_NAME + '="' + str(
                    data[constants.CHANNEL_NAME]) + '"',
                constants.TEMPERATURE + '=' + str(data[constants.TEMPERATURE]),
            ]))

    def _create_post_data(self):
        events = []
        for record in self.records:
            d = collections.OrderedDict()
            if self.gem.time:
                d["time"] = self.gem.time
            if self.index:
                d["index"] = self.index
            if self.source:
                d["source"] = self.source
            if self.sourcetype:
                d["sourcetype"] = self.sourcetype
            d["event"] = record

            events.append(json.dumps(d, indent=4))

        return "\n".join(events)


class SplunkMetricsHandler(SplunkHandler):
    def __init__(self, gem, index="thormetrics", *args, **kwargs):
        super(SplunkMetricsHandler, self).__init__(
            gem, kind=constants.SPLUNK_METRICS, index=index, *args, **kwargs)

    def _create_records(self):
        default_dimensions = {
            "site": self.gem.site,
            "node": self.gem.node,
        }
        m = {
            "metric_name": "voltage",
            "_value": self.gem.voltage,
        }
        m.update(default_dimensions)

        self.records = [m]

        for data in self.gem.electricity:
            for metric in [constants.CURRENT, constants.POWER,
                         constants.ENERGY]:
                m = {
                    "metric_name": metric,
                    "_value": data[metric],
                    constants.CHANNEL_NUMBER: data.get(constants.CHANNEL_NUMBER, ""),
                    constants.CHANNEL_NAME: data.get(constants.CHANNEL_NAME,""),
                }
                m.update(default_dimensions)
                m.update(data["dimensions"])
                self.records.append(m)

        for data in self.gem.temperature:
            m = {
                "metric_name": constants.TEMPERATURE,
                "_value": data[constants.TEMPERATURE],
                constants.CHANNEL_NUMBER: data.get(constants.CHANNEL_NUMBER,
                                                   ""),
                constants.CHANNEL_NAME: data.get(constants.CHANNEL_NAME, ""),
            }
            m.update(default_dimensions)
            self.records.append(m)

    def _create_post_data(self):
        events = []
        for record in self.records:
            d = collections.OrderedDict()
            if self.gem.time:
                d["time"] = self.gem.time
            if self.index:
                d["index"] = self.index
            if self.source:
                d["source"] = self.source
            if self.sourcetype:
                d["sourcetype"] = self.sourcetype
            d["event"] = "metric"
            d["fields"] = record

            events.append(json.dumps(d))

        return "\n".join(events)


class SplunkMetricsSCSHandler(SplunkMetricsHandler):
    api_host = None
    authn_host = None
    tenant = None
    environment = ""
    tokencreds = None

    def __init__(self, gem, tenant, environment="", *args, **kwargs):
        super(SplunkMetricsSCSHandler, self).__init__(
            gem, index="", *args, **kwargs)

        self.tenant = tenant
        self.environment = environment

        env = ""
        if environment != "production":
            env += environment + "."

        self.api_host = "api." + env + "scp.splunk.com"
        self.authn_host = "auth." + env + "scp.splunk.com"

        extn = ".".join(["", environment, tenant, 'json'])
        self.credsfile_raw = os.path.join(CREDSFILE_RAW) + extn
        self.credsfile_token = os.path.join(CREDSFILE_TOKEN) + extn

    def _get_api_data(self):
        self._ensure_credentials()
        return {
            "url": "https://" + self.api_host + "/" + self.tenant + "/ingest/v1beta2/metrics",
            "headers": {
                "Authorization": "Bearer " + self.tokencreds["access_token"]},
            "content-type": "application/json",
        }

    def _load_credentials_raw(self):
        logging.info("Attempting to load credentials from " + self.credsfile_raw)
        with open(self.credsfile_raw) as raw:
            rawcreds = json.load(raw)
        return rawcreds

    def _load_token(self):
        logging.info("Attempting to load token from " + self.credsfile_token)
        with open(self.credsfile_token) as raw:
            return json.load(raw)

    def _save_token(self, tokencreds):
        logging.info("Saving token to " + self.credsfile_token)
        with open(self.credsfile_token, "w") as tokfile:
            tokfile.write(json.dumps(tokencreds, indent=4))

    def _mint_token(self, rawcreds):
        logging.warn({
            "message": "Minting new token",
            "clientId": rawcreds["clientId"],
        })

        mgr = scs_auth.ClientAuthManager(
            host=self.authn_host,
            client_id=rawcreds["clientId"],
            client_secret=rawcreds["clientSecret"]
        )

        token = mgr.authenticate()

        safteynet = 60 * 10
        tnow = int(time.time())
        token['expires_at'] = tnow + token['expires_in'] - safteynet
        logging.warn({
            "message": "Minted new token",
            "access_token": token['access_token'][:12],
            "expires_in": token['expires_in'],
            "expires_at": token['expires_at'],
        })
        return token

    def _check_token_expiration(self):
        if self.tokencreds is not None:
            expires = self.tokencreds.get('expires_at', 0)
            if time.time() > expires:
                logging.warn({
                    "message": "Token expired",
                    "access_token": self.tokencreds["access_token"][
                                    :12] + "...",
                })
                self.tokencreds = None

    def _ensure_credentials(self):
        if self.tokencreds is not None:
            self._check_token_expiration()

        if self.tokencreds is None:
            try:
                self.tokencreds = self._load_token()
                self._check_token_expiration()
            except IOError:
                pass

        if self.tokencreds is None:
            rawcreds = self._load_credentials_raw()
            self.tokencreds = self._mint_token(rawcreds)
            self._save_token(self.tokencreds)

        if not self.tokencreds.get("access_token"):
            raise StandardError("Non existent access token")

        logging.warn({
            "message": "Using token",
            "access_token": self.tokencreds["access_token"][:12] + "...",
        })

    def _create_records(self):
        m = {
            "name": constants.VOLTAGE,
            "value": self.gem.voltage,
            "unit": constants.UNITS[constants.VOLTAGE],
        }
        self.records = [m]

        for data in self.gem.electricity:
            for metric in [constants.CURRENT, constants.POWER,
                         constants.ENERGY]:
                m = {
                    "name": metric,
                    "value": data[metric],
                    "unit": constants.UNITS[metric],
                    "dimensions": data["dimensions"]
                }
                self.records.append(m)

        for data in self.gem.temperature:
            m = {
                "name": constants.TEMPERATURE,
                "value": data[constants.TEMPERATURE],
                "unit": constants.UNITS[constants.TEMPERATURE],
                "dimensions": {
                    constants.CHANNEL_NUMBER: data.get(
                        constants.CHANNEL_NUMBER, ""),
                    constants.CHANNEL_NAME: data.get(
                        constants.CHANNEL_NAME, ""),
                }
            }
            self.records.append(m)

    def _create_post_data(self):
        if not self.records:
            return None

        data = [
            {
                "timestamp": self.gem.time_millis,
                "source": self.source,
                "sourcetype": self.sourcetype,
                "host": self.gem.fq_node,
                "attributes": {
                    "defaultDimensions": {
                        "node": self.gem.node,
                        "site": self.gem.site,
                    }
                },
                "body": self.records
            }
        ]

        return json.dumps(data, indent=4)


def send(gem, kinds=None, source=None, logger=None):
    if not logger:
        logger = logging

    handlers = []
    for kind in kinds:
        if kind == constants.SPLUNK_EVENTS:
            handlers.append(SplunkEventsHandler(gem, source=source,
                                                sourcetype='electricity-events',
                                                logger=logger))
        elif kind == constants.SPLUNK_METRICS:
            handlers.append(SplunkMetricsHandler(gem, source=source,
                                                 sourcetype='electricity-metrics',
                                                 logger=logger))
        elif kind == constants.SPLUNK_METRICS_SCS:
            pattern = CREDSFILE_RAW + ".*"
            configs = glob.glob(pattern)
            logger.info({
                "message": "Loading credentials",
                "n": len(configs),
                "pattern": pattern,
            })
            for config in configs:
                parts = config.split(".")
                tenant = parts[-2]
                environment = parts[-3]
                handlers.append(SplunkMetricsSCSHandler(
                    gem, tenant, environment=environment,
                    source=source, sourcetype='electricity-events', logger=logger))

    success = True
    for handler in handlers:
        try:
            if handler.send(logger=logger):
                logger.info({
                    "message": "Indexing succeeded",
                    "kind": kind,
                })
            else:
                logger.info({
                    "message": "Indexing failed",
                    "kind": kind,
                })
                success = False
        except StandardError as ex:
            logger.exception({
                "message": "Indexing caused exception",
                "kind": kind,
                "ex": ex,
            })
            success = False

    return success
