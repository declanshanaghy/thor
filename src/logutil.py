import errno
import logging
import logging.handlers
import os
import re
import sys

import constants


def setup_logging(stdout=True, log_file=None):
    class DictFormatter(logging.Formatter):
        SECURE_LOG_KEEP_CHARS = ['-', ',', ':', ';', '\s']
        REDACT_WORDS = ['secret']

        def __init__(self, fmt=None, datefmt=None, secure_log=True):
            super(DictFormatter, self).__init__(fmt, datefmt)
            self.secure_log = secure_log

        @staticmethod
        def _dict_to_log_format(d, secure_log=True):
            s = ''
            for k, v in d.items():
                if secure_log:
                    not_replaced_chars = r'[^%s]' % ''.join(
                        DictFormatter.SECURE_LOG_KEEP_CHARS)
                    for secret_key_word in DictFormatter.REDACT_WORDS:
                        if secret_key_word in k:
                            v = re.sub(not_replaced_chars, '*', v)
                if s:
                    s += ' '
                s += '%s="%s"' % (k, v)
            return s

        def format(self, record, secure_log=True):
            if isinstance(record.msg, dict):
                record.msg = self._dict_to_log_format(record.msg,
                                                      self.secure_log)

            logformat = logging.Formatter.format(self, record)
            return logformat

    log_level = logging.INFO
    if constants.LOG_LEVEL == "debug":
        log_level = logging.DEBUG

    messages = []
    messages.append("log level is " + str(constants.LOG_LEVEL))

    # Set up the root logger.
    logger = logging.getLogger()
    logger.setLevel(log_level)

    fragments = [
        '%(asctime)s',
        '%(levelname)s',
        '%(threadName)s',
        '%(name)s',
        '%(module)s:%(lineno)d',
        '%(message)s',
    ]
    format = ' '.join(fragments)

    if stdout:
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(log_level)
        logger.addHandler(ch)
        formatter = DictFormatter(format, secure_log=True)
        ch.setFormatter(formatter)
        messages.append("Logging to stdout")

    if log_file:
        abs_log_filename = os.path.abspath(log_file)
        log_dir = os.path.dirname(abs_log_filename)
        if not os.path.exists(log_dir):
            try:
                os.makedirs(log_dir)
            except OSError as ex:
                # OSError: [Errno 17] File exists
                if ex.errno in [errno.EEXIST, ]:
                    pass
                else:
                    raise

        handler_cls = logging.handlers.RotatingFileHandler
        handler = handler_cls(abs_log_filename, maxBytes=1024 * 1024 * 10,
                              backupCount=2)
        formatter = DictFormatter(format, secure_log=True)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        messages.append("Logging to " + log_file)

    # Disable stupidly verbose INFO messages
    WARN_PKGS = [
        'requests.packages.urllib3.connectionpool',
        'boto3.resources.action',
        'botocore.vendored.requests.packages.urllib3.connectionpool'
    ]
    for pkg in WARN_PKGS:
        logging.getLogger(pkg).setLevel(logging.WARNING)

    for msg in messages:
        logging.info(msg)
