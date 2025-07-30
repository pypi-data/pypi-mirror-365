"""Custom exceptions for quantlab"""


class QuantlabError(Exception):
    """Base exception for quantlab"""
    pass


class DataError(QuantlabError):
    """Exception raised for data-related errors"""
    pass


class StrategyError(QuantlabError):
    """Exception raised for strategy-related errors"""
    pass


class BacktestError(QuantlabError):
    """Exception raised for backtesting errors"""
    pass


class ValidationError(QuantlabError):
    """Exception raised for validation errors"""
    pass