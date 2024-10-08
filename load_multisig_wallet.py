from multisig import MultisigWallet

def main():
    wallet = MultisigWallet()
    wallet.load_wallet()
    address = wallet.get_address()
    print(f"Loaded multisig wallet with address: {address}")
    return wallet

if __name__ == "__main__":
    main()
