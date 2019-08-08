import logging
import os
import time
import json

import boto3
import botocore.exceptions

import constants


def load_data(file):
    n = os.path.join(constants.DATA_DIR, file)
    with open(n) as f:
        return f.read()


def load_yaml(file):
    n = os.path.join(constants.DATA_DIR, file)
    with open(n) as f:
        return json.load(f)

def log_data(kind, data):
    if constants.LOG_REQUESTS is not None and kind in constants.LOG_REQUESTS:
        t = time.time()
        st = time.strftime("%Y%m%dT%H%M%S%Z", time.gmtime(t))
        filename = "%s.%s.txt" % (st, kind)
        fspath = os.path.join(constants.REQ_DIR, filename)
        logging.info("Logging %s to: %s", kind, fspath)

        logging.info({
            "message": "Logging to filesystem",
            "kind": kind,
            "fspath": fspath,
        })
        with open(fspath, "w") as f:
            f.write(data)

        if constants.S3_BUCKET is not None:
            objectname = os.path.join(constants.S3_DATAPATH, kind,
                                      filename)
            logging.info({
                "message": "Logging to S3",
                "kind": kind,
                "fspath": fspath,
                "S3_BUCKET": constants.S3_BUCKET,
                "objectname": objectname,
            })

            # Upload the file
            s3_client = boto3.client('s3')
            try:
                response = s3_client.upload_file(fspath, constants.S3_BUCKET,
                                                 objectname)
                logging.debug("Response from s3: %s", response)
            except botocore.exceptions.ClientError as e:
                logging.error(e)

