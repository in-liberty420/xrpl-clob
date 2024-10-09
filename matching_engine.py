import time
import logging
from collections import defaultdict
from settlement import Settlement

logger = logging.getLogger(__name__)

class MatchingEngine:
    def __init__(self, order_book, xrpl_integration, multisig_wallet, batch_interval=5):  # 5 seconds batch interval
        self.order_book = order_book
        self.xrpl_integration = xrpl_integration
        self.batch_interval = batch_interval
        self.last_batch_time = int(time.time())
        self.last_clearing_price = None
        self.settlement = Settlement(xrpl_integration, multisig_wallet)

    def run_batch_auction(self):
        current_time = int(time.time())
        if current_time - self.last_batch_time >= self.batch_interval:
            logger.info(f"Running batch auction at {current_time}")
            self.match_orders()
            self.last_batch_time = current_time

    def match_orders(self):
        logger.info("Starting order matching process")
        # Clean expired orders before matching
        self.clean_order_book()

        # Aggregate demand and supply
        demand = self.order_book.bids
        supply = self.order_book.asks

        # Find clearing price and max volume
        clearing_price, max_volume = self.find_clearing_price(demand, supply)

        if clearing_price is not None:
            logger.info(f"Clearing price found: {clearing_price}, Max volume: {max_volume}")
            # Execute trades using pro-rata matching
            self.execute_trades(clearing_price, max_volume, demand, supply)
        else:
            logger.info("No matching orders found in this batch")

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
            elif volume == max_volume and clearing_price is not None:
                # If volume is the same, choose the price closest to the last traded price
                if self.last_clearing_price is not None:
                    if abs(price - self.last_clearing_price) < abs(clearing_price - self.last_clearing_price):
                        clearing_price = price

        if clearing_price is not None:
            self.last_clearing_price = clearing_price

        return clearing_price, max_volume

    def execute_trades(self, clearing_price, max_volume, demand, supply):
        print(f"Batch auction executed: {max_volume} @ {clearing_price}")

        total_demand = sum(sum(order.amount for order in demand[p]) for p in demand if p >= clearing_price)
        total_supply = sum(sum(order.amount for order in supply[p]) for p in supply if p <= clearing_price)

        matched_orders = []

        # Pro-rata matching for bids
        matched_orders.extend(self.pro_rata_match(demand, clearing_price, max_volume, total_demand, lambda p: p >= clearing_price))

        # Pro-rata matching for asks
        matched_orders.extend(self.pro_rata_match(supply, clearing_price, max_volume, total_supply, lambda p: p <= clearing_price))

        current_ledger = self.xrpl_integration.get_current_ledger_sequence()
        valid_orders = [
            (order, filled_amount) for order, filled_amount in matched_orders 
            if order.last_ledger_sequence is None or order.last_ledger_sequence > current_ledger
        ]

        # Update order amounts after matching
        for order, filled_amount in valid_orders:
            order.matched_amount = filled_amount
            order.amount -= filled_amount

        # Process settlement
        if self.settlement.process_matched_orders([order for order, _ in valid_orders]):
            # Remove fully filled orders and update partially filled orders
            self.update_order_book(valid_orders)
        else:
            # If settlement failed, we need to invalidate this auction
            print("Settlement failed. Invalidating this auction.")
            # You might want to implement some recovery logic here

        # Clean expired orders and remove 0 volume orders
        self.clean_order_book()

    def pro_rata_match(self, orders, clearing_price, max_volume, total_eligible_volume, price_condition):
        eligible_orders = [order for price, order_list in orders.items() if price_condition(price) for order in order_list]
        matched_orders = []
        
        for order in eligible_orders:
            if total_eligible_volume > 0:
                fill_ratio = min(1, max_volume / total_eligible_volume)
                filled_amount = min(order.amount, order.amount * fill_ratio)
                matched_orders.append((order, filled_amount))
                max_volume -= filled_amount
                total_eligible_volume -= order.amount
        
        return matched_orders

    def clean_order_book(self):
        current_time = int(time.time())
        for price in list(self.order_book.bids.keys()):
            for order in self.order_book.bids[price]:
                if order.expiration <= current_time or order.amount == 0:
                    self.order_book.remove_order(order)
            if not self.order_book.bids[price]:
                del self.order_book.bids[price]
        
        for price in list(self.order_book.asks.keys()):
            for order in self.order_book.asks[price]:
                if order.expiration <= current_time or order.amount == 0:
                    self.order_book.remove_order(order)
            if not self.order_book.asks[price]:
                del self.order_book.asks[price]
