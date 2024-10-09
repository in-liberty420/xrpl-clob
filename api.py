from flask import Flask, request, jsonify
from order_book import Order, OrderBook
import time
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class API:
    def __init__(self, order_book, matching_engine, xrpl_integration):
        self.app = Flask(__name__)
        self.order_book = order_book
        self.matching_engine = matching_engine
        self.xrpl_integration = xrpl_integration
        self.pending_orders = {}
        self.last_matching_time = time.time()

        self.setup_routes()
        self.process_pending_orders()  # Process any existing pending orders on startup

    def process_pending_orders(self):
        for address, orders in self.pending_orders.items():
            for order in orders:
                self.order_book.add_order(order)
            self.pending_orders[address] = []  # Clear processed orders

    def setup_routes(self):
        @self.app.route('/place_order', methods=['POST'])
        def place_order():
            data = request.json
            logger.debug(f"Received full order data: {data}")

            try:
                # Get the current sequence number
                current_sequence = self.xrpl_integration.get_account_sequence(data['xrp_address'])

                # Check if the provided sequence number is valid
                if data['sequence'] < current_sequence:
                    return jsonify({"status": "error", "message": "Invalid sequence number"}), 400

                # Check if multisig_destination is provided
                if 'multisig_destination' not in data:
                    return jsonify({"status": "error", "message": "Multisig destination is required"}), 400

                order = Order(
                    price=data['price'],
                    amount=data['amount_drops'],
                    order_type=data['order_type'],
                    xrp_address=data['xrp_address'],
                    public_key=data['public_key'],
                    expiration=data['expiration'],
                    sequence=data['sequence'],
                    payment_tx_signature=data['payment_tx_signature'],
                    multisig_destination=data['multisig_destination'],
                    last_ledger_sequence=data.get('last_ledger_sequence')
                )
                logger.debug(f"Created order object: {order.__dict__}")

                # Verify payment transaction signature
                payment_signature_valid = self.xrpl_integration.verify_payment_signature(
                    order.payment_tx_signature,
                    order.public_key,
                    data['signed_tx_json']
                )
                logger.debug(f"Payment signature verification result: {payment_signature_valid}")

                if not payment_signature_valid:
                    logger.warning(f"Invalid payment transaction signature for order: {order.__dict__}")
                    return jsonify({"status": "error", "message": "Invalid payment transaction signature"}), 400

                # Store the order in a pending orders list, sorted by sequence number
                self.pending_orders.setdefault(data['xrp_address'], []).append(order)
                self.pending_orders[data['xrp_address']].sort(key=lambda x: x.sequence)

                self.process_pending_orders()  # Process pending orders after adding a new one
                logger.info(f"Order placed and processed: {order.__dict__}")
                return jsonify({"status": "success", "message": "Order placed and processed"})

            except Exception as e:
                logger.error(f"Error processing order: {str(e)}", exc_info=True)
                return jsonify({"status": "error", "message": str(e)}), 400

        @self.app.route('/l2_order_book', methods=['GET'])
        def get_l2_order_book():
            self.order_book.clean_expired_orders()
            book = self.order_book.get_l2_order_book()
            logger.debug(f"Current L2 order book: {book}")
            return jsonify(book)

    def run(self):
        def run_matching_engine():
            current_time = time.time()
            if current_time - self.last_matching_time >= self.matching_engine.batch_interval:
                self.matching_engine.run_batch_auction()
                self.last_matching_time = current_time

        @self.app.before_request
        def before_request():
            run_matching_engine()

        self.app.run(debug=True)
