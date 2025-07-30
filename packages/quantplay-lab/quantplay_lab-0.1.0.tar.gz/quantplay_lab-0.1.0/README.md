# Quantlab

[![Python](https://img.shields.io/pypi/pyversions/quantlab.svg)](https://pypi.org/project/quantlab/)
[![PyPI](https://img.shields.io/pypi/v/quantlab.svg)](https://pypi.org/project/quantlab/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

High-performance backtesting engine for algorithmic trading with focus on Indian markets (NSE, BSE, NFO, BFO).

## Features

- 🚀 **High Performance**: Built on Polars for lightning-fast data processing
- 🇮🇳 **Indian Markets**: Native support for NSE, BSE equities and derivatives
- 📊 **Comprehensive Metrics**: Detailed performance analytics including drawdown, win rate, and BPS
- 💰 **Accurate Charges**: Built-in Indian market charges calculation (STT, brokerage, etc.)
- 🎯 **Multiple Strategy Types**: Support for INTRADAY, OVERNIGHT, SWING strategies
- 📈 **Beautiful Reports**: Rich console output with detailed statistics

## Installation

```bash
pip install quantlab
```

## Quick Start

```python
from quantlab import Strategy, Backtest
import polars as pl

class SimpleMovingAverage(Strategy):
    def __init__(self):
        super().__init__()
        self.name = "sma_crossover"
        self.type = "INTRADAY"
        self.exchange = "NSE"
        self.product = "MIS"
        self.instrument_universe = {
            "NSE_EQ": {"is_liquid": True}
        }
        
    def generate_signals(self, data):
        # Your strategy logic here
        equity_data = data["NSE:EQ"]
        
        # Example: Simple moving average crossover
        signals = equity_data.with_columns([
            pl.col("close").rolling_mean(window_size=20).alias("sma20"),
            pl.col("close").rolling_mean(window_size=50).alias("sma50")
        ])
        
        # Generate buy signals when SMA20 crosses above SMA50
        trades = signals.filter(
            (pl.col("sma20") > pl.col("sma50")) &
            (pl.col("sma20").shift(1) <= pl.col("sma50").shift(1))
        )
        
        # Format output for backtesting
        return trades.select([
            pl.col("symbol").alias("tradingsymbol"),
            pl.col("date").alias("entry_time"),
            # Add exit time, quantity, etc.
        ])

# Run backtest
strategy = SimpleMovingAverage()
results = strategy.run_backtest(data_range=(2020, 2023))
```

## Architecture

```
quantlab/
├── core/           # Backtesting engine
├── data/           # Data loading utilities
├── strategy/       # Strategy framework
├── analysis/       # Performance metrics
├── reporting/      # Results visualization
└── market/         # Market-specific logic (charges, etc.)
```

## Strategy Development

### Basic Strategy Structure

```python
from quantlab import Strategy
import polars as pl

class MyStrategy(Strategy):
    def __init__(self):
        super().__init__()
        self.name = "my_strategy"
        self.type = "INTRADAY"  # or "OVERNIGHT", "SWING"
        self.exchange = "NSE"
        self.product = "MIS"    # or "CNC", "NRML"
        self.STRATEGY_EXIT_TIME = time(15, 15)
        self.interval = 5       # 5-minute candles
        
        # Define universe
        self.instrument_universe = {
            "NSE_EQ": {"is_liquid": True},
            "NSE_INDICES": {"underlying": ["NIFTY 50"]}
        }
    
    def generate_signals(self, data):
        """
        Generate trading signals
        
        Returns DataFrame with columns:
        - tradingsymbol: Symbol to trade
        - entry_time: Entry timestamp
        - exit_time: Exit timestamp  
        - transaction_type: "BUY" or "SELL"
        - quantity: Number of shares
        - stoploss: Optional SL percentage
        """
        # Your strategy logic here
        pass
```

### Data Access

The `data` parameter in `generate_signals` is a dictionary with market data:

```python
{
    "NSE:EQ": pl.DataFrame,      # Equity data
    "NSE:INDICES": pl.DataFrame,  # Index data
    "NFO:FUT": pl.DataFrame,      # Futures data
    "NFO:OPT": pl.DataFrame,      # Options data
}
```

Each DataFrame contains columns: `date`, `open`, `high`, `low`, `close`, `volume`, `oi` (for F&O).

## Performance Metrics

Quantlab provides comprehensive metrics:

- **PnL Analysis**: Total, monthly average, yearly breakdown
- **Risk Metrics**: Maximum drawdown, risk/reward ratio
- **Trade Statistics**: Win rate, number of trades, BPS
- **Time Analysis**: Hourly and time-based performance
- **Trade Details**: Top winning and losing trades

## Indian Market Support

### Charges Calculation

Built-in support for Indian market charges:
- Securities Transaction Tax (STT)
- Exchange transaction charges
- SEBI charges
- Stamp duty
- GST

### Supported Segments

- **Equity**: NSE, BSE cash markets
- **Derivatives**: NFO, BFO futures and options
- **Indices**: NIFTY, SENSEX and sectoral indices

## Advanced Features

### Custom Data Loading

```python
from quantlab.data import BacktestDataLoader

loader = BacktestDataLoader(data_path="./market_data")
data = loader.load_data({
    "NSE_EQ": {"is_liquid": True},
    "NFO_OPT": {"underlying": ["NIFTY"]}
})
```

### Multi-timeframe Strategies

```python
class MultiTimeframe(Strategy):
    def __init__(self):
        super().__init__()
        self.interval = 15  # 15-minute primary timeframe
    
    def generate_signals(self, data):
        # Access different timeframes
        data_5min = self.aggregate_data(data["NSE:EQ"], interval=5)
        data_15min = self.aggregate_data(data["NSE:EQ"], interval=15)
        # Strategy logic using multiple timeframes
```

## Requirements

- Python >= 3.10
- polars >= 1.24.0
- See `requirements.txt` for full list

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This software is for educational purposes only. Do not use this for actual trading without understanding the risks involved. Past performance is not indicative of future results.