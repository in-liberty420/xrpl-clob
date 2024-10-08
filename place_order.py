import httpx
import json
import time
import asyncio
from xrpl.wallet import Wallet
from xrpl.asyncio.clients import AsyncJsonRpcClient
from xrpl.core import keypairs
from xrpl.models import AccountInfo, Payment
from xrpl.asyncio.transaction import autofill_and_sign
from xrpl.asyncio.account import get_next_valid_seq_number
from xrpl.asyncio.ledger import get_fee
import xrpl.utils
from xrpl.core.binarycodec import encode_for_signing
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

async def place_order():
    url = "http://127.0.0.1:5000/place_order"
    
    # Load the test wallet
    wallet = load_test_wallet()
    logger.debug(f"Loaded wallet with address: {wallet.classic_address}")
    
    # Get the current sequence number
    client = AsyncJsonRpcClient("https://s.altnet.rippletest.net:51234")
    account_info = await client.request(AccountInfo(account=wallet.classic_address))
    current_sequence = account_info.result['account_data']['Sequence']

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
    
    # TODO: Implement order data signing later for additional security
    # For now, we'll only sign the payment transaction

    # Get the next valid sequence number and current fee
    sequence = await get_next_valid_seq_number(wallet.classic_address, client)
    fee = await get_fee(client)

    # Convert the amount to drops
    amount_drops = xrpl.utils.xrp_to_drops(order_data['amount'])

    # Create and sign the payment transaction
    payment = Payment(
        account=wallet.classic_address,
        amount=amount_drops,
        destination=multisig_destination,
        sequence=sequence,
        fee=fee
    )
    
    # Sign the transaction
    signed_payment = await autofill_and_sign(payment, client, wallet)
    payment_tx_signature = signed_payment.get_hash()

    logger.debug(f"Payment transaction signature: {payment_tx_signature}")

    # Prepare payload
    payload = {
        **order_data,
        "xrp_address": wallet.classic_address,
        "public_key": wallet.public_key,
        "payment_tx_signature": payment_tx_signature,
        "amount_drops": amount_drops
    }
    # TODO: Add order data signature to payload when implemented
    logger.debug(f"Payload: {payload}")
    
    headers = {"Content-Type": "application/json"}

    # Send request using httpx
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers)
    
    logger.debug(f"Status Code: {response.status_code}")
    logger.debug(f"Response Headers: {response.headers}")
    logger.debug(f"Response Content: {response.text}")
    
    try:
        logger.debug(f"JSON Response: {response.json()}")
    except json.JSONDecodeError:
        logger.error("Failed to decode JSON response")

    # Check the L2 order book
    l2_order_book_url = "http://127.0.0.1:5000/l2_order_book"
    async with httpx.AsyncClient() as client:
        l2_order_book_response = await client.get(l2_order_book_url)
    logger.debug("\nL2 Order book:")
    logger.debug(f"Status Code: {l2_order_book_response.status_code}")
    logger.debug(f"Response Content: {l2_order_book_response.text}")

if __name__ == "__main__":
    asyncio.run(place_order())
