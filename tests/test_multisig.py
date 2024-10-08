import unittest
from unittest.mock import patch, MagicMock
import os
from cryptography.fernet import Fernet
from multisig import MultisigWallet
from xrpl.wallet import Wallet

class TestMultisigWallet(unittest.TestCase):
    def setUp(self):
        self.wallet = MultisigWallet()

    def test_create_wallet(self):
        with patch('multisig.Wallet.create') as mock_create:
            mock_wallet = MagicMock()
            mock_wallet.classic_address = 'rTestAddress123'
            mock_create.return_value = mock_wallet

            with patch.object(self.wallet, 'encrypt_and_store_keys') as mock_encrypt:
                address = self.wallet.create_wallet()

                mock_create.assert_called_once()
                mock_encrypt.assert_called_once()
                self.assertEqual(address, 'rTestAddress123')

    def test_encrypt_and_store_keys(self):
        self.wallet.wallet = Wallet.create()
        
        with patch('builtins.open', unittest.mock.mock_open()) as mock_file:
            self.wallet.encrypt_and_store_keys()

            mock_file.assert_called_once_with("encrypted_wallet.key", "wb")
            mock_file().write.assert_called_once()

    def test_load_wallet(self):
        mock_encrypted_seed = b'gAAAAABexampleencrypteddata'
        mock_decrypted_seed = 'sDecryptedSeed123'

        with patch('builtins.open', unittest.mock.mock_open(read_data=mock_encrypted_seed)):
            with patch('cryptography.fernet.Fernet.decrypt') as mock_decrypt:
                mock_decrypt.return_value = mock_decrypted_seed.encode()

                with patch('xrpl.wallet.Wallet.from_seed') as mock_from_seed:
                    mock_wallet = MagicMock()
                    mock_from_seed.return_value = mock_wallet

                    self.wallet.key = Fernet.generate_key()
                    self.wallet.load_wallet()

                    mock_from_seed.assert_called_once_with(mock_decrypted_seed)
                    self.assertEqual(self.wallet.wallet, mock_wallet)

    def test_create_and_sign_transaction(self):
        self.wallet.wallet = MagicMock()
        self.wallet.wallet.sign = MagicMock(return_value="signed_transaction")

        signed_tx = self.wallet.create_and_sign_transaction('rDestination123', 100)

        self.wallet.wallet.sign.assert_called_once()
        self.assertEqual(signed_tx, "signed_transaction")

    def test_get_address(self):
        self.wallet.wallet = MagicMock()
        self.wallet.wallet.classic_address = 'rTestAddress123'

        address = self.wallet.get_address()
        self.assertEqual(address, 'rTestAddress123')

    def test_check_balance(self):
        self.wallet.wallet = MagicMock()
        self.wallet.client = MagicMock()

        with patch('xrpl.account.get_balance') as mock_get_balance:
            mock_get_balance.return_value = '1000'

            balance = self.wallet.check_balance()
            self.assertEqual(balance, '1000')

    def test_collect_fees(self):
        with patch('builtins.print') as mock_print:
            self.wallet.collect_fees(100)
            mock_print.assert_called_once_with('Collected fees: 100')

if __name__ == '__main__':
    unittest.main()
