from .client import HTTPClient

class Auth:
    def __init__(self, api_key):
        self.api_key = api_key
        self.client = HTTPClient()

    def get_token(self):
        resp = self.client.post("auth/tokens", {"api_key": self.api_key})
        return resp.get("token")