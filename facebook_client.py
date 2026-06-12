import json
import math
from urllib.parse import urlencode

from tornado.httpclient import AsyncHTTPClient, HTTPClientError, HTTPRequest


class FacebookClientError(RuntimeError):
    pass


class FacebookClient:
    def __init__(self, client_id, client_secret, version="v24.0", http_client=None, timeout=10.0):
        if not client_id or not client_secret:
            raise RuntimeError("Facebook client configuration is required")
        if not version.startswith("v") or not version[1:].replace(".", "", 1).isdigit():
            raise RuntimeError("FACEBOOK_GRAPH_VERSION must look like v24.0")
        if not isinstance(timeout, (int, float)) or not math.isfinite(timeout) or timeout <= 0:
            raise RuntimeError("Facebook request timeout must be finite and positive")
        self.client_id = client_id
        self.client_secret = client_secret
        self.version = version
        self.http_client = http_client or AsyncHTTPClient()
        self.timeout = timeout

    def authorization_url(self, redirect_uri, state):
        query = urlencode({
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": "public_profile,user_friends",
            "state": state,
        })
        return "https://www.facebook.com/{}/dialog/oauth?{}".format(self.version, query)

    async def _json_request(self, request):
        try:
            response = await self.http_client.fetch(request, max_body_size=1024 * 1024)
            payload = json.loads(response.body.decode("utf-8"))
        except (HTTPClientError, UnicodeError, ValueError) as error:
            raise FacebookClientError("Facebook request failed") from error
        if not isinstance(payload, dict) or payload.get("error"):
            raise FacebookClientError("Facebook request failed")
        return payload

    async def authenticate(self, redirect_uri, code):
        body = urlencode({
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": redirect_uri,
            "code": code,
        })
        token = await self._json_request(HTTPRequest(
            "https://graph.facebook.com/{}/oauth/access_token".format(self.version),
            method="POST",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            body=body,
            request_timeout=self.timeout,
            connect_timeout=self.timeout,
            follow_redirects=False,
        ))
        access_token = token.get("access_token")
        if not isinstance(access_token, str) or not access_token:
            raise FacebookClientError("Facebook request failed")
        user = await self.request("/me", access_token, fields="id,name")
        if not isinstance(user.get("id"), str) or not isinstance(user.get("name"), str):
            raise FacebookClientError("Facebook request failed")
        user["access_token"] = access_token
        return user

    async def request(self, path, access_token, **parameters):
        if not isinstance(path, str) or not path.startswith("/") or "://" in path:
            raise FacebookClientError("Facebook request path is invalid")
        if not isinstance(access_token, str) or not access_token:
            raise FacebookClientError("Facebook request failed")
        query = urlencode(parameters)
        url = "https://graph.facebook.com/{}{}".format(self.version, path)
        if query:
            url += "?" + query
        return await self._json_request(HTTPRequest(
            url,
            method="GET",
            headers={"Authorization": "Bearer " + access_token},
            request_timeout=self.timeout,
            connect_timeout=self.timeout,
            follow_redirects=False,
        ))
