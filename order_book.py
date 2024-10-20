import time
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

class Order:
    def __init__(self, price, amount, order_type, xrp_address, public_key, expiration=None, sequence=None, payment_tx_signature=None, multisig_destination=None, last_ledger_sequence=None, signed_tx_json=None):
        self.price = price
        self.amount = int(amount)  # Convert to integer here
        self.order_type = order_type
        self.xrp_address = xrp_address
        self.public_key = public_key
        self.expiration = expiration if expiration is not None else int(time.time()) + 300  # Unix time, 5 minutes from now
        self.sequence = sequence
        self.payment_tx_signature = payment_tx_signature
        self.multisig_destination = multisig_destination
        self.last_ledger_sequence = last_ledger_sequence
        self.signed_tx_json = signed_tx_json

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
        self.order_map[order.payment_tx_signature] = order  # Using payment_tx_signature as a unique identifier
        logger.info(f"Order added to the book: {order.__dict__}")

    def remove_order(self, order):
        if order.order_type == "buy":
            self.bids[order.price].remove(order)
            if not self.bids[order.price]:
                del self.bids[order.price]
        elif order.order_type == "sell":
            self.asks[order.price].remove(order)
            if not self.asks[order.price]:
                del self.asks[order.price]
        del self.order_map[order.payment_tx_signature]

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
        self.order_map = {tx_sig: order for tx_sig, order in self.order_map.items() if order.expiration > current_time}
