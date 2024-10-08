import json
import asyncio
from xrpl.asyncio.clients import AsyncJsonRpcClient
from xrpl.models.transactions import Payment
from xrpl.asyncio.transaction import autofill_and_sign
from xrpl.wallet import Wallet
from xrpl.core import keypairs
from xrpl.core.binarycodec import encode_for_signing

async def main():
    # Load the test wallet
    with open("test_wallet.json", "r") as f:
        wallet_info = json.load(f)

    # Create a wallet from the loaded information
    wallet = Wallet(wallet_info['public_key'], wallet_info['private_key'])

    # Create a simple payment transaction
    payment = Payment(
        account=wallet.classic_address,
        amount="1000000",  # 1 XRP in drops
        destination="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"
    )

    # Create a client connection
    async with AsyncJsonRpcClient("https://s.altnet.rippletest.net:51234") as client:
        # Autofill and sign the transaction (but don't submit)
        signed_tx = await autofill_and_sign(payment, wallet, client)

        # Extract the relevant parts of the signed transaction
        tx_blob = signed_tx.to_xrpl()
        signature = tx_blob["TxnSignature"]
        signed_tx_json = signed_tx.to_dict()

        print(f"Signed transaction: {json.dumps(signed_tx_json, indent=2)}")
        print(f"Signature: {signature}")

        # Verify the signature
        # First, we need to recreate the signing data
        signing_data = encode_for_signing(signed_tx_json)

        # Now verify the signature
        is_valid = keypairs.is_valid_message(
            message=signing_data,
            signature=bytes.fromhex(signature),
            public_key=wallet.public_key
        )

        print(f"Signature valid: {is_valid}")

        # As an additional check, let's verify using the built-in verify method
        is_valid_builtin = signed_tx.verify()

        print(f"Signature valid (using built-in verify): {is_valid_builtin}")

if __name__ == "__main__":
    asyncio.run(main())
