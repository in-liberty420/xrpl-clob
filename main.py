from order_book import OrderBook
from matching_engine import MatchingEngine
from api import API
from xrpl_integration import XRPLIntegration

def main():
    order_book = OrderBook()
    xrpl_integration = XRPLIntegration()
    matching_engine = MatchingEngine(order_book, xrpl_integration)
    api = API(order_book, matching_engine, xrpl_integration)
    
    # Start the API server
    api.run()

if __name__ == "__main__":
    main()
