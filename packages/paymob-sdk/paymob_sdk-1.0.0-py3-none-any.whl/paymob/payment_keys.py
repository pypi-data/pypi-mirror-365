from .client import HTTPClient

class PaymentKeys:
    def __init__(self, auth_token: str, integration_id: int):
        self.auth = auth_token
        self.integration_id = integration_id
        self.client = HTTPClient()

    def generate(self, order_id: int, amount_cents: int, billing_data: dict, currency: str = "EGP", expiration: int=3600, lock_order_when_paid: bool=False) -> str:
        """Generate payment keys for a specific order."""
        payload = {
            "auth_token": self.auth,
            "integration_id": self.integration_id,
            "order_id": order_id,
            "amount_cents": amount_cents,
            "currency": currency,
            "expiration": expiration,
            "billing_data": billing_data,
            "lock_order_when_paid": lock_order_when_paid
        }

        res=self.client.post("acceptance/payment_keys", payload)

        return res.get("token")

        