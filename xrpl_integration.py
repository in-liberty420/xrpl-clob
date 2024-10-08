from xrpl.clients import JsonRpcClient
from xrpl.models.transactions import Payment
from xrpl.models import AccountInfo
from xrpl.wallet import generate_faucet_wallet
from xrpl.transaction import submit_and_wait, safe_sign_and_autofill_transaction
from xrpl.core import keypairs

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
        signed_tx = sender_wallet.sign(payment)
        response = submit_and_wait(signed_tx, self.client)
        return response

    def get_account_sequence(self, address):
        request = AccountInfo(account=address)
        response = self.client.request(request)
        return response.result['account_data']['Sequence']

    def verify_payment_signature(self, payment_tx_signature, xrp_address, multisig_destination, amount):
        if payment_tx_signature is None:
            return False
        
        # Recreate the payment transaction
        payment = Payment(
            account=xrp_address,
            amount=str(amount),
            destination=multisig_destination
        )
        
        # Get the account info to fill in the sequence and fee
        account_info = self.client.request(AccountInfo(account=xrp_address))
        sequence = account_info.result['account_data']['Sequence']
        
        # Autofill the transaction
        filled_tx = safe_sign_and_autofill_transaction(payment, self.client, xrp_address)
        
        # Verify the signature
        return keypairs.is_valid_message(filled_tx.to_xrpl(), bytes.fromhex(payment_tx_signature), xrp_address)

    def create_payment_transaction(self, source, destination, amount):
        return Payment(
            account=source,
            destination=destination,
            amount=str(amount)
        )

    def submit_transaction(self, signed_transaction):
        if hasattr(signed_transaction, 'last_ledger_sequence') and signed_transaction.last_ledger_sequence is not None:
            current_ledger = self.get_current_ledger_sequence()
            if signed_transaction.last_ledger_sequence <= current_ledger:
                raise ValueError("Transaction has expired (LastLedgerSequence has passed)")
        return submit_and_wait(signed_transaction, self.client)

    def get_current_ledger_sequence(self):
        return self.client.request('ledger_current')['ledger_current_index']

