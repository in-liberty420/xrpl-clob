from xrpl.core import keypairs

def sign_order(order_data, wallet):
    """Sign an order using an XRP wallet"""
    message = f"{order_data['price']},{order_data['amount']},{order_data['order_type']},{order_data['expiration']}"
    signature = keypairs.sign(message.encode(), wallet.private_key)
    return signature

def verify_order_signature(order, message):
    """Verify the signature of an order"""
    try:
        public_key = keypairs.derive_public_key(order.xrp_address)
        return keypairs.is_valid_message(message.encode(), bytes.fromhex(order.signature), public_key)
    except Exception as e:
        print(f"Error verifying signature: {str(e)}")
        return False
