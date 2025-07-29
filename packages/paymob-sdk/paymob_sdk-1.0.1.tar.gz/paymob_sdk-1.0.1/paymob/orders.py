from .client import HTTPClient

class Orders:
    def __init__(self, auth_token: str):
        self.auth = auth_token
        self.client = HTTPClient()

    def create_order(self, amount_cents: int, currency: str="EGP", items: list=None, delivery_neededL bool=False, merchant_order_id: str) -> dict:
        """Create a new order with the specified parameters.
        """
        payload = {
            "auth_token": self.auth,
            "merchant_order_id": merchant_order_id,
            "amount_cents": amount_cents,
            "currency": currency,
            "delivery_needed": delivery_needed,
            "items": items or []
        }

        return self.client.post("ecommerce/orders", payload)