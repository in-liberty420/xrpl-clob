from flask import Flask, request, jsonify
from order_book import Order
from order_signing import sign_order, verify_order_signature
from xrpl.wallet import Wallet
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
            wallet = Wallet(data['private_key'])  # In a real app, don't send private keys!
            
            order_data = {
                'price': data['price'],
                'amount': data['amount'],
                'order_type': data['order_type'],
                'expiration': data.get('expiration', time.time() + 300)
            }
            
            signature = sign_order(order_data, wallet)
            
            order = Order(
                price=order_data['price'],
                amount=order_data['amount'],
                order_type=order_data['order_type'],
                xrp_address=wallet.classic_address,
                signature=signature,
                expiration=order_data['expiration']
            )
            
            if verify_order_signature(order):
                self.order_book.add_order(order)
                self.matching_engine.run_batch_auction()
                return jsonify({"status": "success", "message": "Order placed successfully"})
            else:
                return jsonify({"status": "error", "message": "Invalid order signature"}), 400

        @self.app.route('/order_book', methods=['GET'])
        def get_order_book():
            self.order_book.clean_expired_orders()  # Clean expired orders before returning the order book
            return jsonify(self.order_book.get_order_book())

    def run(self):
        self.app.run(debug=True)
