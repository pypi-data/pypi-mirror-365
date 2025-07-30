"""Data loading utilities for backtesting"""

import os
from datetime import date
from pathlib import Path
from typing import Dict, Callable

import polars as pl

from quantlab.utils.types import (
    ExchangeType, SegmentType, SymbolConfig,
    EQConfig, FNOConfig, IndicesConfig
)
from quantlab.utils.exceptions import DataError


class BacktestDataLoader:
    """Load historical market data for backtesting"""
    
    def __init__(
        self, 
        data_path: str = "./data",
        data_range: tuple[int, int] | None = None
    ):
        """
        Initialize data loader
        
        Args:
            data_path: Base path to market data
            data_range: Year range for data loading (start_year, end_year)
        """
        self.data_path = Path(data_path)
        
        if data_range is None:
            data_range = (2018, date.today().year)
        self.data_range = data_range
        
        self.SEGMENT_FN_MAP: Dict[SegmentType, Callable[..., pl.DataFrame]] = {
            "EQ": self.load_equity_data,
            "FUT": self.load_futures_data,
            "OPT": self.load_options_data,
            "INDICES": self.load_index_data,
        }
    
    def load_data(self, symbol_config: SymbolConfig) -> Dict[str, pl.DataFrame]:
        """
        Load data based on symbol configuration
        
        Args:
            symbol_config: Dictionary specifying which symbols to load
            
        Returns:
            Dictionary of DataFrames keyed by exchange:segment
        """
        data: Dict[str, pl.DataFrame] = {}
        
        for exchange_segment in symbol_config:
            exchange, segment = exchange_segment.split("_")  # type: ignore
            key = exchange_segment.replace("_", ":")
            
            data[key] = self.SEGMENT_FN_MAP[segment](  # type: ignore
                exchange, symbol_config[exchange_segment]  # type: ignore
            )
        
        return data
    
    def load_equity_data(
        self, 
        exchange: ExchangeType, 
        config: EQConfig
    ) -> pl.DataFrame:
        """Load equity market data"""
        filters = (pl.col("date").dt.year() > self.data_range[0]) & (
            pl.col("date").dt.year() <= self.data_range[1]
        )
        
        # Load day candles for filtering
        day_candles_path = self.data_path / exchange / "EQ" / "processed_day_candles.parquet"
        
        if not day_candles_path.exists():
            raise DataError(f"Day candles not found at {day_candles_path}")
            
        day_candles = pl.read_parquet(str(day_candles_path))
        
        if "closest_fno_expiry" in day_candles.columns:
            day_candles = day_candles.with_columns(
                pl.when(pl.col("closest_fno_expiry").is_not_null())
                .then(pl.lit(True))
                .otherwise(pl.lit(False))
                .alias("is_fno")
            )
        
        # Apply filters based on config
        if config.get("is_liquid", False):
            liquid_symbols = (
                day_candles.filter(pl.col("is_liquid"))
                .select("symbol")
                .to_series()
                .unique()
            )
            filters = filters & pl.col("symbol").is_in(liquid_symbols)
        
        if config.get("sector_indices", False):
            sector_symbols = (
                day_candles.filter(pl.col("underlying_sector").is_not_null())
                .select("symbol")
                .to_series()
                .unique()
            )
            filters = filters & pl.col("symbol").is_in(sector_symbols)
        
        # Load minute data
        minute_path = self.data_path / exchange / "EQ" / "minute"
        
        if not minute_path.exists():
            raise DataError(f"Minute data not found at {minute_path}")
        
        data = (
            pl.scan_parquet(str(minute_path / "*.parquet"))
            .with_columns(pl.lit(None, pl.UInt32).alias("oi"))
            .filter(filters)
            .collect()
        )
        
        return data
    
    def load_options_data(
        self, 
        exchange: ExchangeType, 
        config: FNOConfig
    ) -> pl.DataFrame:
        """Load options market data"""
        underlyings = config.get("underlying", [])
        
        if not underlyings:
            raise DataError("No underlying symbols specified for options")
        
        data_paths = []
        for underlying in underlyings:
            path = self.data_path / exchange / "OPT" / "minute" / underlying
            if path.exists():
                data_paths.append(str(path))
        
        if not data_paths:
            raise DataError(f"No options data found for {underlyings}")
        
        filters = (pl.col("date").dt.year() > self.data_range[0]) & (
            pl.col("date").dt.year() <= self.data_range[1]
        )
        
        data = pl.scan_parquet(data_paths).filter(filters).collect()
        
        if data.is_empty():
            raise DataError("No options data found for specified criteria")
        
        return data
    
    def load_futures_data(
        self, 
        exchange: ExchangeType, 
        config: FNOConfig
    ) -> pl.DataFrame:
        """Load futures market data"""
        underlyings = config.get("underlying", [])
        
        if not underlyings:
            raise DataError("No underlying symbols specified for futures")
        
        data_paths = []
        for underlying in underlyings:
            path = self.data_path / exchange / "FUT" / "minute" / underlying
            if path.exists():
                data_paths.append(str(path))
        
        if not data_paths:
            raise DataError(f"No futures data found for {underlyings}")
        
        filters = (pl.col("date").dt.year() > self.data_range[0]) & (
            pl.col("date").dt.year() <= self.data_range[1]
        )
        
        data = pl.scan_parquet(data_paths).filter(filters).collect()
        
        if data.is_empty():
            raise DataError("No futures data found for specified criteria")
        
        return data
    
    def load_index_data(
        self, 
        exchange: ExchangeType, 
        config: IndicesConfig
    ) -> pl.DataFrame:
        """Load index market data"""
        underlyings = config.get("underlying", [])
        
        if not underlyings:
            raise DataError("No underlying indices specified")
        
        data_paths = []
        for underlying in underlyings:
            path = self.data_path / exchange / "INDICES" / "minute" / f"{underlying}.parquet"
            if path.exists():
                data_paths.append(str(path))
        
        if not data_paths:
            raise DataError(f"No index data found for {underlyings}")
        
        filters = (pl.col("date").dt.year() > self.data_range[0]) & (
            pl.col("date").dt.year() <= self.data_range[1]
        )
        
        data = (
            pl.scan_parquet(data_paths)
            .with_columns(pl.lit(None, pl.UInt32).alias("oi"))
            .filter(filters)
            .collect()
        )
        
        return data