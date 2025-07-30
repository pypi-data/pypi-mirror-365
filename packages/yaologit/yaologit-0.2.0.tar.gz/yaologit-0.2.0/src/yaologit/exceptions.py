"""
Custom exceptions for YaoLogit package
"""


class YaoLogitError(Exception):
    """Base exception for all YaoLogit errors"""
    pass


class ConfigurationError(YaoLogitError):
    """Raised when there's an error in configuration"""
    pass


class LockError(YaoLogitError):
    """Raised when unable to acquire process lock"""
    pass


class LoggerNotInitializedError(YaoLogitError):
    """Raised when trying to use logger before initialization"""
    pass