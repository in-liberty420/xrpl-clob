import threading
import time

class OrderCleaner:
    def __init__(self, order_book, xrpl_integration):
        self.order_book = order_book
        self.xrpl_integration = xrpl_integration
        self.running = False

    def start(self):
        self.running = True
        threading.Thread(target=self._run).start()

    def stop(self):
        self.running = False

    def _run(self):
        while self.running:
            self._clean_orders()
            time.sleep(60)  # Run every minute

    def _clean_orders(self):
        for address in list(self.order_book.order_map.keys()):
            current_sequence = self.xrpl_integration.get_account_sequence(address)
            valid_orders = [order for order in self.order_book.order_map[address] if order.sequence >= current_sequence]
            self.order_book.order_map[address] = valid_orders
