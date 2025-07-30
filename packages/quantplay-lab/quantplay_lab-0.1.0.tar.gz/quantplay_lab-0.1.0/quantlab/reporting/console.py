"""Console output formatting for backtest results"""

import locale
from typing import Any, Literal, Dict, List

from rich.columns import Columns
from rich.console import Console
from rich.padding import Padding
from rich.table import Table
from rich.text import Text

from quantlab.utils.types import BacktestResultType, StrategyInfoType

try:
    locale.setlocale(locale.LC_NUMERIC, "en_IN")
except locale.Error:
    try:
        locale.setlocale(locale.LC_NUMERIC, "en_US.UTF-8")
    except locale.Error:
        pass


class ResultsFormatter:
    """Format and display backtest results in console"""
    
    def __init__(self) -> None:
        self.console = Console()
    
    def format_number(
        self, data: float | int | None, color: bool | str = False
    ) -> Text | None:
        """Format number with locale and color"""
        if data is None:
            return None
        
        # Determine format string
        if isinstance(data, float):
            str_format = f"{'+' if color is True and data > 0 else ''}%{'d' if data.is_integer() else '.2f'}"
        else:
            str_format = f"{'+' if color is True and data > 0 else ''}%d"
        
        text = Text(
            locale.format_string(str_format, data, grouping=True),
            justify="right",
        )
        text.stylize("white")
        
        if color is True:
            if data == 0:
                text.stylize("white")
            elif data > 0:
                text.stylize("green")
            else:
                text.stylize("indian_red")
        elif color:
            text.stylize(str(color))
        
        return text
    
    def strategy_stats(self, results: BacktestResultType) -> Table:
        """Create strategy statistics table"""
        stats_table = Table(title="Strategy Stats", show_lines=True)
        
        stats_table.add_column("Stat", justify="left", style="light_cyan1", no_wrap=True)
        stats_table.add_column("Value", justify="right", style="white")
        
        stats_table.add_row(
            "Overall PNL", self.format_number(results["total_pnl"], color=True)
        )
        stats_table.add_row("BPS", self.format_number(results["bps"], color="yellow"))
        stats_table.add_row(
            "Average Monthly PNL",
            self.format_number(results["average_monthly_pnl"], color=True),
        )
        stats_table.add_row(
            "Max DD", self.format_number(results["max_dd"], color="indian_red")
        )
        
        # Calculate risk/reward ratio
        if results["average_monthly_pnl"] != 0:
            risk_to_reward = abs(results["max_dd"]) / results["average_monthly_pnl"]
            stats_table.add_row(
                "Risk / Reward",
                self.format_number(
                    risk_to_reward,
                    color=(
                        "pale_green1" if risk_to_reward < 3 and risk_to_reward > 0 else "red1"
                    ),
                ),
            )
        
        stats_table.add_row("Win Rate %", self.format_number(results["win_rate"] * 100))
        
        return stats_table
    
    def strategy_info(self, strategy_info: StrategyInfoType) -> Table:
        """Create strategy information table"""
        info_table = Table(title="Strategy Info", show_lines=True)
        
        info_table.add_column(
            "Parameter", justify="left", style="light_cyan1", no_wrap=True
        )
        info_table.add_column("Value", justify="right", style="white")
        info_table.add_row("Strategy Name", strategy_info["strategy_name"])
        
        if strategy_info.get("strategy_type"):
            info_table.add_row("Holding Period", strategy_info["strategy_type"])
        
        if strategy_info.get("exchange"):
            info_table.add_row("Exchange", strategy_info["exchange"])
        
        if strategy_info.get("interval"):
            info_table.add_row(
                "Interval", f"{self.format_number(strategy_info['interval'])} min"
            )
        
        if strategy_info.get("strategy_exit_time"):
            info_table.add_row(
                "Exit Time", strategy_info["strategy_exit_time"].strftime(r"%H:%M")
            )
        
        return info_table
    
    def print_trades(self, trades: List[Dict[str, Any]], title: str) -> Table:
        """Create trades table"""
        bin_table = Table(title=title)
        
        bin_table.add_column("Tradingsymbol", justify="left", style="light_cyan1")
        bin_table.add_column("Transaction Type", justify="right", style="white")
        bin_table.add_column("Quantity", justify="right", style="white")
        bin_table.add_column("Entry Price", justify="right", style="white")
        bin_table.add_column("Entry Time", justify="right", style="white")
        bin_table.add_column("Exit Price", justify="right", style="white")
        bin_table.add_column("Exit Time", justify="right", style="white")
        bin_table.add_column("PnL", justify="right", style="white")
        
        for result in trades:
            bin_table.add_row(
                result["tradingsymbol"],
                result["transaction_type"],
                self.format_number(result["quantity"]),
                self.format_number(result["entry_price"]),
                str(result["entry_time"]),
                self.format_number(result["exit_price"]),
                str(result["exit_time"]),
                self.format_number(result["pnl"], color=True),
            )
        
        return bin_table
    
    def print_bin_metrics(
        self,
        results: BacktestResultType,
        name: Literal["time_stats", "hour_stats", "overnight_stats"],
    ) -> Table:
        """Create binned metrics table"""
        bin_table = Table(title=f"{name.replace('_stats', '').capitalize()} Stats")
        
        bin_table.add_column(
            name.replace("_stats", ""), justify="left", style="light_cyan1", no_wrap=True
        )
        bin_table.add_column("Trades", justify="right", style="white")
        bin_table.add_column("Win Rate %", justify="right", style="white")
        bin_table.add_column("PnL", justify="right", style="white")
        bin_table.add_column("BPS", justify="right", style="white")
        
        for result in results.get(name, []):
            bin_table.add_row(
                f"{result[name.replace('_stats', '')]}",
                self.format_number(result["total_trades"]),
                self.format_number(result["win_rate"]),
                self.format_number(result["pnl"], color=True),
                self.format_number(result["bps"], color=True),
            )
        
        return bin_table
    
    def yearly_drawdown(self, results: BacktestResultType) -> Table:
        """Create yearly statistics table"""
        info_table = Table(title="Yearly Stats")
        
        info_table.add_column("Year", justify="left", style="light_cyan1", no_wrap=True)
        info_table.add_column("Average Monthly PNL", justify="right", style="white")
        info_table.add_column("D1", justify="right", style="white")
        info_table.add_column("D2", justify="right", style="white")
        info_table.add_column("D3", justify="right", style="white")
        info_table.add_column("D4", justify="right", style="white")
        info_table.add_column("Trades", justify="right", style="white")
        
        last_row: Dict[str, float | None] = {}
        
        for i, result in enumerate(results["drawdown_stats"]):
            if result["year"] is None:
                last_row = result
                continue
            
            info_table.add_row(
                f"{result['year']}",
                self.format_number(result["average_monthly_pnl"], color=True),
                self.format_number(result["d1"]),
                self.format_number(result["d2"]),
                self.format_number(result["d3"]),
                self.format_number(result["d4"]),
                self.format_number(result["num_trades"]),
                end_section=(i == len(results["drawdown_stats"]) - 1),
            )
        
        if last_row:
            info_table.add_row(
                "Overall",
                self.format_number(last_row["average_monthly_pnl"], color=True),
                self.format_number(last_row["d1"]),
                self.format_number(last_row["d2"]),
                self.format_number(last_row["d3"]),
                self.format_number(last_row["d4"]),
                self.format_number(last_row["num_trades"]),
            )
        
        return info_table
    
    def title(self, strategy_info: StrategyInfoType) -> Text:
        """Create title text"""
        title = Text(f"Backtest Results : {strategy_info['strategy_name']}")
        title.stylize("yellow", start=19)
        return title
    
    def display_results(
        self, strategy_info: StrategyInfoType | None, results: BacktestResultType
    ) -> None:
        """Display complete backtest results"""
        row1: List[Table] = []
        row2: List[Table] = []
        
        self.console.rule(self.title(strategy_info) if strategy_info else "")
        
        if strategy_info is not None:
            row1.append(self.strategy_info(strategy_info))
        
        if "overnight_stats" in results and results["overnight_stats"]:
            row2.append(self.print_bin_metrics(results, name="overnight_stats"))
        
        row1.extend(
            [
                self.strategy_stats(results),
                self.yearly_drawdown(results),
            ],
        )
        
        row2.extend(
            [
                self.print_bin_metrics(results, "time_stats"),
                self.print_bin_metrics(results, "hour_stats"),
            ],
        )
        
        self.console.print(
            Padding(
                Columns(
                    row1,
                    padding=(4, 4),
                ),
                (2, 3, 2, 3),
            ),
        )
        self.console.rule(characters="--", style="grey53")
        self.console.print(
            Padding(
                Columns(
                    row2,
                    padding=(4, 4),
                ),
                (2, 3, 2, 3),
            ),
        )
        
        self.console.rule(characters="--", style="grey53")
        self.console.print(
            Padding(
                self.print_trades(results["win_trades"], "Win Trades"),
                (2, 3, 2, 3),
            ),
            Padding(
                self.print_trades(results["loss_trades"], "Loss Trades"),
                (0, 3, 2, 3),
            ),
        )
        
        self.console.rule()