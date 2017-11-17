from wsgilog import WsgiLog

import constants


LOG_FORMAT = [
    '%(asctime)s',
    'level=%(levelname)s',
    'comp=%(name)s',
    'loc=%(module)s:%(lineno)d',
    '%(message)s'
]


class Log(WsgiLog):
    def __init__(self, application):
        WsgiLog.__init__(
            self,
            application,
            logformat=' '.join(LOG_FORMAT),
            tofile = True,
            toprint = True,
            tostream = True,
            file = constants.LOG_FILE_WEB,
        )
