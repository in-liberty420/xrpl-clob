import time
from collections import defaultdict

class Order:
    def __init__(self, price, amount, order_type, xrp_address, public_key, signature, expiration=None, sequence=None, payment_tx_signature=None, multisig_destination=None, last_ledger_sequence=None):
        self.price = price
        self.amount = amount
        self.order_type = order_type
        self.xrp_address = xrp_address
        self.public_key = public_key
        self.signature = signature
        self.expiration = expiration if expiration is not None else int(time.time()) + 300  # Unix time, 5 minutes from now
        self.sequence = sequence
        self.payment_tx_signature = payment_tx_signature
        self.multisig_destination = multisig_destination
        self.last_ledger_sequence = last_ledger_sequence

class OrderBook:
    def __init__(self):
        self.bids = defaultdict(list)
        self.asks = defaultdict(list)
        self.order_map = {}

    def add_order(self, order):
        if order.order_type == "buy":
            self.bids[order.price].append(order)
        elif order.order_type == "sell":
            self.asks[order.price].append(order)
        self.order_map[order.signature] = order  # Using signature as a unique identifier

    def remove_order(self, order):
        if order.order_type == "buy":
            self.bids[order.price].remove(order)
            if not self.bids[order.price]:
                del self.bids[order.price]
        elif order.order_type == "sell":
            self.asks[order.price].remove(order)
            if not self.asks[order.price]:
                del self.asks[order.price]
        del self.order_map[order.signature]

    def get_l2_order_book(self):
        current_time = int(time.time())
        return {
            "bids": [(price, sum(order.amount for order in orders if order.expiration > current_time))
                     for price, orders in sorted(self.bids.items(), reverse=True)],
            "asks": [(price, sum(order.amount for order in orders if order.expiration > current_time))
                     for price, orders in sorted(self.asks.items())]
        }

    def clean_expired_orders(self):
        current_time = int(time.time())
        for price, orders in list(self.bids.items()):
            self.bids[price] = [order for order in orders if order.expiration > current_time]
            if not self.bids[price]:
                del self.bids[price]
        for price, orders in list(self.asks.items()):
            self.asks[price] = [order for order in orders if order.expiration > current_time]
            if not self.asks[price]:
                del self.asks[price]
        self.order_map = {sig: order for sig, order in self.order_map.items() if order.expiration > current_time}
