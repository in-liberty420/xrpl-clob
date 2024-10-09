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

# Configuration for orders
ORDER_CONFIG = [
    {"price": 100.0, "amount": 10.0, "order_type": "buy"},
    {"price": 101.0, "amount": 5.0, "order_type": "sell"},
    {"price": 99.0, "amount": 15.0, "order_type": "buy"},
    {"price": 102.0, "amount": 8.0, "order_type": "sell"},
]

def load_test_wallet():
    with open("test_wallet.json", "r") as f:
        wallet_info = json.load(f)
    return Wallet(wallet_info['public_key'], wallet_info['private_key'])

def get_multisig_address():
    with open("multisig_address.txt", "r") as f:
        return f.read().strip()
        
async def place_order(price, amount, order_type):
    url = "http://127.0.0.1:5000/place_order"
    
    wallet = load_test_wallet()
    logger.debug(f"Loaded wallet with address: {wallet.classic_address}")
    
    client = AsyncJsonRpcClient("https://s.altnet.rippletest.net:51234")
    account_info = await client.request(AccountInfo(account=wallet.classic_address))
    current_sequence = account_info.result['account_data']['Sequence']

    multisig_destination = get_multisig_address()
    logger.debug(f"Multisig destination address: {multisig_destination}")

    order_data = {
        "price": price,
        "amount": amount,
        "order_type": order_type,
        "expiration": int(time.time()) + 300,  # Unix time, 5 minutes from now
        "sequence": current_sequence + 1,
        "multisig_destination": multisig_destination
    }
    logger.debug(f"Order data: {order_data}")

    sequence = await get_next_valid_seq_number(wallet.classic_address, client)
    fee = await get_fee(client)

    amount_drops = xrpl.utils.xrp_to_drops(order_data['amount'])

    payment = Payment(
        account=wallet.classic_address,
        amount=amount_drops,
        destination=multisig_destination,
        sequence=sequence,
        fee=fee
    )
    
    signed_payment = await autofill_and_sign(payment, client, wallet)

    signed_tx_json = signed_payment.to_xrpl()
    signature = signed_tx_json["TxnSignature"]

    logger.debug(f"Signed transaction JSON: {json.dumps(signed_tx_json, indent=2)}")
    logger.debug(f"Payment transaction signature: {signature}")

    payload = {
        **order_data,
        "xrp_address": wallet.classic_address,
        "public_key": wallet.public_key,
        "payment_tx_signature": signature,
        "amount_drops": amount_drops,
        "signed_tx_json": signed_tx_json
    }
    logger.debug(f"Payload: {payload}")
    
    headers = {"Content-Type": "application/json"}

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers)
    
    logger.debug(f"Status Code: {response.status_code}")
    logger.debug(f"Response Headers: {response.headers}")
    logger.debug(f"Response Content: {response.text}")
    
    try:
        logger.debug(f"JSON Response: {response.json()}")
    except json.JSONDecodeError:
        logger.error("Failed to decode JSON response")

async def main():
    for order in ORDER_CONFIG:
        await place_order(order["price"], order["amount"], order["order_type"])
        await asyncio.sleep(1)  # Small delay between orders
    
    l2_order_book_url = "http://127.0.0.1:5000/l2_order_book"
    async with httpx.AsyncClient() as client:
        l2_order_book_response = await client.get(l2_order_book_url)
    print("\nL2 Order book:")
    print(l2_order_book_response.text)

if __name__ == "__main__":
    asyncio.run(main())
