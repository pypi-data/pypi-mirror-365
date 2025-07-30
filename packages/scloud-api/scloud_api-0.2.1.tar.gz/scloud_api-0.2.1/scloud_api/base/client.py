from requests import request
import json
from scloud_api.auth import auth_token_client, AuthTokenClient
from .ApiResponse import ApiResponse


class Client:
    def __init__(self, cred=None):
        auth = AuthTokenClient(cred)
        self._auth = auth.get_auth()

    def _request(self, path: str, method: str, data: dict = None) -> ApiResponse:
        endpoint = f"{self._auth.url}{path}"
        res = request(
            method=method,
            url=endpoint,
            headers=self.headers,
            data=(
                json.dumps(data)
                if data and method in ("POST", "PUT", "PATCH")
                else None
            ),
            params=(
                data
                if data and method in ("GET")
                else None
            ))
        return ApiResponse(res.json())

    @property
    def headers(self):
        return {
            "Accept": "application/json",
            "Authorization": f"Bearer {self._auth.access_token}",
        }