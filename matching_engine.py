import time
from collections import defaultdict
from settlement import Settlement

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
            self.match_orders()
            self.last_batch_time = current_time

    def match_orders(self):
        # Clean expired orders before matching
        self.clean_order_book()

        # Aggregate demand and supply
        demand = self.order_book.bids
        supply = self.order_book.asks

        # Find clearing price and max volume
        clearing_price, max_volume = self.find_clearing_price(demand, supply)

        if clearing_price is not None:
            # Execute trades using pro-rata matching
            self.execute_trades(clearing_price, max_volume, demand, supply)

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

        # Update order amounts after matching
        for order, filled_amount in matched_orders:
            order.matched_amount = filled_amount
            order.amount -= filled_amount

        # Process settlement
        if self.settlement.process_matched_orders([order for order, _ in matched_orders]):
            # Remove fully filled orders and update partially filled orders
            self.update_order_book(matched_orders)
        else:
            # If settlement failed, we need to invalidate this auction
            print("Settlement failed. Invalidating this auction.")
            # You might want to implement some recovery logic here

        # Clean expired orders
        self.clean_order_book()

    def update_order_book(self, matched_orders):
        for order, filled_amount in matched_orders:
            if order.amount == 0:
                self.order_book.remove_order(order)
            else:
                # Update the order in the order book with the new amount
                existing_order = self.order_book.order_map.get(order.signature)
                if existing_order:
                    existing_order.amount = order.amount

    def remove_filled_orders(self):
        for price in list(self.order_book.bids.keys()):
            self.order_book.bids[price] = [order for order in self.order_book.bids[price] if order.amount > 0]
            if not self.order_book.bids[price]:
                del self.order_book.bids[price]
        
        for price in list(self.order_book.asks.keys()):
            self.order_book.asks[price] = [order for order in self.order_book.asks[price] if order.amount > 0]
            if not self.order_book.asks[price]:
                del self.order_book.asks[price]

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
            self.order_book.bids[price] = [order for order in self.order_book.bids[price] if order.expiration > current_time]
            if not self.order_book.bids[price]:
                del self.order_book.bids[price]
        
        for price in list(self.order_book.asks.keys()):
            self.order_book.asks[price] = [order for order in self.order_book.asks[price] if order.expiration > current_time]
            if not self.order_book.asks[price]:
                del self.order_book.asks[price]
        
        # Clean up the order_map
        self.order_book.order_map = {sig: order for sig, order in self.order_book.order_map.items() if order.expiration > current_time}
