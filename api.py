from flask import Flask, request, jsonify
from order_book import Order, OrderBook
from order_signing import verify_order_signature
import json
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

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
            logger.debug(f"Received order data: {data}")
            
            try:
                order = Order(
                    price=data['price'],
                    amount=data['amount'],
                    order_type=data['order_type'],
                    xrp_address=data['xrp_address'],
                    signature=data['signature'],
                    expiration=data['expiration']
                )
                logger.debug(f"Created order object: {order.__dict__}")
                
                # Verify the signature
                message = json.dumps({k: data[k] for k in ['price', 'amount', 'order_type', 'expiration']})
                logger.debug(f"Message to verify: {message}")
                logger.debug(f"Signature to verify: {order.signature}")
                logger.debug(f"XRP address: {order.xrp_address}")
                
                verification_result = verify_order_signature(order, message)
                logger.debug(f"Signature verification result: {verification_result}")
                
                if verification_result:
                    self.order_book.add_order(order)
                    self.matching_engine.run_batch_auction()
                    logger.info(f"Order placed successfully: {order.__dict__}")
                    return jsonify({"status": "success", "message": "Order placed successfully"})
                else:
                    logger.warning(f"Invalid order signature for order: {order.__dict__}")
                    return jsonify({"status": "error", "message": "Invalid order signature"}), 400
            except Exception as e:
                logger.error(f"Error processing order: {str(e)}", exc_info=True)
                return jsonify({"status": "error", "message": str(e)}), 400

        @self.app.route('/order_book', methods=['GET'])
        def get_order_book():
            self.order_book.clean_expired_orders()
            book = self.order_book.get_order_book()
            logger.debug(f"Current order book: {book}")
            return jsonify(book)

    def run(self):
        self.app.run(debug=True)
