import base64
import hashlib
import json
import os
from urlparse import urlparse, parse_qs
import time

import requests

DEFAULT_HOST = "auth.scp.splunk.com"
PATH_AUTHN = "/authn"
PATH_AUTHORIZE = "/authorize"
PATH_TOKEN = "/token"
PATH_CSRFTOKEN = "/csrfToken"

HEADERS_DEFAULT = {
    "Accept": "application/json",
    "Content-Type": "application/json"}
HEADERS_URLENCODED = {
    "Accept": "application/json",
    "Content-Type": "application/x-www-form-urlencoded"}

DEFAULT_SCOPE = "openid email profile"
DEFAULT_REFRESH_SCOPE = "openid offline_access email profile"


class AuthManager(object):
    """
    The AuthManager class is a base class that manages different authentication flows.
    When creating an authorization manager, create a subclass that corresponds to
    the flow that you need for your app.
    """

    def __init__(self, host, client_id, requests_hooks=None):
        self._host = host
        self._client_id = client_id
        self._requests_hooks = requests_hooks or []

    def _get(self, url, headers=None, params=None):
        response = requests.get(
            url,
            headers=headers or HEADERS_DEFAULT,
            params=params,
            allow_redirects=False
        )
        return response

    # Note: the requests module interprets the data param in an interesting
    # way, if its a dict, it will be url form encoded, if its a string it
    # will be posted in the body
    def _post(self, url, auth=None, headers=None, data=None, cookies=None):
        response = requests.post(
            url,
            auth=auth,
            headers=headers or HEADERS_DEFAULT,
            data=data,
            cookies=cookies
        )
        return response

    def _url(self, path):
        return "https://%s%s" % (self._host, path)

    @staticmethod
    def _parse_querystring(url):
        """Returns dict containing parsed query string params."""
        if url is None:
            return None
        url = urlparse(url)
        params = parse_qs(url.query)
        params = dict(params)
        return params

    def _post_token(self, auth=None, **data):
        """POST ${basePath}/token, expect 200"""
        path = PATH_TOKEN
        response = self._post(
            self._url(path),
            auth=auth,
            headers=HEADERS_URLENCODED,
            data=data)
        if response.status_code != 200:
            raise StandardError("Unable to post for token", response)
        return response


class PKCEAuthManager(AuthManager):
    """
    This subclass of AuthManager handles the PKCE auth flow.  PKCE should be used when an app is acting on behalf
    of a human user. Both the user and the app are authenticating themselves to the system- the user through username
    and password, the app through the client_id and redirect_uri. For more details, see identity service documentation.
    """

    def __init__(self, host, client_id, redirect_uri, username, password, scope=DEFAULT_REFRESH_SCOPE, requests_hooks=None):
        super(PKCEAuthManager, self).__init__(host, client_id, requests_hooks=requests_hooks)
        self._redirect_uri = redirect_uri
        self._username = username
        self._password = password
        self._state = None
        self._scope = scope

    # Note: see https://tools.ietf.org/html/rfc7636#section-4.1
    # code_verifier = a high-entropy cryptographic random STRING using the
    # unreserved characters [A-Z] / [a-z] / [0-9] / "-" / "." / "_" / "~"
    # from Section 2.3 of [RFC3986], with a minimum length of 43 characters
    # and a maximum length of 128 characters.
    _SAFE = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-._~"

    @staticmethod
    def _create_code_verifier(n):
        """Returns a code verifier of length 'n', where 43 <= n <= 128."""
        assert 43 <= n <= 128, "Code verifier length must be between the values of 43 and 128 inclusive"
        result = bytearray(os.urandom(n))
        result = base64.urlsafe_b64encode(result)
        result = result.rstrip('='.encode('utf-8'))  # strip b64 padding
        return result

    # Note: see https://tools.ietf.org/html/rfc7636#section-4.2
    # code_challenge = BASE64URL-ENCODE(SHA256(ASCII(code_verifier)))
    @staticmethod
    def _create_code_challenge(cv):
        """Returns a code challenge based on the given code verifier."""
        result = hashlib.sha256(cv).digest()
        result = base64.urlsafe_b64encode(result)
        result = result.rstrip('='.encode('utf-8'))  # strip b64 padding
        return result

    def _get_session_token(self, username, password):
        """Returns a one-time session token by authenticating using the
         (extended) "primary" endpoint (/authn)."""
        csrfToken, cookies = self._get_csrf_token()
        if csrfToken is None:
            return None
        result = self._authenticate_user(username, password, csrfToken, cookies)
        if result is None:
            return None
        return result.get("sessionToken", None)

    def _get_csrf_token(self):
        """Returns a CSRF token to be passed into /authn"""
        response = self._get(self._url(PATH_CSRFTOKEN))
        if response.status_code != 200:
            raise StandardError("Authentication failed.", response)
        result = response.json()
        csrfToken = result.get("csrf", None)
        if csrfToken is None:
            raise StandardError("no CSRF token from /csrfToken", response)
        return csrfToken, response.cookies

    def _authenticate_user(self, username, password, csrfToken, cookies):
        """Authenticate using the (extended) "primary" method."""
        data = {"username": username, "password": password, "csrfToken": csrfToken}
        response = self._post(self._url(PATH_AUTHN), data=json.dumps(data), cookies=cookies)
        if response.status_code != 200:
            raise StandardError("Authentication failed.", response)
        result = response.json()
        status = result.get("status", None)
        if status is None:
            raise StandardError("no response status from /authn", response)
        if status != "SUCCESS":  # eg: LOCKED_OUT
            raise StandardError("authentication failed: %s" % status, response)
        return result

    def _get_authorization_code(self, **params):
        """GET ${basePath}/authorize, expect 302 (redirect)"""
        path = PATH_AUTHORIZE
        response = self._get(self._url(path), params=params)
        if response.status_code != 302:
            raise StandardError("Unable to obtain authorization code. Check client_id, redirect_uri, and scope", response)
        location = response.headers.get("location", None)
        if location is None:
            raise StandardError("Unable to obtain authorization code. Check client_id, redirect_uri, and scope", response)
        params = self._parse_querystring(location)
        value = params.get("code", None)
        if value is None:
            raise StandardError("Unable to obtain authorization code. Check client_id, redirect_uri, and scope", response)

        assert value and len(value) == 1
        return value[0]

    def validate(self):
        if self._client_id is None:
            raise ValueError("missing client_id")
        if self._redirect_uri is None:
            raise ValueError("missing redirect_uri")

    def authenticate(self):
        """Authenticate with the (extended) "authorization code with pkce"
         flow."""

        self.validate()

        # retrieve one time session token
        session_token = self._get_session_token(self._username, self._password)

        cv = self._create_code_verifier(50)
        cc = self._create_code_challenge(cv)

        # request authorization code
        auth_code = self._get_authorization_code(
            client_id=self._client_id,
            code_challenge=cc.decode("utf-8"),
            code_challenge_method="S256",
            nonce="none",
            redirect_uri=self._redirect_uri,
            response_type="code",
            scope=self._scope,
            session_token=session_token,
            state=self._state or str(time.time())
        )

        # exchange authorization code for token(s)
        response = self._post_token(
            client_id=self._client_id,
            code=auth_code,
            code_verifier=cv,
            grant_type="authorization_code",
            redirect_uri=self._redirect_uri
        )
        if response.status_code != 200:
            raise StandardError("Unable to exchange authorization code for a token", response)
        return response.json()

class ClientAuthManager(AuthManager):
    """
    Implements the Client Credentials auth flow. Client Credentials is used when an application is authorized to
    make calls on it's own behalf- in other words, there is not a human user associated with the request. For
    more details look to documentation for the identity service.
    """

    # TODO: Host can be an optional value since it has a default
    def __init__(self, host, client_id, client_secret, scope="", requests_hooks=None):
        super(ClientAuthManager, self).__init__(host, client_id, requests_hooks=requests_hooks)
        self._client_secret = client_secret
        self._scope = scope

    def authenticate(self):
        """Authenticate using the "client credentials" flow."""
        if self._client_id is None:
            raise ValueError("missing client_id")
        if self._client_secret is None:
            raise ValueError("missing client_secret")
        if self._scope is None:
            raise ValueError("missing scope")

        data = {"grant_type": "client_credentials", "scope": self._scope}
        auth = (self._client_id, self._client_secret)
        response = self._post_token(auth, **data)
        if response.status_code != 200:
            raise StandardError("Unable to authenticate. Check credentials.", response)
        return response.json()
