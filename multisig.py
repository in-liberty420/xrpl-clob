from xrpl.wallet import Wallet
from xrpl.clients import JsonRpcClient
from xrpl.models.transactions import Payment
from xrpl.core import keypairs
import xrpl.account
import os
from cryptography.fernet import Fernet

class MultisigWallet:
    def __init__(self):
        self.client = JsonRpcClient("https://s.altnet.rippletest.net:51234")
        self.wallet = None
        self.key = self.load_key()

    def load_key(self):
        try:
            with open("encrypted_wallet.key", "rb") as file:
                encrypted_data = file.read()
                # Assuming the key is the first 44 bytes of the encrypted data
                return encrypted_data[:44]
        except FileNotFoundError:
            return None

    def create_wallet(self):
        if os.path.exists("encrypted_wallet.key"):
            raise ValueError("Wallet already exists. Use load_wallet() instead.")
        self.wallet = Wallet.create()
        self.key = Fernet.generate_key()
        self.encrypt_and_store_keys()
        return self.wallet.classic_address

    def encrypt_and_store_keys(self):
        if not self.wallet:
            raise ValueError("Wallet not created yet")
        
        f = Fernet(self.key)
        encrypted_seed = f.encrypt(self.wallet.seed.encode())
        
        with open("encrypted_wallet.key", "wb") as file:
            file.write(self.key + encrypted_seed)

    def load_wallet(self):
        if not os.path.exists("encrypted_wallet.key"):
            raise FileNotFoundError("Encrypted wallet file not found")
        
        if self.key is None:
            raise ValueError("Encryption key not found. Please create a wallet first.")
        
        with open("encrypted_wallet.key", "rb") as file:
            encrypted_data = file.read()
        
        encrypted_seed = encrypted_data[44:]  # The seed data starts after the key
        
        f = Fernet(self.key)
        decrypted_seed = f.decrypt(encrypted_seed).decode()
        self.wallet = Wallet.from_seed(decrypted_seed)

    def create_and_sign_transaction(self, destination, amount):
        if not self.wallet:
            raise ValueError("Wallet not loaded")
        
        payment = Payment(
            account=self.wallet.classic_address,
            amount=str(amount),
            destination=destination
        )
        
        signed_tx = self.wallet.sign(payment)
        return signed_tx

    def sign_transaction(self, transaction):
        if not self.wallet:
            raise ValueError("Wallet not loaded")
        return self.wallet.sign(transaction)

    def get_address(self):
        if not self.wallet:
            raise ValueError("Wallet not created or loaded")
        return self.wallet.classic_address

    def check_balance(self):
        if not self.wallet:
            raise ValueError("Wallet not created or loaded")
        return xrpl.account.get_balance(self.wallet.classic_address, self.client)

    def collect_fees(self, amount):
        # Placeholder for fee collection
        print(f"Collected fees: {amount}")
        # Implement actual fee collection logic here when needed
        pass
