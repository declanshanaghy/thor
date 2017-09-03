import chalice
import os
import datetime
import json
import logging

from chalicelib import constants
from chalicelib import seg

app = chalice.Chalice(app_name='thor')
app.log.setLevel(logging.DEBUG)

@app.route('/sites/{site}', methods=['PUT'], content_types=[])
def sites(site):
    try:
        data = app.current_request.raw_body
        app.log.info("Received data: %s", data)

        if constants.LOG_REQUESTS:
            n = "%s.req" % datetime.datetime.now()
            p = os.path.join(constants.REQ_DIR, n)
            with open(p, "w") as f:
                f.write(data)

        g = seg.parse(data)

        d = json.dumps(g, indent=4, sort_keys=True)
        app.log.info("Parsed data: %s", d)

        return g
    except Exception as ex:
        app.log.error(str(ex), exc_info=True)
        raise chalice.ChaliceViewError(str(ex))

@app.lambda_function(name='splunk-delivery')
def splunk_delivery(event, context):
    app.log.info('action=handler, status=start, event=%s', event)
    app.log.debug('action=debug_context, context="%s"', dir(context))
    return {"delivered": "splunk"}
