from .client import HTTPClient

class Refunds:
    def __init__(self, auth_token: str):
        self.auth = auth_token
        self.client = HTTPClient()

    def void(self, transaction_id: int) -> dict:
        return self.client.post("acceptance/void_refund/void", {"transaction_id": transaction_id})

    def refund(self, transaction_id: int, amount_cents: int) -> dict:
        payload = {
            "auth_token": self.auth,
            "transaction_id": transaction_id,
            "amount_cents": amount_cents
        }
        return self.client.post("acceptance/void_refund/refund", payload)