from .client import HTTPClient

class WalletPayments:
    def __init__(self, auth_token: str):
        self.auth = auth_token
        self.client = HTTPClient()

    def pay(self, payment_key: str, identifier: str) -> dict:
        payload = {
            "auth_token": self.auth,
            "payment_key": payment_key,
            "identifier": identifier
        }
        return self.client.post("acceptance/payments/wallet", payload)