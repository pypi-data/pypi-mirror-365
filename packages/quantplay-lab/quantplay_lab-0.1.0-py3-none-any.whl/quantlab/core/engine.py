"""Main backtesting engine"""

from datetime import date
from typing import Dict

import polars as pl

from quantlab.core.evaluator import Evaluator
from quantlab.core.validator import TradeValidator
from quantlab.utils.types import StrategyType
from quantlab.utils.exceptions import BacktestError


class Backtest:
    """Main backtesting engine for running strategy simulations"""
    
    def __init__(
        self,
        strategy_type: StrategyType = "INTRADAY",
        data_path: str | None = None,
    ):
        """
        Initialize backtest engine
        
        Args:
            strategy_type: Type of strategy (INTRADAY, OVERNIGHT, SWING)
            data_path: Path to market data
        """
        self.strategy_type = strategy_type
        self.data_path = data_path
        self.evaluator = Evaluator(strategy_type)
        
    def run(
        self,
        strategy,
        start_date: str | date | None = None,
        end_date: str | date | None = None,
        save_results: bool = False,
    ) -> pl.DataFrame:
        """
        Run backtest for a strategy
        
        Args:
            strategy: Strategy instance with generate_signals method
            start_date: Start date for backtest
            end_date: End date for backtest
            save_results: Whether to save results
            
        Returns:
            DataFrame with backtest results
        """
        try:
            # Set default date range
            if start_date is None:
                start_date = date(2018, 1, 1)
            elif isinstance(start_date, str):
                start_date = date.fromisoformat(start_date)
                
            if end_date is None:
                end_date = date.today()
            elif isinstance(end_date, str):
                end_date = date.fromisoformat(end_date)
            
            # Load data through strategy's data loader
            market_data = strategy.load_data(start_date, end_date)
            
            # Generate signals
            signals = strategy.generate_signals(market_data)
            
            if signals.is_empty():
                return pl.DataFrame()
            
            # Add metadata
            signals = signals.with_columns(
                pl.lit(strategy.name).alias("tag"),
                pl.lit(self.strategy_type).alias("strategy_type"),
                pl.lit(strategy.product).alias("product"),
                pl.lit(strategy.exchange).alias("exchange"),
            )
            
            # Validate trades
            TradeValidator.validate_trades(signals)
            
            # Prepare market data for evaluation
            all_market_data = pl.concat(list(market_data.values())).sort("date")
            all_market_data = all_market_data.filter(
                pl.col("symbol").is_in(signals["tradingsymbol"].unique().to_list())
            )
            
            # Aggregate data if needed
            if hasattr(strategy, 'interval') and strategy.interval > 1:
                all_market_data = strategy.aggregate_data(all_market_data)
            
            # Evaluate performance
            results = self.evaluator.evaluate_performance(signals, all_market_data)
            
            # Add backtest metadata
            results = results.with_columns(
                pl.lit(0, pl.Float64()).alias("slippage"),
                pl.lit("BACKTEST").alias("mode"),
            )
            
            return results
            
        except Exception as e:
            raise BacktestError(f"Backtest failed: {e}") from e