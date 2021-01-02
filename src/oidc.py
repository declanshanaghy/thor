import base64

import json
import requests


class OIDCClient(object):
    def __init__(self, host, auth_server='default'):
        self.host = host
        self.auth_servier = auth_server

    # // Authenticate using the "client credentials" flow.
    # func (self *Client) ClientFlow(clientId, clientSecret, scope string) (*Context, error) {
    # 	form := url.Values{
    # 		"grant_type": {"client_credentials"},
    # 		"scope":      {scope}}
    # 	request, err := newFormPost(self.url(PathToken), form)
    # 	if err != nil {
    # 		return nil, err
    # 	}
    # 	request.SetBasicAuth(clientId, clientSecret)
    # 	response, err := newHttpClient().Do(request)
    # 	if err != nil {
    # 		return nil, err
    # 	}
    # 	defer response.Body.Close()
    # 	if response.StatusCode != http.StatusOK {
    # 		return nil, httpError(response)
    # 	}
    # 	return decode(response)
    # }

    def client_credentials(self, client_id, secret, scope=None):
        form = {
            "grant_type": "client_credentials",
        }
        if scope:
            form["scope"] = scope

        a = base64.b64encode(client_id + ":" + secret)
        headers = {"Authorization": "Basic " + a}
        r = requests.post(self.host + "/oauth2/" + self.auth_servier + "/v1/token",
                          data=form, headers=headers)
        if r.status_code != 200:
            raise StandardError("Error %s: %s" % (r.status_code, r.text))
        r2 = json.loads(r.text)
        return r2['access_token']
