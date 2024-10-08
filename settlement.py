from xrpl.transaction import XRPLReliableSubmissionException
import logging

logger = logging.getLogger(__name__)

class Settlement:
    def __init__(self, xrpl_integration, multisig_wallet):
        self.xrpl_integration = xrpl_integration
        self.multisig_wallet = multisig_wallet

    def process_matched_orders(self, matched_orders):
        for buy_order, sell_order in matched_orders:
            # Create and submit incoming transactions
            buy_tx = self.xrpl_integration.create_payment_transaction(
                buy_order.xrp_address,
                self.multisig_wallet.get_address(),
                buy_order.amount
            )
            sell_tx = self.xrpl_integration.create_payment_transaction(
                sell_order.xrp_address,
                self.multisig_wallet.get_address(),
                sell_order.amount
            )

            if not self.submit_transaction(buy_tx, "Incoming buy") or not self.submit_transaction(sell_tx, "Incoming sell"):
                logger.error("Failed to process incoming transactions. Invalidating auction.")
                return False

            # Create and submit outgoing transactions
            buy_payout = self.xrpl_integration.create_payment_transaction(
                self.multisig_wallet.get_address(),
                buy_order.xrp_address,
                buy_order.amount  # This should be the amount of the asset bought, not XRP
            )
            sell_payout = self.xrpl_integration.create_payment_transaction(
                self.multisig_wallet.get_address(),
                sell_order.xrp_address,
                sell_order.amount * sell_order.price  # This converts the XRP amount to the equivalent in the other asset
            )

            if not self.submit_transaction(buy_payout, "Outgoing buy payout") or not self.submit_transaction(sell_payout, "Outgoing sell payout"):
                logger.error("Failed to process outgoing transactions.")
                # You might want to implement some recovery logic here
                return False

        return True

    def submit_transaction(self, transaction, description):
        signed_tx = self.multisig_wallet.sign_transaction(transaction)
        try:
            result = self.xrpl_integration.submit_transaction(signed_tx)
            if result.is_successful():
                logger.info(f"{description} transaction submitted successfully: {result.result['hash']}")
                return True
            else:
                logger.error(f"{description} transaction failed: {result.result}")
                return False
        except XRPLReliableSubmissionException as e:
            logger.error(f"Error submitting {description} transaction: {e}")
            return False
