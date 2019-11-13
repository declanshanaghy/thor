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
        obj_path = os.path.join(constants.REQ_DIR, filename)

        if constants.LOG_FS_ENABLED:
            logging.info("Logging %s to: %s", kind, obj_path)

            logging.info({
                "message": "Logging to filesystem",
                "kind": kind,
                "path": obj_path,
            })
            with open(obj_path, "w") as f:
                f.write(data)

        if constants.LOG_S3_BUCKET is not None:
            objectname = os.path.join(constants.LOG_S3_DATAPATH, kind,
                                      filename)
            logging.info({
                "message": "Logging to S3",
                "kind": kind,
                "path": obj_path,
                "S3_BUCKET": constants.LOG_S3_BUCKET,
                "objectname": objectname,
            })

            # Upload the file
            s3_client = boto3.client('s3')
            try:
                response = s3_client.upload_file(obj_path, constants.LOG_S3_BUCKET,
                                                 objectname)
                logging.debug("Response from s3: %s", response)
            except botocore.exceptions.ClientError as e:
                logging.error(e)

