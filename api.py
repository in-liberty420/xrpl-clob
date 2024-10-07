from flask import Flask, request, jsonify
from order_book import Order
import time

class API:
    def __init__(self, order_book, matching_engine, xrpl_integration):
        self.app = Flask(__name__)
        self.order_book = order_book
        self.matching_engine = matching_engine
        self.xrpl_integration = xrpl_integration

        self.setup_routes()

    def setup_routes(self):
        @self.app.route('/place_order', methods=['POST'])
        def place_order():
            data = request.json
            expiration = data.get('expiration', time.time() + 300)  # Default 5 minutes expiration
            order = Order(data['price'], data['amount'], data['order_type'], data['user_id'], expiration)
            self.order_book.add_order(order)
            self.matching_engine.run_batch_auction()  # Trigger a batch auction after each new order
            return jsonify({"status": "success", "message": "Order placed successfully"})

        @self.app.route('/order_book', methods=['GET'])
        def get_order_book():
            self.order_book.clean_expired_orders()  # Clean expired orders before returning the order book
            return jsonify(self.order_book.get_order_book())

    def run(self):
        self.app.run(debug=True)
