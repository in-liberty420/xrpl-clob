import json
from xrpl.wallet import generate_faucet_wallet
from xrpl.clients import JsonRpcClient

def create_and_fund_wallet():
    client = JsonRpcClient("https://s.altnet.rippletest.net:51234")
    wallet = generate_faucet_wallet(client)
    
    wallet_info = {
        "public_key": wallet.public_key,
        "private_key": wallet.private_key,
        "classic_address": wallet.classic_address
    }
    
    with open("test_wallet.json", "w") as f:
        json.dump(wallet_info, f)
    
    print(f"Wallet created and funded. Address: {wallet.classic_address}")

if __name__ == "__main__":
    create_and_fund_wallet()
