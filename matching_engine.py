import time
from collections import defaultdict

class MatchingEngine:
    def __init__(self, order_book, batch_interval=5):  # 5 seconds batch interval
        self.order_book = order_book
        self.batch_interval = batch_interval
        self.last_batch_time = int(time.time())
        self.last_clearing_price = None

    def run_batch_auction(self):
        current_time = int(time.time())
        if current_time - self.last_batch_time >= self.batch_interval:
            self.match_orders()
            self.last_batch_time = current_time

    def match_orders(self):
        # Clean expired orders before matching
        self.clean_order_book()

        # Aggregate demand and supply
        demand = self.order_book.bids
        supply = self.order_book.asks

        # Find clearing price
        clearing_price = self.find_clearing_price(demand, supply)

        if clearing_price is not None:
            # Execute trades using pro-rata matching
            self.execute_trades(clearing_price, demand, supply)

    def find_clearing_price(self, demand, supply):
        all_prices = sorted(set(demand.keys()) | set(supply.keys()))
        max_volume = 0
        min_imbalance = float('inf')
        clearing_price = None

        for price in all_prices:
            cumulative_demand = sum(sum(order.amount for order in demand[p]) for p in demand if p >= price)
            cumulative_supply = sum(sum(order.amount for order in supply[p]) for p in supply if p <= price)
            volume = min(cumulative_demand, cumulative_supply)
            imbalance = abs(cumulative_demand - cumulative_supply)

            if volume > max_volume or (volume == max_volume and imbalance < min_imbalance):
                max_volume = volume
                min_imbalance = imbalance
                clearing_price = price
            elif volume == max_volume and imbalance == min_imbalance:
                # If still tied, choose price closest to last traded price
                if self.last_clearing_price is not None:
                    if abs(price - self.last_clearing_price) < abs(clearing_price - self.last_clearing_price):
                        clearing_price = price

        if clearing_price is not None:
            self.last_clearing_price = clearing_price

        return self.last_clearing_price

    def execute_trades(self, clearing_price, demand, supply):
        executed_volume = min(
            sum(sum(order.amount for order in demand[p]) for p in demand if p >= clearing_price),
            sum(sum(order.amount for order in supply[p]) for p in supply if p <= clearing_price)
        )

        print(f"Batch auction executed: {executed_volume} @ {clearing_price}")

        # Pro-rata matching for bids
        self.pro_rata_match(demand, clearing_price, executed_volume, lambda p: p >= clearing_price)

        # Pro-rata matching for asks
        self.pro_rata_match(supply, clearing_price, executed_volume, lambda p: p <= clearing_price)

        # Remove fully filled orders
        self.remove_filled_orders()

        # Clean expired orders
        self.clean_order_book()

    def remove_filled_orders(self):
        for price in list(self.order_book.bids.keys()):
            self.order_book.bids[price] = [order for order in self.order_book.bids[price] if order.amount > 0]
            if not self.order_book.bids[price]:
                del self.order_book.bids[price]
        
        for price in list(self.order_book.asks.keys()):
            self.order_book.asks[price] = [order for order in self.order_book.asks[price] if order.amount > 0]
            if not self.order_book.asks[price]:
                del self.order_book.asks[price]

    def pro_rata_match(self, orders, clearing_price, executed_volume, price_condition):
        eligible_orders = [
            order for price, order_list in orders.items()
            if price_condition(price)
            for order in order_list
        ]

        total_eligible_volume = sum(order.amount for order in eligible_orders)

        for order in eligible_orders:
            if total_eligible_volume > 0:
                fill_ratio = min(1, executed_volume / total_eligible_volume)
                filled_amount = order.amount * fill_ratio
                order.amount -= filled_amount
                executed_volume -= filled_amount
                total_eligible_volume -= order.amount
            # Here you would typically record the trade or notify the user

    def clean_order_book(self):
        current_time = int(time.time())
        for price in list(self.order_book.bids.keys()):
            self.order_book.bids[price] = [order for order in self.order_book.bids[price] if order.expiration > current_time]
            if not self.order_book.bids[price]:
                del self.order_book.bids[price]
        
        for price in list(self.order_book.asks.keys()):
            self.order_book.asks[price] = [order for order in self.order_book.asks[price] if order.expiration > current_time]
            if not self.order_book.asks[price]:
                del self.order_book.asks[price]
        
        # Clean up the order_map
        self.order_book.order_map = {sig: order for sig, order in self.order_book.order_map.items() if order.expiration > current_time}
