"""Common type definitions for quantlab"""

from typing import Literal, TypedDict, Dict, List, Any
from datetime import datetime, date, time

# Strategy types
StrategyType = Literal["INTRADAY", "OVERNIGHT", "SWING", "BUYANDHOLD"]
TransactionType = Literal["BUY", "SELL"]
ProductType = Literal["MIS", "CNC", "NRML"]
ExchangeType = Literal["NSE", "BSE", "NFO", "BFO"]
SegmentType = Literal["EQ", "FUT", "OPT", "INDICES"]
OrderType = Literal["MARKET", "LIMIT", "SL", "SL-M"]

# Symbol configuration types
class EQConfig(TypedDict, total=False):
    is_liquid: bool
    is_fno_traded: bool
    sector_indices: bool
    extra_columns: List[str]


class FNOConfig(TypedDict, total=False):
    is_liquid: bool
    underlying: List[str]
    sector_indices: bool


class IndicesConfig(TypedDict, total=False):
    underlying: List[str]
    sector_indices: bool


SymbolConfig = Dict[str, EQConfig | FNOConfig | IndicesConfig]


# Trade type
class Trade(TypedDict):
    tradingsymbol: str
    transaction_type: TransactionType
    quantity: int
    entry_price: float
    entry_time: datetime
    exit_price: float
    exit_time: datetime
    pnl: float
    charges: float
    exchange: ExchangeType
    product: ProductType


# Backtest results types
class BacktestResultType(TypedDict):
    total_pnl: float
    bps: float
    max_dd: float
    average_monthly_pnl: float
    win_rate: float
    drawdown_stats: List[Dict[str, float | None]]
    time_stats: List[Dict[str, Any]]
    hour_stats: List[Dict[str, Any]]
    overnight_stats: List[Dict[str, Any]] | None
    loss_trades: List[Dict[str, Any]]
    win_trades: List[Dict[str, Any]]


class StrategyInfoType(TypedDict):
    strategy_name: str
    strategy_exit_time: time | None
    strategy_type: StrategyType | None
    interval: int | None
    exchange: ExchangeType | None