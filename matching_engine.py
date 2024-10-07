import time
from collections import defaultdict

class MatchingEngine:
    def __init__(self, order_book, batch_interval=5):  # 5 seconds batch interval
        self.order_book = order_book
        self.batch_interval = batch_interval
        self.last_batch_time = time.time()

    def run_batch_auction(self):
        current_time = time.time()
        if current_time - self.last_batch_time >= self.batch_interval:
            self.match_orders()
            self.last_batch_time = current_time

    def match_orders(self):
        # Aggregate demand and supply
        demand = defaultdict(float)
        supply = defaultdict(float)

        for bid in self.order_book.bids:
            for price in range(int(bid.price * 100), 0, -1):
                demand[price / 100] += bid.amount

        for ask in self.order_book.asks:
            for price in range(1, int(ask.price * 100) + 1):
                supply[price / 100] += ask.amount

        # Find clearing price
        clearing_price = None
        max_volume = 0
        for price in sorted(set(demand.keys()) | set(supply.keys())):
            volume = min(demand[price], supply[price])
            if volume > max_volume:
                max_volume = volume
                clearing_price = price

        if clearing_price is None:
            return  # No trades possible

        # Execute trades
        executed_volume = min(demand[clearing_price], supply[clearing_price])
        print(f"Batch auction executed: {executed_volume} @ {clearing_price}")

        # Update order book
        self.update_order_book(clearing_price, executed_volume)

    def update_order_book(self, clearing_price, executed_volume):
        remaining_volume = executed_volume

        # Process bids
        for bid in self.order_book.bids[:]:
            if bid.price >= clearing_price:
                if bid.amount <= remaining_volume:
                    remaining_volume -= bid.amount
                    self.order_book.remove_order(bid)
                else:
                    bid.amount -= remaining_volume
                    break

        remaining_volume = executed_volume

        # Process asks
        for ask in self.order_book.asks[:]:
            if ask.price <= clearing_price:
                if ask.amount <= remaining_volume:
                    remaining_volume -= ask.amount
                    self.order_book.remove_order(ask)
                else:
                    ask.amount -= remaining_volume
                    break

        # Remove expired orders
        current_time = time.time()
        self.order_book.bids = [bid for bid in self.order_book.bids if bid.expiration > current_time]
        self.order_book.asks = [ask for ask in self.order_book.asks if ask.expiration > current_time]
