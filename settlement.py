from xrpl.models import Payment
from xrpl.transaction import submit_and_wait, XRPLReliableSubmissionException
import logging

logger = logging.getLogger(__name__)

class Settlement:
    def __init__(self, xrpl_integration, multisig_wallet):
        self.xrpl_integration = xrpl_integration
        self.multisig_wallet = multisig_wallet

    def process_matched_orders(self, matched_orders):
        incoming_transactions = []
        for buy_order, sell_order in matched_orders:
            buy_tx = self.create_incoming_transaction(buy_order)
            sell_tx = self.create_incoming_transaction(sell_order)
            incoming_transactions.extend([buy_tx, sell_tx])
        
        if not self.submit_incoming_transactions(incoming_transactions):
            logger.error("Failed to process all incoming transactions. Invalidating auction.")
            return False

        outgoing_transactions = []
        for buy_order, sell_order in matched_orders:
            buy_payout = self.create_outgoing_transaction(buy_order, "XRP")
            sell_payout = self.create_outgoing_transaction(sell_order, "USD")  # Assuming USD for simplicity
            outgoing_transactions.extend([buy_payout, sell_payout])

        self.submit_outgoing_transactions(outgoing_transactions)
        return True

    def create_incoming_transaction(self, order):
        return Payment(
            account=order.xrp_address,
            destination=self.multisig_wallet.get_address(),
            amount=str(order.amount),
            sequence=order.sequence
        )

    def create_outgoing_transaction(self, order, asset_type):
        amount = order.amount if asset_type == "XRP" else order.amount * order.price
        return Payment(
            account=self.multisig_wallet.get_address(),
            destination=order.xrp_address,
            amount=str(amount),
            sequence=self.xrpl_integration.get_account_sequence(self.multisig_wallet.get_address())
        )

    def submit_incoming_transactions(self, transactions):
        for tx in transactions:
            try:
                result = submit_and_wait(tx, self.xrpl_integration.client)
                if result.is_successful():
                    logger.info(f"Incoming transaction submitted successfully: {result.result['hash']}")
                else:
                    logger.error(f"Incoming transaction failed: {result.result}")
                    return False
            except XRPLReliableSubmissionException as e:
                logger.error(f"Error submitting incoming transaction: {e}")
                return False
        return True

    def submit_outgoing_transactions(self, transactions):
        for tx in transactions:
            signed_tx = self.multisig_wallet.sign_transaction(tx)
            try:
                result = submit_and_wait(signed_tx, self.xrpl_integration.client)
                if result.is_successful():
                    logger.info(f"Outgoing transaction submitted successfully: {result.result['hash']}")
                else:
                    logger.error(f"Outgoing transaction failed: {result.result}")
            except XRPLReliableSubmissionException as e:
                logger.error(f"Error submitting outgoing transaction: {e}")
