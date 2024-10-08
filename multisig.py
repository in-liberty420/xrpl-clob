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
        self.key = None

    def create_wallet(self):
        self.wallet = Wallet.create()
        self.encrypt_and_store_keys()
        return self.wallet.classic_address

    def encrypt_and_store_keys(self):
        if not self.wallet:
            raise ValueError("Wallet not created yet")
        
        self.key = Fernet.generate_key()
        f = Fernet(self.key)
        encrypted_seed = f.encrypt(self.wallet.seed.encode())
        
        with open("encrypted_wallet.key", "wb") as file:
            file.write(encrypted_seed)

    def load_wallet(self):
        if not os.path.exists("encrypted_wallet.key"):
            raise FileNotFoundError("Encrypted wallet file not found")
        
        with open("encrypted_wallet.key", "rb") as file:
            encrypted_seed = file.read()
        
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
