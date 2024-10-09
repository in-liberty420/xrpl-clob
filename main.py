import os
import asyncio
from order_book import OrderBook
from matching_engine import MatchingEngine
from api import API
from xrpl_integration import XRPLIntegration
from multisig import MultisigWallet

async def run_matching_engine(matching_engine):
    while True:
        matching_engine.run_batch_auction()
        await asyncio.sleep(5)  # Wait for 5 seconds before the next auction

async def main():
    order_book = OrderBook()
    xrpl_integration = XRPLIntegration()
    multisig_wallet = MultisigWallet()
    
    if os.path.exists("encrypted_wallet.key"):
        try:
            multisig_wallet.load_wallet()
            print("Existing wallet loaded successfully.")
        except ValueError as e:
            print(f"Error loading wallet: {str(e)}")
            return
    else:
        try:
            multisig_wallet.create_wallet()
            print("New wallet created successfully.")
        except ValueError as e:
            print(f"Error creating wallet: {str(e)}")
            return
    
    multisig_address = multisig_wallet.get_address()
    print(f"Multisig wallet address: {multisig_address}")
    
    with open("multisig_address.txt", "w") as f:
        f.write(multisig_address)
    
    matching_engine = MatchingEngine(order_book, xrpl_integration, multisig_wallet)
    api = API(order_book, matching_engine, xrpl_integration)
    
    # Start the matching engine in a separate task
    asyncio.create_task(run_matching_engine(matching_engine))
    
    # Start the API server
    await api.run()

if __name__ == "__main__":
    asyncio.run(main())
