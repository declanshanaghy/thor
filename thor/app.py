import chalice
import os
import datetime
import json
import logging

import chalicelib.constants as constants
import chalicelib.seg as seg

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
        if site == g['site']:
            return g
        else:
            raise chalice.BadRequestError("Requested site does not match data")
    except Exception as ex:
        app.log.error(str(ex), exc_info=True)
        raise chalice.ChaliceViewError(str(ex))

