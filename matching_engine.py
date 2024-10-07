import time

class MatchingEngine:
    def __init__(self, order_book, batch_interval=60):  # 60 seconds batch interval
        self.order_book = order_book
        self.batch_interval = batch_interval
        self.last_batch_time = time.time()

    def run_batch_auction(self):
        current_time = time.time()
        if current_time - self.last_batch_time >= self.batch_interval:
            self.match_orders()
            self.last_batch_time = current_time

    def match_orders(self):
        while self.order_book.bids and self.order_book.asks:
            best_bid = self.order_book.bids[0]
            best_ask = self.order_book.asks[0]

            if best_bid.price >= best_ask.price:
                # Match found
                trade_price = (best_bid.price + best_ask.price) / 2
                trade_amount = min(best_bid.amount, best_ask.amount)

                # Execute trade (in a real system, you'd call XRPL here)
                print(f"Trade executed: {trade_amount} @ {trade_price}")

                # Update orders
                best_bid.amount -= trade_amount
                best_ask.amount -= trade_amount

                # Remove filled orders
                if best_bid.amount == 0:
                    self.order_book.remove_order(best_bid)
                if best_ask.amount == 0:
                    self.order_book.remove_order(best_ask)
            else:
                # No more matches possible
                break
