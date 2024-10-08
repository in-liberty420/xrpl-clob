from xrpl.clients import JsonRpcClient
from xrpl.models.transactions import Payment
from xrpl.models import AccountInfo
from xrpl.wallet import generate_faucet_wallet
from xrpl.transaction import submit_and_wait
from xrpl.core import keypairs
from xrpl.account import get_next_valid_seq_number
from xrpl.ledger import get_fee
from xrpl.core.binarycodec import encode_for_signing

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

    def verify_payment_signature(self, payment_tx_signature, xrp_address, multisig_destination, amount_drops, sequence):
        if payment_tx_signature is None:
            return False
        
        # Prepare the transaction data for signing
        tx_json = {
            "Account": xrp_address,
            "Amount": amount_drops,
            "Destination": multisig_destination,
            "TransactionType": "Payment",
            "Sequence": sequence
        }
        
        # Encode the transaction data
        encoded_tx = encode_for_signing(tx_json)
        
        try:
            # Ensure the signature is in the correct format
            signature_bytes = bytes.fromhex(payment_tx_signature)
            
            # Verify the signature
            return keypairs.is_valid_message(encoded_tx, signature_bytes, xrp_address)
        except ValueError as e:
            logger.error(f"Invalid payment signature format: {e}")
            return False

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

