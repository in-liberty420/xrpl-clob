import json
from xrpl.clients import JsonRpcClient
from xrpl.wallet import generate_faucet_wallet
from xrpl.models import Payment
from xrpl.transaction import submit_and_wait, sign
from xrpl.utils import xrp_to_drops

def fund_new_wallet():
    # Initialize the client
    client = JsonRpcClient("https://s.altnet.rippletest.net:51234")

    # Generate a new wallet funded by the Testnet faucet
    new_wallet = generate_faucet_wallet(client, debug=True)
    print(f"Generated new wallet: {new_wallet.classic_address}")

    # Generate another wallet to fund the new wallet
    funding_wallet = generate_faucet_wallet(client, debug=True)

    # Create a payment transaction to send XRP to the new wallet
    payment = Payment(
        account=funding_wallet.classic_address,
        amount=xrp_to_drops(1000),  # Send 1000 XRP
        destination=new_wallet.classic_address
    )

    # Sign and submit the transaction
    signed_tx = sign(payment, funding_wallet)
    submit_result = submit_and_wait(signed_tx, client)

    if submit_result.is_successful():
        print(f"Successfully funded new wallet with 1000 XRP. Transaction hash: {submit_result.result['hash']}")
        
        # Save the new wallet info to a file
        wallet_info = {
            "classic_address": new_wallet.classic_address,
            "public_key": new_wallet.public_key,
            "private_key": new_wallet.private_key
        }
        with open("funded_wallet.json", "w") as f:
            json.dump(wallet_info, f, indent=2)
        print("New wallet info saved to funded_wallet.json")
    else:
        print(f"Failed to fund new wallet. Error: {submit_result.result}")

if __name__ == "__main__":
    fund_new_wallet()
