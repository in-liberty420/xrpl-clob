from multisig import MultisigWallet

def main():
    wallet = MultisigWallet()
    address = wallet.create_wallet()
    print(f"Multisig wallet created with address: {address}")
    print("Encrypted keys have been stored in 'encrypted_wallet.key'")

if __name__ == "__main__":
    main()
