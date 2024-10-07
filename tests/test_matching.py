import pytest
from matching_engine import MatchingEngine
from order_book import OrderBook, Order
import time

@pytest.fixture
def order_book():
    return OrderBook()

@pytest.fixture
def matching_engine(order_book):
    return MatchingEngine(order_book, batch_interval=1)  # Use a shorter interval for testing

def create_order(price, amount, order_type):
    return Order(price, amount, order_type, "dummy_address", "dummy_public_key", "dummy_signature")

class TestMatchingEngine:

    def test_initialization(self, matching_engine):
        assert matching_engine.batch_interval == 1
        assert isinstance(matching_engine.order_book, OrderBook)

    def test_run_batch_auction_timing(self, matching_engine):
        start_time = time.time()
        matching_engine.run_batch_auction()
        assert time.time() - start_time < matching_engine.batch_interval

    def test_simple_match(self, matching_engine, order_book):
        order_book.add_order(create_order(100, 10, "buy"))
        order_book.add_order(create_order(100, 10, "sell"))
        matching_engine.match_orders()
        assert len(order_book.bids) == 0
        assert len(order_book.asks) == 0

    def test_partial_match(self, matching_engine, order_book):
        order_book.add_order(create_order(100, 15, "buy"))
        order_book.add_order(create_order(100, 10, "sell"))
        matching_engine.match_orders()
        assert len(order_book.bids) == 1
        assert order_book.bids[0].amount == 5
        assert len(order_book.asks) == 0

    def test_no_match(self, matching_engine, order_book):
        order_book.add_order(create_order(90, 10, "buy"))
        order_book.add_order(create_order(110, 10, "sell"))
        matching_engine.match_orders()
        assert len(order_book.bids) == 1
        assert len(order_book.asks) == 1

    def test_multiple_matches(self, matching_engine, order_book):
        order_book.add_order(create_order(100, 10, "buy"))
        order_book.add_order(create_order(101, 5, "buy"))
        order_book.add_order(create_order(99, 7, "sell"))
        order_book.add_order(create_order(100, 8, "sell"))
        matching_engine.match_orders()
        assert len(order_book.bids) == 0
        assert len(order_book.asks) == 1
        assert order_book.asks[0].amount == 0

    def test_clearing_price_determination(self, matching_engine, order_book):
        order_book.add_order(create_order(102, 5, "buy"))
        order_book.add_order(create_order(101, 3, "buy"))
        order_book.add_order(create_order(100, 2, "buy"))
        order_book.add_order(create_order(99, 4, "sell"))
        order_book.add_order(create_order(100, 3, "sell"))
        order_book.add_order(create_order(101, 3, "sell"))
        matching_engine.match_orders()
        # The clearing price should be 101
        assert len(order_book.bids) == 1
        assert order_book.bids[0].price == 100
        assert len(order_book.asks) == 1
        assert order_book.asks[0].price == 101

    def test_expired_order_removal(self, matching_engine, order_book):
        expired_order = create_order(100, 10, "buy")
        expired_order.expiration = time.time() - 1  # Set expiration to 1 second ago
        order_book.add_order(expired_order)
        order_book.add_order(create_order(100, 10, "sell"))
        matching_engine.match_orders()
        assert len(order_book.bids) == 0
        assert len(order_book.asks) == 1

    def test_batch_auction_interval(self, matching_engine):
        start_time = time.time()
        matching_engine.run_batch_auction()
        matching_engine.run_batch_auction()  # This should not run immediately
        assert time.time() - start_time < 2 * matching_engine.batch_interval

    def test_large_order_book(self, matching_engine, order_book):
        for i in range(1000):
            order_book.add_order(create_order(100 + i * 0.01, 1, "buy"))
            order_book.add_order(create_order(110 - i * 0.01, 1, "sell"))
        matching_engine.match_orders()
        assert len(order_book.bids) + len(order_book.asks) < 2000

    def test_edge_case_same_price(self, matching_engine, order_book):
        order_book.add_order(create_order(100, 10, "buy"))
        order_book.add_order(create_order(100, 10, "buy"))
        order_book.add_order(create_order(100, 15, "sell"))
        matching_engine.match_orders()
        assert len(order_book.bids) == 0
        assert len(order_book.asks) == 1
        assert order_book.asks[0].amount == 5
