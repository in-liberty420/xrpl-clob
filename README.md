# XRP Ledger Decentralized Exchange (DEX)

## Overview
This project implements a decentralized exchange (DEX) on the XRP Ledger Testnet. It features a central limit order book (CLOB) with batch auctions, multisignature wallets for enhanced security, and a RESTful API for order placement and management.

## Features
- Central Limit Order Book (CLOB)
- Batch auction matching engine
- Multisignature wallet integration
- RESTful API for order placement and management
- Real-time order book updates
- Automatic settlement on the XRP Ledger Testnet

## Technology Stack
- Python 3.x
- Flask (Web Framework)
- xrpl-py (XRP Ledger Python Library)
- Poetry (Dependency Management)

## Setup and Installation
1. Clone the repository:
   ```
   git clone https://github.com/yourusername/xrpl-dex.git
   cd xrpl-dex
   ```

2. Install dependencies using Poetry:
   ```
   poetry install
   ```

3. Activate the virtual environment:
   ```
   poetry shell
   ```

4. Set up the multisignature wallet:
   ```
   python create_multisig_wallet.py
   ```

5. Start the application:
   ```
   python main.py
   ```

## API Endpoints
- `POST /place_order`: Place a new order
- `GET /l2_order_book`: Retrieve the current L2 order book

For detailed API documentation, please refer to the [API Documentation](docs/API.md) file.

## Interacting with the XRPL Testnet
This DEX interacts with the XRP Ledger Testnet in the following ways:
1. Creating and managing multisignature wallets
2. Submitting and verifying transactions
3. Monitoring account balances and order status
4. Settling matched orders on the ledger

For more details on XRPL integration, see the [XRPL Integration Guide](docs/XRPL_Integration.md).

## Architecture

Our DEX consists of the following main components:
1. Order Book
2. Matching Engine
3. Settlement System
4. API Layer
5. XRPL Integration

For a detailed explanation of each component, please refer to the [Architecture Overview](docs/Architecture.md).

## Security Considerations
- Multisignature wallets for enhanced fund security
- Transaction signature verification
- Rate limiting and DDoS protection (TODO)

## Performance Optimizations
- Batch auction mechanism for efficient order matching
- Optimized data structures for fast order book updates

## Testing
To run the test suite:
```
pytest tests/
```

For more information on our testing strategy, see the [Testing Guide](docs/Testing.md).

## Contributing
We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for more information on how to get started.

## Future Improvements
- Implement WebSocket support for real-time updates
- Add support for limit orders with "Good Till Cancelled" option
- Implement a more sophisticated fee structure
- Enhance monitoring and alerting capabilities

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements
- XRP Ledger Foundation for their excellent documentation and support
- The open-source community for various libraries and tools used in this project
