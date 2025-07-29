from .client import HTTPClient

class KioskPayments:
    def __init__(self, auth_token: str):
        self.auth = auth_token
        self.client = HTTPClient()

    def pay(self, payment_key: str) -> dict:
        payload = {
            "auth_token": self.auth,
            "payment_key": payment_key
        }
        return self.client.post("acceptance/payments/cash", payload)