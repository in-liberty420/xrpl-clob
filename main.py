from order_book import OrderBook
from matching_engine import MatchingEngine
from api import API
from xrpl_integration import XRPLIntegration
from multisig import MultisigWallet

def main():
    order_book = OrderBook()
    xrpl_integration = XRPLIntegration()
    multisig_wallet = MultisigWallet()
    multisig_wallet.load_wallet()  # Assuming the wallet is already created and stored
    matching_engine = MatchingEngine(order_book, xrpl_integration, multisig_wallet)
    api = API(order_book, matching_engine, xrpl_integration)
    
    # Start the API server
    api.run()

if __name__ == "__main__":
    main()
