import os
import logging
from order_book import OrderBook
from matching_engine import MatchingEngine
from api import API
from xrpl_integration import XRPLIntegration
from multisig import MultisigWallet

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    order_book = OrderBook()
    xrpl_integration = XRPLIntegration()
    multisig_wallet = MultisigWallet()
    
    if os.path.exists("encrypted_wallet.key"):
        try:
            multisig_wallet.load_wallet()
            logger.info("Existing wallet loaded successfully.")
        except ValueError as e:
            logger.error(f"Error loading wallet: {str(e)}")
            return
    else:
        try:
            multisig_wallet.create_wallet()
            logger.info("New wallet created successfully.")
        except ValueError as e:
            logger.error(f"Error creating wallet: {str(e)}")
            return
    
    multisig_address = multisig_wallet.get_address()
    logger.info(f"Multisig wallet address: {multisig_address}")
    
    with open("multisig_address.txt", "w") as f:
        f.write(multisig_address)
    
    matching_engine = MatchingEngine(order_book, xrpl_integration, multisig_wallet)
    api = API(order_book, matching_engine, xrpl_integration)
    
    # Run the API in the main thread
    api.run()

if __name__ == "__main__":
    main()
