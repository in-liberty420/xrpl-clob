import json
from xrpl.clients import JsonRpcClient
from xrpl.wallet import generate_faucet_wallet, Wallet
from xrpl.models import Payment
from xrpl.transaction import submit_and_wait, sign
from xrpl.utils import xrp_to_drops

def fund_existing_wallet(existing_address: str, amount_xrp: int = 1000):
    # Initialize the client
    client = JsonRpcClient("https://s.altnet.rippletest.net:51234")

    # Generate a funding wallet using the Testnet faucet
    funding_wallet = generate_faucet_wallet(client, debug=True)
    print(f"Generated funding wallet: {funding_wallet.classic_address}")

    # Create a payment transaction to send XRP to the existing wallet
    payment = Payment(
        account=funding_wallet.classic_address,
        amount=xrp_to_drops(amount_xrp),
        destination=existing_address
    )

    # Sign and submit the transaction
    signed_tx = sign(payment, funding_wallet)
    submit_result = submit_and_wait(signed_tx, client)

    if submit_result.is_successful():
        print(f"Successfully funded existing wallet {existing_address} with {amount_xrp} XRP. Transaction hash: {submit_result.result['hash']}")
    else:
        print(f"Failed to fund existing wallet. Error: {submit_result.result}")

if __name__ == "__main__":
    existing_wallet_address = "rM3wUBADU4ctaYeFizTxYfPAmU7botXoTr"
    fund_existing_wallet(existing_wallet_address)
