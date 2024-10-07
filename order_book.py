class Order:
    def __init__(self, price, amount, order_type, user_id):
        self.price = price
        self.amount = amount
        self.order_type = order_type
        self.user_id = user_id

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
        return {
            "bids": [(order.price, order.amount) for order in self.bids],
            "asks": [(order.price, order.amount) for order in self.asks]
        }
