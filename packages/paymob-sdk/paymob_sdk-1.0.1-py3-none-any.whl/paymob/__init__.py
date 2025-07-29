# In paymob_sdk/paymob/_init_.py

from .auth import Auth
from .orders import Orders
from .payment_keys import PaymentKeys
from .transactions import Transactions
from .wallet import WalletPayments
from .kiosk import KioskPayments
from .refund import Refunds

class PayMobClient:
    def __init__(self, api_key: str, integration_id: int):
        self.auth = Auth(api_key)
        self.transaction = Transactions(self.auth.get_token())
        self.order = Orders(self.transaction.auth)  # pass token
        self.payment_key = PaymentKeys(self.transaction.auth, integration_id)
        self.wallet = WalletPayments(self.transaction.auth)
        self.kiosk = KioskPayments(self.transaction.auth)
        self.refund = Refunds(self.transaction.auth)