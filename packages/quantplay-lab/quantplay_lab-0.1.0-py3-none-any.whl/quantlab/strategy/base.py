"""Base strategy class for backtesting"""

import logging
from abc import ABC, abstractmethod
from datetime import date, time, timedelta
from typing import Dict, List

import polars as pl

from quantlab.core.engine import Backtest
from quantlab.data.loader import BacktestDataLoader
from quantlab.analysis.metrics import Reporting
from quantlab.utils.types import (
    StrategyType, ExchangeType, ProductType, SymbolConfig
)

logging.basicConfig(level=logging.INFO)


class Strategy(ABC):
    """Abstract base class for trading strategies"""
    
    def __init__(self) -> None:
        """Initialize strategy with default parameters"""
        self.type: StrategyType = "INTRADAY"
        self.name: str = "unnamed_strategy"
        self.tag: str = ""
        
        self.STRATEGY_EXIT_TIME: time = time(15, 15)
        self.product: ProductType = "MIS"
        self.exchange: ExchangeType = "NSE"
        self.instrument_universe: SymbolConfig = {}
        
        self.interval: int = 1  # Minutes
        self.slippage: float = 0
        
        self.required_columns: List[str] = []
        self.backtest_data: Dict[str, pl.DataFrame] = {}
        
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def aggregate_data(self, data: pl.DataFrame) -> pl.DataFrame:
        """
        Aggregate minute data to specified interval
        
        Args:
            data: Minute-level market data
            
        Returns:
            Aggregated data at specified interval
        """
        if self.interval == 1:
            return data
        
        cols = [
            pl.col("open").first(),
            pl.col("high").max(),
            pl.col("low").min(),
            pl.col("close").last(),
            pl.col("volume").sum(),
        ]
        
        if "oi" in data.columns:
            cols.append(pl.col("oi").last())
        
        data = data.sort(["symbol", "date"])
        
        data = data.group_by_dynamic(
            index_column="date",
            every=timedelta(minutes=self.interval),
            closed="left",
            label="left",
            include_boundaries=False,
            group_by="symbol",
            start_by="window",
        ).agg(cols)
        
        return data
    
    def load_data(
        self, 
        start_date: date,
        end_date: date,
        data_path: str = "./data"
    ) -> Dict[str, pl.DataFrame]:
        """
        Load market data for backtesting
        
        Args:
            start_date: Start date for data
            end_date: End date for data
            data_path: Path to market data
            
        Returns:
            Dictionary of DataFrames by exchange:segment
        """
        loader = BacktestDataLoader(
            data_path=data_path,
            data_range=(start_date.year, end_date.year)
        )
        
        self.backtest_data = loader.load_data(self.instrument_universe)
        return self.backtest_data
    
    def run_backtest(
        self,
        save_results: bool = False,
        data_range: tuple[int, int] | None = None,
        data_path: str = "./data",
    ) -> pl.DataFrame:
        """
        Run backtest for this strategy
        
        Args:
            save_results: Whether to save results
            data_range: Year range for backtest
            data_path: Path to market data
            
        Returns:
            DataFrame with backtest results
        """
        if self.type == "BUYANDHOLD":
            return pl.DataFrame()
        
        if data_range is None:
            data_range = (2018, date.today().year)
        
        # Create backtest engine
        backtest = Backtest(
            strategy_type=self.type,
            data_path=data_path
        )
        
        # Run backtest
        results = backtest.run(
            strategy=self,
            start_date=date(data_range[0], 1, 1),
            end_date=date(data_range[1], 12, 31),
            save_results=save_results
        )
        
        if not results.is_empty() and not save_results:
            # Display results
            Reporting.stats(
                results,
                {
                    "strategy_name": self.name,
                    "strategy_exit_time": self.STRATEGY_EXIT_TIME,
                    "strategy_type": self.type,
                    "interval": self.interval,
                    "exchange": self.exchange,
                }
            )
        
        return results
    
    @abstractmethod
    def generate_signals(self, data: Dict[str, pl.DataFrame]) -> pl.DataFrame:
        """
        Generate trading signals from market data
        
        Args:
            data: Dictionary of market data by exchange:segment
            
        Returns:
            DataFrame with trading signals containing columns:
            - tradingsymbol: Symbol to trade
            - entry_time: Entry timestamp
            - exit_time: Exit timestamp
            - transaction_type: BUY or SELL
            - quantity: Number of shares/lots
            - stoploss: Optional stoploss percentage (e.g., 0.02 for 2%)
        """
        pass