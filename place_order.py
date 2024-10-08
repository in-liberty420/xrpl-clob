import httpx
import json
import time
from xrpl.wallet import Wallet
from xrpl.clients import JsonRpcClient
from xrpl.core import keypairs
from xrpl.models import AccountInfo, Payment
from xrpl.transaction import sign
from xrpl.account import get_next_valid_seq_number
from xrpl.ledger import get_fee
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def load_test_wallet():
    with open("test_wallet.json", "r") as f:
        wallet_info = json.load(f)
    return Wallet(wallet_info['public_key'], wallet_info['private_key'])

def get_multisig_address():
    with open("multisig_address.txt", "r") as f:
        return f.read().strip()

def place_order():
    url = "http://127.0.0.1:5000/place_order"
    
    # Load the test wallet
    wallet = load_test_wallet()
    logger.debug(f"Loaded wallet with address: {wallet.classic_address}")
    
    # Get the current sequence number
    client = JsonRpcClient("https://s.altnet.rippletest.net:51234")
    current_sequence = client.request(AccountInfo(account=wallet.classic_address)).result['account_data']['Sequence']

    # Get the multisig wallet address
    multisig_destination = get_multisig_address()
    logger.debug(f"Multisig destination address: {multisig_destination}")

    # Create order data
    order_data = {
        "price": 100.0,
        "amount": 10.0,
        "order_type": "buy",
        "expiration": int(time.time()) + 300,  # Unix time, 5 minutes from now
        "sequence": current_sequence + 1,  # Use the next sequence number
        "multisig_destination": multisig_destination
    }
    logger.debug(f"Order data: {order_data}")
    
    # Sign the order
    message = json.dumps(order_data)
    signature = keypairs.sign(message.encode(), wallet.private_key)
    logger.debug(f"Message to sign: {message}")
    logger.debug(f"Signature: {signature}")
    logger.debug(f"Public key: {wallet.public_key}")

    # Get the next valid sequence number and current fee
    sequence = get_next_valid_seq_number(wallet.classic_address, client)
    fee = get_fee(client)

    # Create and sign the payment transaction
    payment = Payment(
        account=wallet.classic_address,
        amount=str(order_data['amount']),
        destination=multisig_destination,
        sequence=sequence,
        fee=fee
    )
    
    # Sign the transaction
    signed_payment = sign(payment, wallet)
    payment_tx_signature = signed_payment.get_hash()
    logger.debug(f"Payment transaction signature: {payment_tx_signature}")

    # Prepare payload
    payload = {
        **order_data,
        "xrp_address": wallet.classic_address,
        "public_key": wallet.public_key,
        "signature": signature,
        "payment_tx_signature": payment_tx_signature
    }
    logger.debug(f"Payload: {payload}")
    
    headers = {"Content-Type": "application/json"}

    # Send request using httpx
    with httpx.Client() as client:
        response = client.post(url, json=payload, headers=headers)
    
    logger.debug(f"Status Code: {response.status_code}")
    logger.debug(f"Response Headers: {response.headers}")
    logger.debug(f"Response Content: {response.text}")
    
    try:
        logger.debug(f"JSON Response: {response.json()}")
    except json.JSONDecodeError:
        logger.error("Failed to decode JSON response")

    # Check the L2 order book
    l2_order_book_url = "http://127.0.0.1:5000/l2_order_book"
    with httpx.Client() as client:
        l2_order_book_response = client.get(l2_order_book_url)
    logger.debug("\nL2 Order book:")
    logger.debug(f"Status Code: {l2_order_book_response.status_code}")
    logger.debug(f"Response Content: {l2_order_book_response.text}")

if __name__ == "__main__":
    place_order()
