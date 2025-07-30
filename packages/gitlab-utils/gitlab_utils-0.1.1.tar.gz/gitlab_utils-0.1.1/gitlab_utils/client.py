# gitlab_wrapper/client.py

import requests

from .apis.users import UsersAPI


class GitLabClient:
    def __init__(self, base_url: str, private_token: str):
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "Private-Token": private_token,
            "Content-Type": "application/json",
        }

        # Attach user-related API methods
        self.users = UsersAPI(self)

    def _request(self, method: str, endpoint: str, **kwargs):
        url = f"{self.base_url}/api/v4/{endpoint.lstrip('/')}"
        response = requests.request(method, url, headers=self.headers, **kwargs)
        if not response.ok:
            response.raise_for_status()
        return response.json()

    def get(self, endpoint, **kwargs):
        return self._request("GET", endpoint, **kwargs)

    def post(self, endpoint, **kwargs):
        return self._request("POST", endpoint, **kwargs)

    def put(self, endpoint, **kwargs):
        return self._request("PUT", endpoint, **kwargs)

    def delete(self, endpoint, **kwargs):
        return self._request("DELETE", endpoint, **kwargs)
