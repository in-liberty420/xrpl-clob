import json
from xrpl.clients import JsonRpcClient
from xrpl.wallet import generate_faucet_wallet
from xrpl.models import Payment
from xrpl.transaction import submit_and_wait, sign
from xrpl.utils import xrp_to_drops
from multisig import MultisigWallet

def fund_multisig_wallet():
    # Initialize the client
    client = JsonRpcClient("https://s.altnet.rippletest.net:51234")

    # Load the multisig wallet
    multisig_wallet = MultisigWallet()
    multisig_wallet.load_wallet()
    multisig_address = multisig_wallet.get_address()

    print(f"Funding multisig wallet: {multisig_address}")

    # Generate a new wallet funded by the Testnet faucet
    faucet_wallet = generate_faucet_wallet(client, debug=True)

    # Create a payment transaction to send XRP to the multisig wallet
    payment = Payment(
        account=faucet_wallet.classic_address,
        amount=xrp_to_drops(1000),  # Send 1000 XRP
        destination=multisig_address
    )

    # Sign and submit the transaction
    signed_tx = sign(payment, faucet_wallet)
    submit_result = submit_and_wait(signed_tx, client)

    if submit_result.is_successful():
        print(f"Successfully funded multisig wallet with 1000 XRP. Transaction hash: {submit_result.result['hash']}")
    else:
        print(f"Failed to fund multisig wallet. Error: {submit_result.result}")

if __name__ == "__main__":
    fund_multisig_wallet()
