from xrpl.clients import JsonRpcClient
from xrpl.models.transactions import Payment
from xrpl.wallet import generate_faucet_wallet
from xrpl.transaction import safe_sign_and_submit_transaction

class XRPLIntegration:
    def __init__(self):
        self.client = JsonRpcClient("https://s.altnet.rippletest.net:51234")

    def create_wallet(self):
        return generate_faucet_wallet(self.client)

    def send_payment(self, sender_wallet, destination_address, amount):
        payment = Payment(
            account=sender_wallet.classic_address,
            amount=str(amount),
            destination=destination_address,
        )
        response = safe_sign_and_submit_transaction(payment, sender_wallet, self.client)
        return response
