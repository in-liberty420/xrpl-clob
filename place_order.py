import requests
import json
import time
from xrpl.wallet import generate_faucet_wallet
from xrpl.clients import JsonRpcClient
from order_signing import sign_order

def place_order():
    url = "http://127.0.0.1:5000/place_order"
    
    # Generate a test wallet (in a real app, you'd use a persistent wallet)
    client = JsonRpcClient("https://s.altnet.rippletest.net:51234")
    wallet = generate_faucet_wallet(client)
    
    # Current time plus 3 seconds
    expiration = time.time() + 3
    
    order_data = {
        "price": 100.0,
        "amount": 10.0,
        "order_type": "buy",
        "expiration": expiration
    }
    
    signature = sign_order(order_data, wallet)
    
    payload = {
        **order_data,
        "xrp_address": wallet.classic_address,
        "signature": signature
    }
    
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, data=json.dumps(payload), headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {response.headers}")
    print(f"Response Content: {response.text}")
    
    try:
        print(f"JSON Response: {response.json()}")
    except json.JSONDecodeError:
        print("Failed to decode JSON response")

    # Wait for 4 seconds to see the order expire
    time.sleep(4)

    # Check the order book after expiration
    order_book_url = "http://127.0.0.1:5000/order_book"
    order_book_response = requests.get(order_book_url)
    print("Order book after expiration:")
    print(f"Status Code: {order_book_response.status_code}")
    print(f"Response Headers: {order_book_response.headers}")
    print(f"Response Content: {order_book_response.text}")
    
    try:
        print(json.dumps(order_book_response.json(), indent=2))
    except json.JSONDecodeError:
        print("Failed to decode JSON response for order book")

if __name__ == "__main__":
    place_order()
