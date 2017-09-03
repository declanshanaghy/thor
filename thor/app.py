import chalice
import os
import datetime
import json
import logging

import gem

app = chalice.Chalice(app_name='thor')
app.log.setLevel(logging.DEBUG)

REQ_DIR = 'requests'
LOG_REQUESTS = os.environ.get('LOG_REQUESTS', False)
if LOG_REQUESTS == 'true':
    if not os.path.exists(REQ_DIR):
        os.makedirs(REQ_DIR)

@app.route('/sites/{site}', methods=['PUT'], content_types=[])
def sites(site):
    try:
        data = app.current_request.raw_body
        app.log.info("Received data: %s", data)

        if LOG_REQUESTS:
            n = "%s.req" % datetime.datetime.now()
            p = os.path.join(REQ_DIR, n)
            with open(p, "w") as f:
                f.write(data)

        g = gem.parse(data)
        app.log.info("Parsed data: %s", json.dumps(g))
        if site == g['site']:
            return g
        else:
            raise chalice.BadRequestError("Requested site does not match data")
    except Exception as ex:
        app.log.error(str(ex))
        raise chalice.ChaliceViewError(str(ex))

