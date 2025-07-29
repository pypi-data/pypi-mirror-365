from .client import HTTPClient

class Transactions:
    def __init__(self, auth_token: str):
        self.auth = auth_token
        self.client = HTTPClient()

    def inquiry(self, order_id: int=None, trasnaction_id: int=None, merchant_order_id: str=None) -> dict:
        payload = {"auth_token": self.auth}
        if order_id is not None:
            payload["order_id"] = order_id
        elif trasnaction_id is not None:
            payload["transaction_id"] = trasnaction_id
        elif merchant_order_id is not None:
            payload["merchant_order_id"] = merchant_order_id
        else:
            raise ValueError("At least one of order_id, transaction_id, or merchant_order_id must be provided.")

        return self.client.post("acceptance/transactions", payload)