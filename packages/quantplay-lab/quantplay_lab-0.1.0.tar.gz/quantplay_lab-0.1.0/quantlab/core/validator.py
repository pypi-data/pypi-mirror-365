"""Trade validation logic"""

from typing import get_args, List

import polars as pl

from quantlab.utils.types import StrategyType, TransactionType
from quantlab.utils.exceptions import ValidationError


class TradeValidator:
    """Validates trades data for backtesting"""
    
    @staticmethod
    def validate_trades(
        trades: pl.DataFrame,
        columns_to_validate: List[str] | None = None,
    ) -> None:
        """Validate trades DataFrame has required columns and correct data"""
        
        if columns_to_validate is None:
            columns_to_validate = [
                "tradingsymbol",
                "entry_time",
                "exit_time",
                "tag",
                "transaction_type",
                "strategy_type",
            ]
        
        if trades.is_empty():
            raise ValidationError("No trades found")

        # Check required columns exist
        for column in columns_to_validate:
            if column not in trades.columns:
                raise ValidationError(f"{column} must be provided in trades")

        # Validate transaction types
        if "transaction_type" in columns_to_validate:
            transaction_types = (
                trades.select("transaction_type").unique().to_series().to_list()
            )
            if len(transaction_types) > 2:
                raise ValidationError("More than 2 transaction types found")
            
            valid_types = set(get_args(TransactionType))
            if not set(transaction_types).issubset(valid_types):
                raise ValidationError(f"Invalid transaction types: {transaction_types}")

        # Validate strategy types
        if "strategy_type" in columns_to_validate:
            strategy_types = trades.select("strategy_type").unique().to_series().to_list()
            allowed_strategy_types = get_args(StrategyType)

            if len(strategy_types) != 1:
                raise ValidationError("All trades must have the same strategy_type")

            strategy_type = strategy_types[0]
            if strategy_type not in allowed_strategy_types:
                raise ValidationError(f"Invalid strategy_type: {strategy_type}")