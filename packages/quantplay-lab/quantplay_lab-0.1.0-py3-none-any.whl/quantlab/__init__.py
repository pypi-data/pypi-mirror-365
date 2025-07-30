"""
quantlab - High-performance backtesting engine for algorithmic trading
"""

__version__ = "0.1.0"

from quantlab.core.engine import Backtest
from quantlab.strategy.base import Strategy

__all__ = ["Backtest", "Strategy", "__version__"]