import os
from order_book import OrderBook
from matching_engine import MatchingEngine
from api import API
from xrpl_integration import XRPLIntegration
from multisig import MultisigWallet

def main():
    order_book = OrderBook()
    xrpl_integration = XRPLIntegration()
    multisig_wallet = MultisigWallet()
    
    try:
        multisig_wallet.load_wallet()
        print("Existing wallet loaded successfully.")
    except (FileNotFoundError, ValueError):
        print("Creating new wallet...")
        multisig_wallet.create_wallet()
        print("New wallet created successfully.")
    
    matching_engine = MatchingEngine(order_book, xrpl_integration, multisig_wallet)
    api = API(order_book, matching_engine, xrpl_integration)
    
    # Start the API server
    api.run()

if __name__ == "__main__":
    main()
