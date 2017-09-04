import os
import datetime
import json

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

            s = seg.parse(data)
            logger.info("Parsed data: %s", s.seg)

            r = splunk.send(s.records, time=s.time,
                            source=s.fq_node, logger=logger)
            logger.info("Splunk response: %s", r)

            web.header('Content-Type', 'application/json')

            ret = {
                seg.TIMESTAMP: s.timestamp,
                seg.SITE: s.site,
                seg.NODE: s.node,
                seg.FQ_NODE: s.fq_node,
                seg.VOLTAGE: s.voltage,
                seg.ELECTRICITY: len(s.seg[seg.ELECTRICITY]),
                seg.TEMPERATURE: len(s.seg[seg.TEMPERATURE]),
            }
            return json.dumps(ret, indent=4, sort_keys=True)
        except Exception as ex:
            logger.error(str(ex), exc_info=True)
            raise web.BadRequest(str(ex))


if __name__ == "__main__":
    urls = (
        '/sites/(.*)', 'Sites'
    )
    app = web.application(urls, globals())
    app.run(log.Log)
