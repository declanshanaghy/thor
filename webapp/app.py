import os
import datetime
import json

import web

import log

import asciiwh
import constants
import seg
import gem
import splunk


class SEGReceiver:
    def PUT(self, site):
        logger = web.ctx.env.get('wsgilog.logger')
        logger.info("Processing site: %s", site)

        try:
            data = web.data()
            logger.info("Received data: %s", data)

            if constants.LOG_REQUESTS:
                n = "%s.req.txt" % datetime.datetime.now()
                p = os.path.join(constants.REQ_DIR, n)
                logger.info("Logging request to: %s", p)
                with open(p, "w") as f:
                    f.write(data)

            g = gem.GEM()
            seg.parse(data, g)
            logger.info("Parsed GEM: %s", g)
            splunk.send(g, logger=logger)

            web.header('Content-Type', 'application/json')
            ret = {
                constants.TIMESTAMP: g.timestamp,
                constants.SITE: g.site,
                constants.NODE: g.node,
                constants.FQ_NODE: g.fq_node,
                constants.VOLTAGE: g.voltage,
                constants.ELECTRICITY: len(g.electricity),
                constants.TEMPERATURE: len(g.temperature),
            }
            return json.dumps(ret, indent=4, sort_keys=True)
        except Exception as ex:
            logger.error(str(ex), exc_info=True)
            raise web.BadRequest(str(ex))


class ASCIIWHReceiver:
    def GET(self, arse=None):
        logger = web.ctx.env.get('wsgilog.logger')

        try:
            data = web.input()
            logger.info("Received data: %s", data)

            if constants.LOG_REQUESTS:
                n = "%s.req.txt" % datetime.datetime.now()
                p = os.path.join(constants.REQ_DIR, n)
                logger.info("Logging request to: %s", p)
                s = "&".join("%s=%s" % (k, v) for k, v in data.items())
                with open(p, "w") as f:
                    f.write(s)

            g = gem.GEM()
            asciiwh.parse(data, g)
            logger.info("Parsed data: %s", g)
            splunk.send(g, logger=logger)

            web.header('Content-Type', 'application/json')
            ret = {
                constants.TIMESTAMP: g.timestamp,
                constants.SITE: g.site,
                constants.NODE: g.node,
                constants.FQ_NODE: g.fq_node,
                constants.VOLTAGE: g.voltage,
                constants.ELECTRICITY: len(g.electricity),
                constants.TEMPERATURE: len(g.temperature),
            }
            return json.dumps(ret, indent=4, sort_keys=True)
        except Exception as ex:
            logger.error(str(ex), exc_info=True)
            raise web.BadRequest(str(ex))


if __name__ == "__main__":
    urls = (
        '/asciiwh', 'ASCIIWHReceiver',
        '/asciiwh/(.*)', 'ASCIIWHReceiver',
        '/newseg/(.*)', 'SEGReceiver',
        '/sites/(.*)', 'SEGReceiver'
    )
    app = web.application(urls, globals())
    app.run(log.Log)
