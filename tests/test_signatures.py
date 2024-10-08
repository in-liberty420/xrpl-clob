import json
from xrpl.wallet import Wallet
from xrpl.core import keypairs
from xrpl.models import Payment
from xrpl.transaction import sign
from xrpl_integration import XRPLIntegration

def test_order_signature():
    # Create a test wallet
    wallet = Wallet.create()

    # Create sample order data
    order_data = {
        "price": 100.0,
        "amount": 10.0,
        "order_type": "buy",
        "expiration": 1234567890,
        "sequence": 1,
        "multisig_destination": "rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"
    }

    # Sign the order
    message = json.dumps(order_data)
    signature = keypairs.sign(message.encode(), wallet.private_key)

    # Verify the signature
    is_valid = keypairs.is_valid_message(message.encode(), signature, wallet.public_key)

    print(f"Order Signature Valid: {is_valid}")
    assert is_valid, "Order signature verification failed"

def test_payment_signature():
    # Create a test wallet and XRPLIntegration instance
    wallet = Wallet.create()
    xrpl_integration = XRPLIntegration()

    # Create a sample payment
    payment = Payment(
        account=wallet.classic_address,
        amount="1000000",  # 1 XRP in drops
        destination="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"
    )

    # Sign the payment
    signed_payment = sign(payment, wallet)
    payment_tx_signature = signed_payment.txn_signature
    
    # Ensure payment_tx_signature is a hex string
    if isinstance(payment_tx_signature, bytes):
        payment_tx_signature = payment_tx_signature.hex()
    elif isinstance(payment_tx_signature, str):
        # If it's already a string, ensure it's a valid hex string
        if not all(c in '0123456789ABCDEFabcdef' for c in payment_tx_signature):
            raise ValueError("Invalid hex string in txn_signature")

    # Verify the payment signature
    is_valid = xrpl_integration.verify_payment_signature(
        payment_tx_signature,
        wallet.classic_address,
        "rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
        1000000,
        payment.sequence
    )

    print(f"Payment Signature Valid: {is_valid}")
    assert is_valid, "Payment signature verification failed"

if __name__ == "__main__":
    print("Testing Order Signature:")
    test_order_signature()
    print("\nTesting Payment Signature:")
    test_payment_signature()
