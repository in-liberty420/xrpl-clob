from flask import Flask, request, jsonify
from order_book import Order

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
            order = Order(data['price'], data['amount'], data['order_type'], data['user_id'])
            self.order_book.add_order(order)
            return jsonify({"status": "success", "message": "Order placed successfully"})

        @self.app.route('/order_book', methods=['GET'])
        def get_order_book():
            return jsonify(self.order_book.get_order_book())

    def run(self):
        self.app.run(debug=True)
