import requests
import requests.auth


HEC_TOKEN = "B840C47D-FDF9-4C94-AD7F-EC92FD289204"
SPLUNK_URL = "http://35.166.45.189:8088/services/collector/event"


def send(event):
    headers = {"Authorization": "Splunk " + HEC_TOKEN}
    data = {
        "source": event['site'] + '-' + event['node'],
        "sourcetype": "json",
        "event": event
    }
    r = requests.post(SPLUNK_URL, json=data, headers=headers)
    if r.status_code == 200:
        return r.json()
    else:
        raise StandardError("%s: %s" % (r.status_code, r.text))

