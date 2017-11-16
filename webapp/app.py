import json
import web

import seg
import gem
import log


class NewSEGReceiver(gem.GEMProcessor):
    def PUT(self, site):
        logger = web.ctx.env.get('wsgilog.logger')
        logger.info("Processing NewSEG. site=%s", site)

        try:
            data = web.data()
            parser = seg.NEWSEGParser(data)
            ret = self.process(parser, logger=logger)
            return json.dumps(ret, indent=4, sort_keys=True)
        except Exception as ex:
            logger.error(str(ex), exc_info=True)
            raise web.BadRequest(str(ex))


if __name__ == "__main__":
    urls = (
        '/newseg/(.*)', 'NewSEGReceiver',
        '/sites/(.*)', 'NewSEGReceiver',
    )
    app = web.application(urls, globals())
    app.run(log.Log)
