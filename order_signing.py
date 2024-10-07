from xrpl.core.keypairs import sign, verify
from xrpl.wallet import Wallet

def sign_order(order_data, wallet):
    """Sign an order using an XRP wallet"""
    message = f"{order_data['price']},{order_data['amount']},{order_data['order_type']},{order_data['expiration']}"
    signature = sign(message, wallet.private_key)
    return signature

def verify_order_signature(order):
    """Verify the signature of an order"""
    message = f"{order.price},{order.amount},{order.order_type},{order.expiration}"
    return verify(message, order.signature, order.xrp_address)
