import json
from xrpl.core import keypairs
from xrpl.transaction import safe_sign_and_autofill_transaction
from xrpl.models import Payment
from xrpl.wallet import Wallet
from xrpl.core.binarycodec import encode_for_signing, decode

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

# Sign the transaction
signed_tx = safe_sign_and_autofill_transaction(payment, wallet)

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
tx_blob_bytes = decode(signed_tx.to_xrpl())
is_valid_builtin = signed_tx.verify(tx_blob_bytes)

print(f"Signature valid (using built-in verify): {is_valid_builtin}")
