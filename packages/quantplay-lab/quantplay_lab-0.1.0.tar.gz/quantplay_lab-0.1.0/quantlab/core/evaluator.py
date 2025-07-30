"""Performance evaluation for backtesting"""

import polars as pl

from quantlab.utils.types import StrategyType
from quantlab.market.india.charges import Charges


def round_to_tick_expr(expr: pl.Expr) -> pl.Expr:
    """Round price to nearest tick size (0.05)"""
    return (expr * 20).round(0) / 20


class Evaluator:
    """Evaluates backtest performance"""
    
    def __init__(self, backtest_mode: StrategyType = "INTRADAY") -> None:
        self.backtest_mode: StrategyType = backtest_mode
        self.market_data: pl.DataFrame = pl.DataFrame()
    
    def apply_time_based_exit(
        self,
        trades_df: pl.DataFrame,
    ) -> pl.DataFrame:
        """Apply time-based exit prices to trades"""
        self.market_data = self.market_data.with_columns(
            pl.col("close").alias("entry_price"),
            pl.col("close").alias("close_price"),
            pl.col("date").alias("entry_time"),
            pl.col("date").alias("exit_time"),
            pl.col("symbol").alias("tradingsymbol"),
        )

        trades_df = trades_df.drop(
            column
            for column in ["entry_price", "close_price"]
            if column in trades_df.columns
        )

        trades_df = trades_df.join(
            self.market_data.select(["tradingsymbol", "entry_time", "entry_price"]),
            on=["tradingsymbol", "entry_time"],
            how="left",
        )
        trades_df = trades_df.join(
            self.market_data.select(["tradingsymbol", "exit_time", "close_price"]),
            on=["tradingsymbol", "exit_time"],
            how="left",
        )

        number_of_trades = len(trades_df)
        out_trades_df = trades_df.filter(
            (pl.col("entry_price").is_not_null() & (pl.col("entry_price") > 0))
            & (pl.col("close_price").is_not_null() & (pl.col("close_price") > 0))
        )

        trade_diff = number_of_trades - len(out_trades_df)

        if trade_diff > 0:
            print(f"Dropped {trade_diff} trades due to empty values")

        return out_trades_df
    
    def add_attributes(self, trades_df: pl.DataFrame) -> pl.DataFrame:
        """Add market data attributes based on strategy type"""
        if self.backtest_mode == "INTRADAY":
            return self._add_intraday_attributes(trades_df)
        elif self.backtest_mode == "OVERNIGHT":
            return self._add_overnight_attributes(trades_df)
        elif self.backtest_mode == "SWING":
            return self._add_swing_attributes(trades_df)
        else:
            raise ValueError(f"Unknown strategy type: {self.backtest_mode}")
    
    def _add_intraday_attributes(self, trades_df: pl.DataFrame) -> pl.DataFrame:
        """Add intraday-specific attributes"""
        return (
            trades_df.drop(
                col
                for col in ["date", "open", "high", "low", "close"]
                if col in trades_df.columns
            )
            .join(
                self.market_data.select(
                    ["tradingsymbol", "date_only", "date", "high", "low", "close"]
                ),
                on=["tradingsymbol", "date_only"],
                how="left",
            )
            .filter(
                (pl.col("date") > pl.col("entry_time"))
                & (pl.col("date") <= pl.col("exit_time"))
            )
            .with_columns(
                pl.when(pl.col("exit_time") == pl.col("date"))
                .then(1)
                .otherwise(0)
                .alias("is_trade_closed")
            )
        )
    
    def _add_overnight_attributes(self, trades_df: pl.DataFrame) -> pl.DataFrame:
        """Add overnight-specific attributes"""
        trades_df = trades_df.with_columns(
            pl.col("exit_time").dt.date().alias("date_only")
        )

        return (
            trades_df.drop(
                col
                for col in ["date", "open", "high", "low", "close"]
                if col in trades_df.columns
            )
            .join(
                self.market_data.select(
                    ["tradingsymbol", "date_only", "date", "high", "low", "close"]
                ),
                on=["tradingsymbol", "date_only"],
                how="left",
            )
            .filter(
                (pl.col("date") > pl.col("entry_time"))
                & (pl.col("date") <= pl.col("exit_time"))
            )
            .with_columns(
                pl.when(pl.col("exit_time") == pl.col("date"))
                .then(1)
                .otherwise(0)
                .alias("is_trade_closed")
            )
        )
    
    def _add_swing_attributes(self, trades_df: pl.DataFrame) -> pl.DataFrame:
        """Add swing-specific attributes"""
        return self._add_overnight_attributes(trades_df)
    
    def apply_stoploss(self, trades_df: pl.DataFrame) -> pl.DataFrame:
        """Apply stoploss logic to trades"""
        if "stoploss" not in trades_df.columns:
            return trades_df

        minimum_stoploss = trades_df.select(pl.col("stoploss").min()).to_series()[0]

        if minimum_stoploss <= 0:  # type: ignore
            raise ValueError(
                f"Invalid stoploss entry [{minimum_stoploss}] found in the trades data"
            )

        trades_df = trades_df.with_columns(
            pl.when(pl.col("transaction_type") == "SELL")
            .then(round_to_tick_expr((1 + pl.col("stoploss")) * pl.col("entry_price")))
            .otherwise(
                round_to_tick_expr((1 - pl.col("stoploss")) * pl.col("entry_price"))
            )
            .alias("stoploss_price")
        )

        trades_df = trades_df.with_columns(
            pl.when(
                (
                    (pl.col("transaction_type") == "SELL")
                    & (pl.col("high") >= pl.col("stoploss_price"))
                )
                | (
                    (pl.col("transaction_type") == "BUY")
                    & (pl.col("low") <= pl.col("stoploss_price"))
                )
            )
            .then(1)
            .otherwise(pl.col("is_trade_closed"))
            .alias("is_trade_closed"),
            pl.when(
                (
                    (pl.col("transaction_type") == "SELL")
                    & (pl.col("high") >= pl.col("stoploss_price"))
                )
                | (
                    (pl.col("transaction_type") == "BUY")
                    & (pl.col("low") <= pl.col("stoploss_price"))
                )
            )
            .then(pl.col("stoploss_price"))
            .otherwise(pl.col("close_price"))
            .alias("close_price"),
        )

        return trades_df
    
    def apply_charges(self, trades: pl.DataFrame) -> pl.DataFrame:
        """Apply Indian market charges to trades"""
        trades = trades.with_columns(
            pl.when(pl.col("exchange").is_in(["NSE", "BSE"]))
            .then(
                pl.when(pl.col("product").eq("CNC"))
                .then(pl.lit("DELIVERY"))
                .otherwise(pl.lit("INTRADAY"))
            )
            .otherwise(
                pl.when(pl.col("tradingsymbol").str.ends_with("FUT"))
                .then(pl.lit("FUT"))
                .otherwise(pl.lit("OPT"))
            )
            .alias("segment")
        ).with_columns(
            pl.struct(
                [
                    "exchange",
                    "segment",
                    "transaction_type",
                    "quantity",
                    "entry_price",
                    "exit_price",
                ]
            )
            .map_elements(lambda x: Charges.get_charges(**x), return_dtype=pl.Float64())
            .alias("charges")
        )

        filtered_columns = [
            "tradingsymbol",
            "transaction_type",
            "exchange",
            "quantity",
            "entry_price",
            "entry_time",
            "exit_price",
            "exit_time",
            "charges",
            (
                (pl.col("exit_price") - pl.col("entry_price"))
                .mul(pl.col("quantity"))
                .mul(
                    pl.when(pl.col("transaction_type").eq("SELL"))
                    .then(pl.lit(-1))
                    .otherwise(pl.lit(1))
                )
            )
            .sub(pl.col("charges"))
            .alias("pnl"),
        ]

        if "overnight_return" in trades.columns:
            filtered_columns.append("overnight_return")

        trades = trades.select(filtered_columns).sort("entry_time")

        return trades
    
    def evaluate_performance(
        self,
        trades: pl.DataFrame,
        market_data: pl.DataFrame,
    ) -> pl.DataFrame:
        """Evaluate complete performance of trades"""
        self.market_data = market_data

        trades_df = trades.clone()
        trades_df = trades_df.with_columns(
            pl.col("entry_time").dt.date().alias("date_only")
        )

        self.market_data = self.market_data.with_columns(
            pl.col("date").dt.date().alias("date_only")
        )

        # Apply time based exit
        trades_df = self.apply_time_based_exit(trades_df)
        trades_df = self.add_attributes(trades_df)
        trades_df = self.apply_stoploss(trades_df)

        # Filter for closed trades
        trades_df = trades_df.filter(pl.col("is_trade_closed") == 1)
        trades_df = trades_df.group_by(["tradingsymbol", "entry_time"]).agg(
            pl.all().first()
        )
        trades_df = trades_df.with_columns(pl.col("date").alias("closing_timestamp"))

        filtered_columns = [
            "tradingsymbol",
            "transaction_type",
            "quantity",
            "entry_price",
            "entry_time",
            "close_price",
            "closing_timestamp",
            "exchange",
            "product",
        ]

        if "overnight_return" in trades.columns:
            filtered_columns.append("overnight_return")

        trades_df = (
            trades_df.sort("entry_time")
            .select(filtered_columns)
            .rename(
                {
                    "close_price": "exit_price",
                    "closing_timestamp": "exit_time",
                }
            )
        )

        # Apply charges
        trades_df = self.apply_charges(trades_df)

        return trades_df