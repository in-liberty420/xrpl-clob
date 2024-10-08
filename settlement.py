from xrpl.transaction import XRPLReliableSubmissionException
import logging

logger = logging.getLogger(__name__)

class Settlement:
    def __init__(self, xrpl_integration, multisig_wallet):
        self.xrpl_integration = xrpl_integration
        self.multisig_wallet = multisig_wallet

    def process_matched_orders(self, matched_orders):
        for order in matched_orders:
            if not self.execute_order(order):
                return False
        return True

    def execute_order(self, order):
        # Execute the full pre-signed transaction
        if not self.submit_transaction(order.payment_tx_signature, f"Full payment for {order.order_type} order"):
            return False

        # Calculate the amount to pay out
        payout_amount = order.amount * order.price if order.order_type == "sell" else order.amount

        # Create and submit the payout transaction
        payout_tx = self.xrpl_integration.create_payment_transaction(
            self.multisig_wallet.get_address(),
            order.xrp_address,
            payout_amount
        )
        return self.submit_transaction(payout_tx, f"Payout for {order.order_type} order")

    def submit_transaction(self, transaction, description):
        try:
            result = self.xrpl_integration.submit_transaction(transaction)
            if result.is_successful():
                logger.info(f"{description} transaction submitted successfully: {result.result['hash']}")
                return True
            else:
                logger.error(f"{description} transaction failed: {result.result}")
                return False
        except XRPLReliableSubmissionException as e:
            logger.error(f"Error submitting {description} transaction: {e}")
            return False
