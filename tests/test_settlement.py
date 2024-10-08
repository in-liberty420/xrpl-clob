import pytest
from unittest.mock import Mock, patch
from settlement import Settlement
from order_book import Order
from xrpl.transaction import XRPLReliableSubmissionException

@pytest.fixture
def mock_xrpl_integration():
    mock = Mock()
    mock.submit_transaction.return_value.is_successful.return_value = True
    mock.submit_transaction.return_value.result = {'hash': 'mock_hash'}
    return mock

@pytest.fixture
def mock_multisig_wallet():
    wallet = Mock()
    wallet.get_address.return_value = "rMultisigWalletAddress"
    return wallet

@pytest.fixture
def settlement(mock_xrpl_integration, mock_multisig_wallet):
    return Settlement(mock_xrpl_integration, mock_multisig_wallet)

def create_mock_order(order_type, price, amount, address="rUserAddress"):
    order = Mock(spec=Order)
    order.order_type = order_type
    order.price = price
    order.amount = amount
    order.xrp_address = address
    order.payment_tx_signature = "mock_payment_signature"
    return order

def test_process_matched_orders_success(settlement):
    buy_order = create_mock_order("buy", 100, 10)
    sell_order = create_mock_order("sell", 100, 10)
    
    with patch.object(Settlement, 'execute_order', return_value=True) as mock_execute:
        result = settlement.process_matched_orders([buy_order, sell_order])
    
    assert result == True
    assert mock_execute.call_count == 2

def test_process_matched_orders_failure(settlement):
    buy_order = create_mock_order("buy", 100, 10)
    sell_order = create_mock_order("sell", 100, 10)
    
    with patch.object(Settlement, 'execute_order', side_effect=[True, False]) as mock_execute:
        result = settlement.process_matched_orders([buy_order, sell_order])
    
    assert result == False
    assert mock_execute.call_count == 2

def test_execute_order_buy(settlement, mock_xrpl_integration, mock_multisig_wallet):
    buy_order = create_mock_order("buy", 100, 10)
    mock_xrpl_integration.create_payment_transaction.return_value = "mock_payout_tx"
    
    with patch.object(Settlement, 'submit_transaction', side_effect=[True, True]) as mock_submit:
        result = settlement.execute_order(buy_order)
    
    assert result == True
    mock_submit.assert_any_call(buy_order.payment_tx_signature, "Full payment for buy order")
    mock_submit.assert_any_call("mock_payout_tx", "Payout for buy order")
    mock_xrpl_integration.create_payment_transaction.assert_called_once_with(
        mock_multisig_wallet.get_address(), buy_order.xrp_address, 10
    )

def test_execute_order_sell(settlement, mock_xrpl_integration, mock_multisig_wallet):
    sell_order = create_mock_order("sell", 100, 10)
    mock_xrpl_integration.create_payment_transaction.return_value = "mock_payout_tx"
    
    with patch.object(Settlement, 'submit_transaction', side_effect=[True, True]) as mock_submit:
        result = settlement.execute_order(sell_order)
    
    assert result == True
    mock_submit.assert_any_call(sell_order.payment_tx_signature, "Full payment for sell order")
    mock_submit.assert_any_call("mock_payout_tx", "Payout for sell order")
    mock_xrpl_integration.create_payment_transaction.assert_called_once_with(
        mock_multisig_wallet.get_address(), sell_order.xrp_address, 1000  # 10 * 100
    )

def test_submit_transaction_success(settlement, mock_xrpl_integration):
    mock_xrpl_integration.submit_transaction.return_value.is_successful.return_value = True
    mock_xrpl_integration.submit_transaction.return_value.result = {'hash': 'mock_hash'}
    
    result = settlement.submit_transaction("mock_tx", "Test transaction")
    
    assert result == True
    mock_xrpl_integration.submit_transaction.assert_called_once_with("mock_tx")

def test_submit_transaction_failure(settlement, mock_xrpl_integration):
    mock_xrpl_integration.submit_transaction.return_value.is_successful.return_value = False
    mock_xrpl_integration.submit_transaction.return_value.result = {'error': 'mock_error'}
    
    result = settlement.submit_transaction("mock_tx", "Test transaction")
    
    assert result == False
    mock_xrpl_integration.submit_transaction.assert_called_once_with("mock_tx")

def test_submit_transaction_exception(settlement, mock_xrpl_integration):
    mock_xrpl_integration.submit_transaction.side_effect = XRPLReliableSubmissionException("Test exception")
    
    result = settlement.submit_transaction("mock_tx", "Test transaction")
    
    assert result == False
    mock_xrpl_integration.submit_transaction.assert_called_once_with("mock_tx")
