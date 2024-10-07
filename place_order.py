import requests
import json
import time

def place_order():
    url = "http://127.0.0.1:5000/place_order"
    
    # Current time plus 3 seconds
    expiration = time.time() + 3
    
    payload = {
        "price": 100.0,
        "amount": 10.0,
        "order_type": "buy",
        "user_id": "user123",
        "expiration": expiration
    }
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, data=json.dumps(payload), headers=headers)
    print(response.json())

    # Wait for 4 seconds to see the order expire
    time.sleep(4)

    # Check the order book after expiration
    order_book_url = "http://127.0.0.1:5000/order_book"
    order_book_response = requests.get(order_book_url)
    print("Order book after expiration:")
    print(json.dumps(order_book_response.json(), indent=2))

if __name__ == "__main__":
    place_order()
