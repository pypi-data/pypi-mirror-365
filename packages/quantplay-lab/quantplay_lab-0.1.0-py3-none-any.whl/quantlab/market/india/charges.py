"""Indian market charges calculation"""

from typing import Literal, TypedDict

from quantlab.utils.types import ExchangeType, TransactionType


class ChargesBreakdown(TypedDict):
    turnover: float
    brokerage: float
    stt_total: float | None
    exc_trans_charge: float
    notional_turnover: float | None
    stax: float
    ctt: float | None
    sebi_charges: float
    stamp_charges: float
    total_tax: float
    breakeven: float


DEFAULT_BROKERAGE = 0.0


class Charges:
    """Calculate Indian market charges for various segments"""
    
    @staticmethod
    def get_charges(
        quantity: int,
        transaction_type: TransactionType,
        segment: Literal["DELIVERY", "FUT", "OPT", "INTRADAY"],
        exchange: ExchangeType,
        entry_price: float = 0.0,
        exit_price: float = 0.0,
        brokerage: float = DEFAULT_BROKERAGE,
    ) -> float:
        """Calculate total charges for a trade"""
        assert exchange in ["NSE", "BSE", "NFO", "BFO"]
        assert segment in ["DELIVERY", "FUT", "OPT", "INTRADAY"]

        charges: ChargesBreakdown
        exchange = "NSE" if exchange[0] == "N" else "BSE"  # type: ignore

        if transaction_type == "BUY":
            buy_price, sell_price = entry_price, exit_price
        else:
            buy_price, sell_price = exit_price, entry_price

        if segment == "DELIVERY":
            charges = Charges.delivery(
                quantity,
                exchange,  # type: ignore
                buy_price,
                sell_price,
                brokerage,
            )
        elif segment == "INTRADAY":
            charges = Charges.intraday(
                quantity,
                exchange,  # type: ignore
                buy_price,
                sell_price,
                brokerage,
            )
        elif segment == "FUT":
            charges = Charges.futures(
                quantity,
                exchange,  # type: ignore
                buy_price,
                sell_price,
                brokerage,
            )
        elif segment == "OPT":
            charges = Charges.options(
                quantity,
                exchange,  # type: ignore
                buy_price,
                sell_price,
                brokerage,
            )

        return charges["total_tax"]

    @staticmethod
    def intraday(
        quantity: int,
        exchange: Literal["NSE", "BSE"],
        buy_price: float = 0.0,
        sell_price: float = 0.0,
        brokerage: float = DEFAULT_BROKERAGE,
    ) -> ChargesBreakdown:
        """Calculate charges for intraday equity trades"""
        turnover = (buy_price + sell_price) * quantity

        stt_total = round(sell_price * quantity * 0.00025)
        sebi_charges = turnover * 0.000001

        exc_trans_charge = (
            0.0000297 * turnover if exchange == "NSE" else 0.0000375 * turnover
        )
        nse_ipft = 0.000001 * turnover if exchange == "NSE" else 0
        exc_trans_charge = exc_trans_charge + nse_ipft

        stax = 0.18 * (brokerage + exc_trans_charge + sebi_charges)
        stamp_charges = round(buy_price * quantity * 0.00003)
        total_tax = (
            brokerage + stt_total + exc_trans_charge + stax + sebi_charges + stamp_charges
        )
        breakeven = total_tax / quantity

        return {
            "turnover": turnover,
            "brokerage": brokerage,
            "stt_total": stt_total,
            "exc_trans_charge": exc_trans_charge,
            "stax": stax,
            "sebi_charges": sebi_charges,
            "stamp_charges": stamp_charges,
            "total_tax": total_tax,
            "breakeven": breakeven,
        }

    @staticmethod
    def delivery(
        quantity: int,
        exchange: Literal["NSE", "BSE"],
        buy_price: float = 0.0,
        sell_price: float = 0.0,
        brokerage: float = DEFAULT_BROKERAGE,
    ) -> ChargesBreakdown:
        """Calculate charges for delivery equity trades"""
        turnover = (buy_price + sell_price) * quantity
        stt_total = round(turnover * 0.001)
        sebi_charges = turnover * 0.000001
        exc_trans_charge = (
            0.0000297 * turnover if exchange == "NSE" else 0.0000375 * turnover
        )
        nse_ipft = 0.000001 * turnover if exchange == "NSE" else 0
        exc_trans_charge = exc_trans_charge + nse_ipft
        stax = 0.18 * (brokerage + exc_trans_charge + sebi_charges)
        stamp_charges = round(buy_price * quantity * 0.00015)
        total_tax = (
            brokerage + stt_total + exc_trans_charge + stax + sebi_charges + stamp_charges
        )
        breakeven = total_tax / quantity

        return {
            "turnover": turnover,
            "brokerage": brokerage,
            "stt_total": stt_total,
            "exc_trans_charge": exc_trans_charge,
            "stax": stax,
            "sebi_charges": sebi_charges,
            "stamp_charges": stamp_charges,
            "total_tax": total_tax,
            "breakeven": breakeven,
        }

    @staticmethod
    def futures(
        quantity: int,
        exchange: Literal["NSE", "BSE"],
        buy_price: float = 0.0,
        sell_price: float = 0.0,
        brokerage: float = DEFAULT_BROKERAGE,
    ) -> ChargesBreakdown:
        """Calculate charges for futures trades"""
        turnover = (buy_price + sell_price) * quantity
        stt_total = round(sell_price * quantity * 0.0002)
        sebi_charges = turnover * 0.000001
        exc_trans_charge = 0.0000173 * turnover if exchange == "NSE" else 0
        nse_ipft = 0.000001 * turnover if exchange == "NSE" else 0
        exc_trans_charge = exc_trans_charge + nse_ipft
        stax = 0.18 * (brokerage + exc_trans_charge + sebi_charges)
        stamp_charges = round(buy_price * quantity * 0.00002)
        total_tax = (
            brokerage + stt_total + exc_trans_charge + stax + sebi_charges + stamp_charges
        )
        breakeven = total_tax / quantity

        return {
            "turnover": turnover,
            "brokerage": brokerage,
            "stt_total": stt_total,
            "exc_trans_charge": exc_trans_charge,
            "stax": stax,
            "sebi_charges": sebi_charges,
            "stamp_charges": stamp_charges,
            "total_tax": total_tax,
            "breakeven": breakeven,
        }

    @staticmethod
    def options(
        quantity: int,
        exchange: Literal["NSE", "BSE"],
        buy_price: float = 0.0,
        sell_price: float = 0.0,
        brokerage: float = DEFAULT_BROKERAGE,
    ) -> ChargesBreakdown:
        """Calculate charges for options trades"""
        turnover = (buy_price + sell_price) * quantity
        stt_total = round(sell_price * quantity * 0.001)
        sebi_charges = turnover * 0.000001
        exc_trans_charge = (
            0.0003503 * turnover if exchange == "NSE" else 0.000325 * turnover
        )
        nse_ipft = 0.000005 * turnover if exchange == "NSE" else 0
        exc_trans_charge = exc_trans_charge + nse_ipft
        stax = 0.18 * (brokerage + exc_trans_charge + sebi_charges)
        stamp_charges = round(buy_price * quantity * 0.00003)
        total_tax = (
            brokerage + stt_total + exc_trans_charge + stax + sebi_charges + stamp_charges
        )
        breakeven = total_tax / quantity

        return {
            "turnover": turnover,
            "brokerage": brokerage,
            "stt_total": stt_total,
            "exc_trans_charge": exc_trans_charge,
            "stax": stax,
            "sebi_charges": sebi_charges,
            "stamp_charges": stamp_charges,
            "total_tax": total_tax,
            "breakeven": breakeven,
        }