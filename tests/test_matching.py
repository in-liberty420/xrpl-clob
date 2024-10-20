import pytest
import time
from unittest.mock import Mock
from matching_engine import MatchingEngine
from order_book import OrderBook, Order
from xrpl_integration import XRPLIntegration
from multisig import MultisigWallet

@pytest.fixture
def order_book():
    return OrderBook()

@pytest.fixture
def mock_xrpl_integration():
    mock = Mock(spec=XRPLIntegration)
    mock.get_account_sequence.return_value = 1  # Default sequence number
    mock.submit_transaction.return_value.is_successful.return_value = True
    mock.submit_transaction.return_value.result = {'hash': 'mock_hash'}
    return mock

@pytest.fixture
def mock_multisig_wallet():
    return Mock(spec=MultisigWallet)

@pytest.fixture
def matching_engine(order_book, mock_xrpl_integration, mock_multisig_wallet):
    return MatchingEngine(order_book, mock_xrpl_integration, mock_multisig_wallet, batch_interval=1)  # Use a shorter interval for testing

def create_order(price, amount, order_type, order_id=None, sequence=None):
    return Order(price, amount, order_type, f"address_{order_id}", f"pubkey_{order_id}", f"sig_{order_id}", int(time.time()) + 300, sequence=sequence)

class TestMatchingEngine:

    def test_initialization(self, matching_engine):
        assert matching_engine.batch_interval == 1
        assert isinstance(matching_engine.order_book, OrderBook)

    def test_find_clearing_price(self, matching_engine):
        # Test with no matching orders
        matching_engine.order_book.add_order(create_order(98, 10, "buy", "1", sequence=1))
        matching_engine.order_book.add_order(create_order(102, 10, "sell", "2", sequence=2))
        matching_engine.match_orders()
        assert matching_engine.last_clearing_price is None

        # Test with matching orders
        matching_engine.order_book.add_order(create_order(100, 10, "buy", "3", sequence=3))
        matching_engine.order_book.add_order(create_order(100, 10, "sell", "4", sequence=4))
        matching_engine.match_orders()
        assert matching_engine.last_clearing_price == 100

        # Test again with no matching orders
        matching_engine.order_book.add_order(create_order(98, 10, "buy", "5", sequence=5))
        matching_engine.order_book.add_order(create_order(102, 10, "sell", "6", sequence=6))
        matching_engine.match_orders()
        assert matching_engine.last_clearing_price == 100  # Should still be 100 from the last match

    def test_pro_rata_matching(self, matching_engine):
        matching_engine.order_book.add_order(create_order(100, 6, "buy", "1", sequence=1))
        matching_engine.order_book.add_order(create_order(100, 4, "buy", "2", sequence=2))
        matching_engine.order_book.add_order(create_order(100, 15, "sell", "3", sequence=3))

        matching_engine.match_orders()

        # Check that buy orders were fully filled and removed
        assert 100 not in matching_engine.order_book.bids
        
        # Check that sell order was partially filled
        assert len(matching_engine.order_book.asks[100]) == 1
        assert matching_engine.order_book.asks[100][0].amount == 5  # 15 - (6 + 4)

        # Verify the clearing price
        assert matching_engine.last_clearing_price == 100

    def test_partial_fill(self, matching_engine):
        matching_engine.order_book.add_order(create_order(100, 10, "buy", "1", sequence=1))
        matching_engine.order_book.add_order(create_order(100, 7, "sell", "2", sequence=2))

        matching_engine.match_orders()

        assert len(matching_engine.order_book.bids[100]) == 1
        assert matching_engine.order_book.bids[100][0].amount == 3
        assert 100 not in matching_engine.order_book.asks

    def test_multiple_price_levels(self, matching_engine):
        matching_engine.order_book.add_order(create_order(101, 5, "buy", "1", sequence=1))
        matching_engine.order_book.add_order(create_order(100, 5, "buy", "2", sequence=2))
        matching_engine.order_book.add_order(create_order(99, 10, "sell", "3", sequence=3))
    
        matching_engine.match_orders()
    
        assert 100 not in matching_engine.order_book.bids
        assert 101 not in matching_engine.order_book.bids
        assert 99 not in matching_engine.order_book.asks
        assert len(matching_engine.order_book.bids) == 0
        assert len(matching_engine.order_book.asks) == 0

    def test_no_match(self, matching_engine):
        matching_engine.order_book.add_order(create_order(98, 10, "buy", "1", sequence=1))
        matching_engine.order_book.add_order(create_order(102, 10, "sell", "2", sequence=2))

        matching_engine.match_orders()

        assert len(matching_engine.order_book.bids[98]) == 1
        assert len(matching_engine.order_book.asks[102]) == 1

    def test_exact_match(self, matching_engine):
        matching_engine.order_book.add_order(create_order(100, 10, "buy", "1", sequence=1))
        matching_engine.order_book.add_order(create_order(100, 10, "sell", "2", sequence=2))

        matching_engine.match_orders()

        assert 100 not in matching_engine.order_book.bids
        assert 100 not in matching_engine.order_book.asks

    def test_order_expiration(self, matching_engine):
        current_time = int(time.time())
        expired_order = create_order(100, 10, "buy", "1", sequence=1)
        expired_order.expiration = current_time - 1
        matching_engine.order_book.add_order(expired_order)
        matching_engine.order_book.add_order(create_order(100, 10, "sell", "2", sequence=2))

        matching_engine.match_orders()

        assert 100 not in matching_engine.order_book.bids
        assert len(matching_engine.order_book.asks[100]) == 1

    def test_large_order_book(self, matching_engine):
        for i in range(1000):
            matching_engine.order_book.add_order(create_order(100 + i * 0.01, 1, "buy", f"buy_{i}", sequence=i+1))
            matching_engine.order_book.add_order(create_order(110 - i * 0.01, 1, "sell", f"sell_{i}", sequence=i+1001))

        matching_engine.match_orders()

        total_orders = sum(len(orders) for orders in matching_engine.order_book.bids.values()) + \
                       sum(len(orders) for orders in matching_engine.order_book.asks.values())
        assert total_orders < 2000

    def test_batch_auction_timing(self, matching_engine):
        start_time = time.time()
        matching_engine.run_batch_auction()
        matching_engine.run_batch_auction()  # This should not run immediately
        assert time.time() - start_time < 2 * matching_engine.batch_interval
