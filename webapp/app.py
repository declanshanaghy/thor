import os
import datetime
import json
import logging

import web

import log
import constants
import seg
import splunk


class Sites:
    def PUT(self, site):
        logger = web.ctx.env.get('wsgilog.logger')
        logger.info("Processing site: %s", site)

        try:
            data = web.data()
            logger.info("Received data: %s", data)

            if constants.LOG_REQUESTS:
                n = "%s.req" % datetime.datetime.now()
                p = os.path.join(constants.REQ_DIR, n)
                logger.info("Logging request to: %s", p)
                with open(p, "w") as f:
                    f.write(data)

            g = seg.parse(data)
            j = json.dumps(g, indent=4)

            logger.info("Parsed data: %s", g)

            r = splunk.send(g)
            logger.info("Splunk response: %s", r)

            web.header('Content-Type', 'application/json')
            return j
        except Exception as ex:
            logger.error(str(ex), exc_info=True)
            raise web.BadRequest(str(ex))


if __name__ == "__main__":
    urls = (
        '/sites/(.*)', 'Sites'
    )
    app = web.application(urls, globals())
    app.run(log.Log)
