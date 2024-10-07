import time

class Order:
    def __init__(self, price, amount, order_type, xrp_address, public_key, signature, expiration=None):
        self.price = price
        self.amount = amount
        self.order_type = order_type
        self.xrp_address = xrp_address
        self.public_key = public_key
        self.signature = signature
        self.expiration = expiration or (time.time() + 300)  # Default 5 minutes expiration

class OrderBook:
    def __init__(self):
        self.bids = []
        self.asks = []

    def add_order(self, order):
        if order.order_type == "buy":
            self.bids.append(order)
            self.bids.sort(key=lambda x: x.price, reverse=True)
        elif order.order_type == "sell":
            self.asks.append(order)
            self.asks.sort(key=lambda x: x.price)

    def remove_order(self, order):
        if order.order_type == "buy":
            self.bids.remove(order)
        elif order.order_type == "sell":
            self.asks.remove(order)

    def get_order_book(self):
        current_time = time.time()
        return {
            "bids": [(order.price, order.amount) for order in self.bids if order.expiration > current_time],
            "asks": [(order.price, order.amount) for order in self.asks if order.expiration > current_time]
        }

    def clean_expired_orders(self):
        current_time = time.time()
        self.bids = [bid for bid in self.bids if bid.expiration > current_time]
        self.asks = [ask for ask in self.asks if ask.expiration > current_time]
