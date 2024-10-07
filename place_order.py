import requests
import json
import time
from xrpl.wallet import generate_faucet_wallet
from xrpl.clients import JsonRpcClient
from xrpl.core import keypairs
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def place_order():
    url = "http://127.0.0.1:5000/place_order"
    
    # Generate a test wallet
    client = JsonRpcClient("https://s.altnet.rippletest.net:51234")
    wallet = generate_faucet_wallet(client)
    logger.debug(f"Generated wallet with address: {wallet.classic_address}")
    
    # Create order data
    order_data = {
        "price": 100.0,
        "amount": 10.0,
        "order_type": "buy",
        "expiration": int(time.time() + 300)  # 5 minutes from now
    }
    logger.debug(f"Order data: {order_data}")
    
    # Sign the order
    message = json.dumps(order_data)
    signature = keypairs.sign(message.encode(), wallet.private_key)
    logger.debug(f"Message to sign: {message}")
    logger.debug(f"Signature: {signature.hex()}")  # Convert to hex string

    # Prepare payload
    payload = {
        **order_data,
        "xrp_address": wallet.classic_address,
        "signature": signature.hex()  # Send as hex string
    }
    logger.debug(f"Payload: {payload}")
    
    headers = {"Content-Type": "application/json"}

    # Send request
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    
    logger.debug(f"Status Code: {response.status_code}")
    logger.debug(f"Response Headers: {response.headers}")
    logger.debug(f"Response Content: {response.text}")
    
    try:
        logger.debug(f"JSON Response: {response.json()}")
    except json.JSONDecodeError:
        logger.error("Failed to decode JSON response")

    # Check the order book
    order_book_url = "http://127.0.0.1:5000/order_book"
    order_book_response = requests.get(order_book_url)
    logger.debug("\nOrder book:")
    logger.debug(f"Status Code: {order_book_response.status_code}")
    logger.debug(f"Response Content: {order_book_response.text}")

if __name__ == "__main__":
    place_order()
