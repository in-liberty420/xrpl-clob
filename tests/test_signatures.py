import json
from xrpl.wallet import Wallet
from xrpl.core import keypairs
from xrpl.models import Payment
from xrpl.transaction import sign
from xrpl_integration import XRPLIntegration

def load_test_wallet():
    with open("test_wallet.json", "r") as f:
        wallet_info = json.load(f)
    return Wallet(wallet_info['public_key'], wallet_info['private_key'])

def test_order_signature():
    # Load the test wallet
    wallet = load_test_wallet()

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
    signature = bytes.fromhex(keypairs.sign(message.encode(), wallet.private_key))

    # Verify the signature
    is_valid = keypairs.is_valid_message(message.encode(), signature, wallet.public_key)

    print(f"Order Signature Valid: {is_valid}")
    assert is_valid, "Order signature verification failed"

def test_payment_signature():
    # Load the test wallet and create XRPLIntegration instance
    wallet = load_test_wallet()
    xrpl_integration = XRPLIntegration()

    # Create a sample payment
    payment = Payment(
        account=wallet.classic_address,
        amount="1000000",  # 1 XRP in drops
        destination="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
        sequence=1
    )

    # Sign the payment
    signed_payment = sign(payment, wallet)

    # Log the type of txn_signature
    print(f"Type of signed_payment.txn_signature: {type(signed_payment.txn_signature)}")
    print(f"Value of signed_payment.txn_signature: {signed_payment.txn_signature}")

    # Create the transaction JSON expected by verify_payment_signature
    tx_json = {
        "Account": wallet.classic_address,
        "Amount": "1000000",
        "Destination": "rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
        "TransactionType": "Payment",
        "Sequence": 1,
        "SigningPubKey": wallet.public_key,
        "TxnSignature": signed_payment.txn_signature  # Remove .hex()
    }

    print(f"Length of signed_payment.txn_signature: {len(signed_payment.txn_signature)}")
    print(f"Full value of signed_payment.txn_signature: {signed_payment.txn_signature}")

    print(f"Length of tx_json['TxnSignature']: {len(tx_json['TxnSignature'])}")
    print(f"Full value of tx_json['TxnSignature']: {tx_json['TxnSignature']}")

    print(f"Wallet address: {wallet.classic_address}")
    print(f"Wallet public key: {wallet.public_key}")
    print(f"Payment signature: {tx_json['TxnSignature']}")
    print(f"Payment sequence: {tx_json['Sequence']}")

    # Verify the payment signature
    is_valid = xrpl_integration.verify_payment_signature(
        tx_json["TxnSignature"],
        tx_json["SigningPubKey"],
        tx_json["Destination"],
        int(tx_json["Amount"]),
        tx_json["Sequence"]
    )

    print(f"Payment Signature Valid: {is_valid}")
    assert is_valid, "Payment signature verification failed"

if __name__ == "__main__":
    print("Testing Order Signature:")
    test_order_signature()
    print("\nTesting Payment Signature:")
    test_payment_signature()
