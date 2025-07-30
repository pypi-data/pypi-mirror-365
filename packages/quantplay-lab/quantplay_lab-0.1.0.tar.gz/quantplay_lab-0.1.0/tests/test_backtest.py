"""Basic tests for quantlab backtesting engine"""

import pytest
import polars as pl
from datetime import datetime, time

from quantlab import Strategy, Backtest
from quantlab.utils.types import StrategyType
from quantlab.utils.exceptions import ValidationError


class MockStrategy(Strategy):
    """Mock strategy for testing"""
    
    def __init__(self):
        super().__init__()
        self.name = "test_strategy"
        self.type = "INTRADAY"
        self.exchange = "NSE"
        self.product = "MIS"
        
    def generate_signals(self, data):
        """Generate mock signals"""
        return pl.DataFrame({
            "tradingsymbol": ["RELIANCE", "TCS"],
            "entry_time": [
                datetime(2023, 1, 1, 9, 30),
                datetime(2023, 1, 1, 10, 0)
            ],
            "exit_time": [
                datetime(2023, 1, 1, 15, 0),
                datetime(2023, 1, 1, 15, 0)
            ],
            "transaction_type": ["BUY", "SELL"],
            "quantity": [100, 50],
            "stoploss": [0.02, 0.02]
        })


def test_strategy_initialization():
    """Test strategy initialization"""
    strategy = MockStrategy()
    
    assert strategy.name == "test_strategy"
    assert strategy.type == "INTRADAY"
    assert strategy.exchange == "NSE"
    assert strategy.product == "MIS"
    assert strategy.interval == 1


def test_backtest_initialization():
    """Test backtest engine initialization"""
    backtest = Backtest(strategy_type="INTRADAY")
    
    assert backtest.strategy_type == "INTRADAY"
    assert backtest.evaluator.backtest_mode == "INTRADAY"


def test_data_aggregation():
    """Test data aggregation functionality"""
    strategy = MockStrategy()
    strategy.interval = 5
    
    # Create sample minute data
    dates = pl.datetime_range(
        datetime(2023, 1, 1, 9, 15),
        datetime(2023, 1, 1, 10, 0),
        interval="1m"
    )
    
    data = pl.DataFrame({
        "date": dates,
        "symbol": ["RELIANCE"] * len(dates),
        "open": [100.0] * len(dates),
        "high": [101.0] * len(dates),
        "low": [99.0] * len(dates),
        "close": [100.5] * len(dates),
        "volume": [1000] * len(dates)
    })
    
    # Aggregate to 5-minute
    aggregated = strategy.aggregate_data(data)
    
    # Check aggregation worked
    assert len(aggregated) < len(data)
    assert aggregated["volume"].sum() == data["volume"].sum()


def test_trade_validation():
    """Test trade validation"""
    from quantlab.core.validator import TradeValidator
    
    # Valid trades
    valid_trades = pl.DataFrame({
        "tradingsymbol": ["RELIANCE"],
        "entry_time": [datetime(2023, 1, 1, 9, 30)],
        "exit_time": [datetime(2023, 1, 1, 15, 0)],
        "tag": ["test"],
        "transaction_type": ["BUY"],
        "strategy_type": ["INTRADAY"]
    })
    
    # Should not raise
    TradeValidator.validate_trades(valid_trades)
    
    # Empty trades
    empty_trades = pl.DataFrame()
    
    with pytest.raises(ValidationError, match="No trades found"):
        TradeValidator.validate_trades(empty_trades)
    
    # Invalid transaction type
    invalid_trades = valid_trades.with_columns(
        pl.lit("INVALID").alias("transaction_type")
    )
    
    with pytest.raises(ValidationError, match="Invalid transaction types"):
        TradeValidator.validate_trades(invalid_trades)


def test_charges_calculation():
    """Test Indian market charges calculation"""
    from quantlab.market.india import Charges
    
    # Test intraday charges
    charges = Charges.get_charges(
        quantity=100,
        transaction_type="BUY",
        segment="INTRADAY",
        exchange="NSE",
        entry_price=100,
        exit_price=105
    )
    
    assert charges > 0
    assert isinstance(charges, float)
    
    # Test delivery charges
    delivery_charges = Charges.get_charges(
        quantity=100,
        transaction_type="BUY",
        segment="DELIVERY",
        exchange="NSE",
        entry_price=100,
        exit_price=105
    )
    
    assert delivery_charges > charges  # Delivery has higher charges


if __name__ == "__main__":
    pytest.main([__file__])