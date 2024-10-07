import time
from collections import defaultdict

class MatchingEngine:
    def __init__(self, order_book, batch_interval=5):  # 5 seconds batch interval
        self.order_book = order_book
        self.batch_interval = batch_interval
        self.last_batch_time = time.time()
        self.last_clearing_price = None

    def run_batch_auction(self):
        current_time = time.time()
        if current_time - self.last_batch_time >= self.batch_interval:
            self.match_orders()
            self.last_batch_time = current_time

    def match_orders(self):
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
        clearing_price = None

        for price in all_prices:
            cumulative_demand = sum(sum(order.amount for order in demand[p]) for p in demand if p >= price)
            cumulative_supply = sum(sum(order.amount for order in supply[p]) for p in supply if p <= price)
            volume = min(cumulative_demand, cumulative_supply)

            if volume > max_volume:
                max_volume = volume
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

        # Remove fully filled orders and update partially filled orders
        self.clean_order_book()

    def pro_rata_match(self, orders, clearing_price, executed_volume, price_condition):
        eligible_orders = [
            order for price, order_list in orders.items()
            if price_condition(price)
            for order in order_list
        ]

        total_eligible_volume = sum(order.amount for order in eligible_orders)

        for order in eligible_orders:
            fill_ratio = min(1, executed_volume / total_eligible_volume)
            filled_amount = order.amount * fill_ratio
            order.amount -= filled_amount
            # Here you would typically record the trade or notify the user

    def clean_order_book(self):
        self.order_book.clean_expired_orders()
