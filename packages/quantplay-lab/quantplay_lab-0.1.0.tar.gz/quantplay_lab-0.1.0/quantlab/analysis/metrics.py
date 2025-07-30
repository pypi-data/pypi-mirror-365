"""Performance metrics and analysis"""

from datetime import timedelta
from typing import List, Dict, Any

import polars as pl
from polars.dataframe.group_by import GroupBy

from quantlab.utils.types import BacktestResultType, StrategyInfoType
from quantlab.reporting.console import ResultsFormatter


class Reporting:
    """Calculate and display backtest performance metrics"""
    
    @staticmethod
    def get_group_metrics(
        trades: GroupBy, additional_cols: List[pl.Expr | str] = []
    ) -> pl.DataFrame:
        """Calculate metrics for grouped trades"""
        return trades.agg(
            pl.col("pnl").sum().alias("pnl"),
            pl.col("entry_turnover").sum().alias("entry_turnover"),
            pl.col("pnl").filter(pl.col("pnl") <= 0).len().alias("loss_trades"),
            pl.col("pnl").filter(pl.col("pnl") > 0).len().alias("win_trades"),
            pl.col("pnl").len().alias("total_trades"),
        ).select(
            *additional_cols,
            "pnl",
            "total_trades",
            (pl.col("win_trades") / (pl.col("win_trades") + pl.col("loss_trades")) * 100)
            .round(2)
            .alias("win_rate"),
            (pl.col("pnl") / pl.col("entry_turnover") * 10000).alias("bps"),
        )
    
    @staticmethod
    def overnight_return_metrics(
        trades: pl.DataFrame, interval: float = 0.01
    ) -> pl.DataFrame:
        """Calculate metrics grouped by overnight returns"""
        overnight_group = trades.with_columns(
            pl.col("overnight_return")
            .mul(100)
            .round()
            .truediv(100)
            .alias("overnight_return"),
            (pl.col("quantity") * pl.col("entry_price")).alias("entry_turnover"),
        ).group_by("overnight_return")

        return Reporting.get_group_metrics(overnight_group, ["overnight_return"]).sort(
            "overnight_return"
        )
    
    @staticmethod
    def time_metrics(
        trades: pl.DataFrame, interval: int = 15
    ) -> tuple[pl.DataFrame, pl.DataFrame]:
        """Calculate time-based metrics"""
        time_df = (
            trades.with_columns(
                (pl.col("quantity") * pl.col("entry_price")).alias("entry_turnover"),
            )
            .group_by_dynamic("entry_time", every=timedelta(minutes=interval))
            .agg(
                pl.col("pnl").sum().alias("pnl"),
                pl.col("entry_turnover").sum().alias("entry_turnover"),
            )
        )

        interval_stats = (
            Reporting.get_group_metrics(
                time_df.group_by(pl.col("entry_time").dt.time()), ["entry_time"]
            )
            .sort("entry_time")
            .rename({"entry_time": "time"})
        )

        hourly_stats = (
            Reporting.get_group_metrics(
                time_df.group_by(pl.col("entry_time").dt.hour()), ["entry_time"]
            )
            .sort("entry_time")
            .rename({"entry_time": "hour"})
        )

        return interval_stats, hourly_stats
    
    @staticmethod
    def drawdown(trades_df: pl.DataFrame) -> pl.Series:
        """Calculate top drawdowns"""
        return (
            trades_df.select([pl.col("entry_time").dt.date().alias("date"), "pnl"])
            .group_by("date")
            .sum()
            .sort("date")
            .with_columns(pl.col("pnl").cum_sum().alias("pnl"))
            .with_columns(pl.col("pnl").cum_max().alias("cum_max"))
            .with_columns(pl.col("pnl").sub(pl.col("cum_max")).alias("drawdown"))
            .top_k(5, by="drawdown", reverse=True)
            .select("drawdown")
            .sort("drawdown")
            .to_series()
        )
    
    @staticmethod
    def average_monthly_pnl(trades_df: pl.DataFrame) -> float:
        """Calculate average monthly PnL"""
        return (
            trades_df.select(
                [
                    pl.col("entry_time").dt.month().alias("month"),
                    pl.col("entry_time").dt.year().alias("year"),
                    "pnl",
                ]
            )
            .group_by(["month", "year"])
            .sum()
            .mean()
            .select("pnl")
            .to_series()
            .to_list()[0]
        )
    
    @staticmethod
    def stats(
        trades_df: pl.DataFrame,
        strategy_info: StrategyInfoType | None = None,
        result_formatter: ResultsFormatter | None = None,
    ) -> pl.DataFrame:
        """
        Calculate and display comprehensive backtest statistics
        
        Args:
            trades_df: DataFrame with trade results
            strategy_info: Strategy metadata
            result_formatter: Formatter for console output
            
        Returns:
            DataFrame with yearly statistics
        """
        if result_formatter is None:
            result_formatter = ResultsFormatter()
        
        stats: List[Dict[str, float | None]] = []

        # Calculate overall metrics
        bps = (
            trades_df.select(
                "pnl",
                (pl.col("quantity") * pl.col("entry_price")).alias("entry_turnover"),
            )
            .sum()
            .select((pl.col("pnl") / pl.col("entry_turnover") * 10000).alias("bps"))
            .item(0, "bps")
        )

        total_pnl = (
            trades_df.select("pnl")
            .sum()
            .item(0, "pnl")
        )

        # Get top losing and winning trades
        loss_trades = (
            trades_df.select(
                [
                    "tradingsymbol",
                    "transaction_type",
                    "quantity",
                    "entry_price",
                    "entry_time",
                    "exit_price",
                    "exit_time",
                    "pnl",
                ]
            )
            .sort("pnl")
            .head(10)
        )

        win_trades = (
            trades_df.select(
                [
                    "tradingsymbol",
                    "transaction_type",
                    "quantity",
                    "entry_price",
                    "entry_time",
                    "exit_price",
                    "exit_time",
                    "pnl",
                ]
            )
            .sort("pnl", descending=True)
            .head(10)
        )

        # Calculate drawdowns and average PnL
        total_drawdown = Reporting.drawdown(trades_df)
        total_average_pnl = Reporting.average_monthly_pnl(trades_df)

        max_dd = total_drawdown[0] if len(total_drawdown) > 0 else 0
        monthly_pnl = total_average_pnl
        
        win_rate = (
            trades_df.select(
                pl.col("pnl").filter(pl.col("pnl") > 0).len().alias("win_trades")
            )
            .with_columns(pl.col("win_trades").truediv(len(trades_df)).alias("win_rate"))
            .item(0, "win_rate")
        )

        # Add overall stats
        stats.append(
            {
                "year": None,
                "average_monthly_pnl": total_average_pnl,
                "d1": total_drawdown[0] if len(total_drawdown) > 0 else None,
                "d2": total_drawdown[1] if len(total_drawdown) > 1 else None,
                "d3": total_drawdown[2] if len(total_drawdown) > 2 else None,
                "d4": total_drawdown[3] if len(total_drawdown) > 3 else None,
                "num_trades": len(trades_df),
            }
        )

        # Calculate yearly stats
        for year, df in trades_df.group_by(pl.col("entry_time").dt.year()):
            year_drawdown = Reporting.drawdown(df)
            year_average_pnl = Reporting.average_monthly_pnl(df)

            if len(year_drawdown) < 4:
                continue

            stats.append(
                {
                    "year": year[0],  # type: ignore
                    "average_monthly_pnl": year_average_pnl,
                    "d1": year_drawdown[0],
                    "d2": year_drawdown[1],
                    "d3": year_drawdown[2],
                    "d4": year_drawdown[3],
                    "num_trades": len(df),
                }
            )

        # Calculate time-based metrics
        time_stats, hour_stats = Reporting.time_metrics(trades_df)

        # Prepare results
        backtest_results: BacktestResultType = {
            "total_pnl": total_pnl,
            "bps": bps,
            "average_monthly_pnl": monthly_pnl,
            "max_dd": max_dd,
            "win_rate": win_rate,
            "drawdown_stats": stats,
            "hour_stats": hour_stats.to_dicts(),
            "time_stats": time_stats.to_dicts(),
            "loss_trades": loss_trades.to_dicts(),
            "win_trades": win_trades.to_dicts(),
        }

        # Add overnight metrics if available
        if "overnight_return" in trades_df:
            overnight_stats = Reporting.overnight_return_metrics(trades_df)
            backtest_results["overnight_stats"] = overnight_stats.to_dicts()

        # Display results
        result_formatter.display_results(strategy_info, backtest_results)

        # Print number of trades and drawdown
        print(f"\nNumber of trades: {len(trades_df)}")
        print(f"Maximum drawdown: {max_dd:.2f}")

        return pl.from_dicts(stats).sort("year", descending=True)