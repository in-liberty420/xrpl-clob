from xrpl.core.keypairs import sign
from xrpl.core.addresscodec import classic_address_to_xaddress
from xrpl.core.binarycodec import decode

def sign_order(order_data, wallet):
    """Sign an order using an XRP wallet"""
    message = f"{order_data['price']},{order_data['amount']},{order_data['order_type']},{order_data['expiration']}"
    signature = sign(message.encode(), wallet.private_key)
    return signature

def verify_order_signature(order):
    """Verify the signature of an order"""
    from xrpl.core import keypairs
    message = f"{order.price},{order.amount},{order.order_type},{order.expiration}"
    public_key = keypairs.derive_public_key(order.signature)
    derived_address = classic_address_to_xaddress(keypairs.derive_classic_address(public_key), tag=None, is_test=True)
    return derived_address == order.xrp_address and keypairs.is_valid_message(message.encode(), order.signature, public_key)
