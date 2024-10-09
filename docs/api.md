# API Documentation

## Endpoints

### 1. Place Order
- **URL:** `/place_order`
- **Method:** POST
- **Description:** Place a new order in the order book.
- **Request Body:**
  ```json
  {
    "price": float,
    "amount_drops": int,
    "order_type": "buy" | "sell",
    "xrp_address": string,
    "public_key": string,
    "expiration": int,
    "sequence": int,
    "payment_tx_signature": string,
    "multisig_destination": string,
    "last_ledger_sequence": int,
    "signed_tx_json": object
  }
  ```
- **Response:**
  - Success: `{"status": "success", "message": "Order placed and processed"}`
  - Error: `{"status": "error", "message": "Error description"}`

### 2. Get L2 Order Book
- **URL:** `/l2_order_book`
- **Method:** GET
- **Description:** Retrieve the current L2 order book.
- **Response:** JSON object containing bids and asks.

## Error Handling
- All errors return a JSON object with `status` and `message` fields.
- HTTP status codes are used appropriately (e.g., 400 for bad requests).

## Rate Limiting
- [Describe any rate limiting implemented on the API]

## Authentication
- [Describe any authentication methods required to use the API]
