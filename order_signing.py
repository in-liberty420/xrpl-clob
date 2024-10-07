from xrpl.core import keypairs
from xrpl.core.addresscodec import decode_classic_address
import logging

logger = logging.getLogger(__name__)

def sign_order(order_data, wallet):
    """Sign an order using an XRP wallet"""
    message = f"{order_data['price']},{order_data['amount']},{order_data['order_type']},{order_data['expiration']}"
    signature = keypairs.sign(message.encode(), wallet.private_key)
    return signature

def verify_order_signature(order, message):
    """Verify the signature of an order"""
    try:
        logger.debug(f"Verifying signature for order: {order.__dict__}")
        logger.debug(f"Message to verify: {message}")
        logger.debug(f"Signature to verify: {order.signature}")
        logger.debug(f"XRP address: {order.xrp_address}")
        
        # Convert the signature from hex to bytes
        signature_bytes = bytes.fromhex(order.signature)
        logger.debug(f"Signature bytes: {signature_bytes}")
        
        # Derive public key from XRP address
        public_key = keypairs.derive_public_key(order.xrp_address)
        logger.debug(f"Derived public key: {public_key}")
        
        # Verify the signature
        result = keypairs.is_valid_message(message.encode(), signature_bytes, public_key)
        logger.debug(f"Signature verification result: {result}")
        return result
    except Exception as e:
        logger.error(f"Error verifying signature: {str(e)}", exc_info=True)
        return False
