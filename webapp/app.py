import os
import datetime
import json
import logging

import web

import constants
import seg
import gem
import log
import splunk


class GEMReceiver(object):
    def proc(self, parser, logger=None):
        if not logger:
            logger = logging

        logger.info("Received data: %s", parser.data)

        if constants.LOG_REQUESTS:
            n = "%s.req.txt" % datetime.datetime.now()
            p = os.path.join(constants.REQ_DIR, n)
            logger.info("Logging request to: %s", p)
            with open(p, "w") as f:
                f.write(parser.format_log())

        g = gem.GEM()
        parser.parse(g)
        g.finalize()

        logger.info("Parsed GEM: %s", g)
        splunk.send(g, logger=logger)

        return {
            constants.TIMESTAMP: g.timestamp,
            constants.SITE: g.site,
            constants.NODE: g.node,
            constants.FQ_NODE: g.fq_node,
            constants.VOLTAGE: g.voltage,
            constants.ELECTRICITY: len(g.electricity),
            constants.TEMPERATURE: len(g.temperature),
        }


class NewSEGReceiver(GEMReceiver):
    def PUT(self, site):
        logger = web.ctx.env.get('wsgilog.logger')
        logger.info("Processing NewSEG. site=%s", site)

        try:
            data = web.data()
            parser = seg.NEWSEGParser(data)
            ret = self.proc(parser, logger=logger)
            return json.dumps(ret, indent=4, sort_keys=True)
        except Exception as ex:
            logger.error(str(ex), exc_info=True)
            raise web.BadRequest(str(ex))


if __name__ == "__main__":
    urls = (
        '(.*)', 'ASCIIWHReceiver',
        '/asciiwh', 'ASCIIWHReceiver',
        '/asciiwh/(.*)', 'ASCIIWHReceiver',
        '/newseg/(.*)', 'NewSEGReceiver',
        '/sites/(.*)', 'NewSEGReceiver',
    )
    app = web.application(urls, globals())
    app.run(log.Log)
