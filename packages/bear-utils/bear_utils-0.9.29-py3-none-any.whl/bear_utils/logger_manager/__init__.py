"""Logging utilities for Bear Utils."""

from typing import Any

from bear_utils.logger_manager._common import VERBOSE_CONSOLE_FORMAT
from bear_utils.logger_manager._log_level import DEBUG, ERROR, FAILURE, INFO, SUCCESS, VERBOSE, WARNING, LogLevel
from bear_utils.logger_manager._styles import DEFAULT_THEME
from bear_utils.logger_manager.logger_protocol import AsyncLoggerProtocol, LoggerProtocol
from bear_utils.logger_manager.loggers._console import LogConsole
from bear_utils.logger_manager.loggers.base_logger import BaseLogger
from bear_utils.logger_manager.loggers.buffer_logger import BufferLogger
from bear_utils.logger_manager.loggers.console_logger import ConsoleLogger
from bear_utils.logger_manager.loggers.fastapi_logger import LoggingClient, LoggingServer
from bear_utils.logger_manager.loggers.file_logger import FileLogger
from bear_utils.logger_manager.loggers.simple_logger import SimpleLogger
from bear_utils.logger_manager.loggers.sub_logger import SubConsoleLogger


def get_logger(
    console: bool = True,
    file: bool = False,
    queue_handler: bool = False,
    buffering: bool = False,
    **kwargs,
) -> BaseLogger | ConsoleLogger | BufferError | FileLogger:
    """Get a logger instance based on the specified parameters.

    Args:
        name (str): The name of the logger.
        level (int): The logging level.
        console (bool): Whether to enable console logging.
        file (bool): Whether to enable file logging.
        queue_handler (bool): Whether to use a queue handler.
        buffering (bool): Whether to enable buffering.
        style_disabled (bool): Whether to disable styling.
        logger_mode (bool): Whether the logger is in logger mode.
        **kwargs: Additional keyword arguments for customization.

    Returns:
        BaseLogger | ConsoleLogger | BufferLogger| FileLogger: An instance of the appropriate logger.
    """
    if (not console and not file) and buffering:
        return BufferLogger(queue_handler=queue_handler, **kwargs)
    if (console and file) or (console and buffering):
        return ConsoleLogger(queue_handler=queue_handler, buffering=buffering, **kwargs)
    if not console and not buffering and file:
        return FileLogger(queue_handler=queue_handler, **kwargs)
    return BaseLogger(**kwargs)


def get_console(namespace: str) -> tuple[BaseLogger, SubConsoleLogger]:
    """Get a console logger and a sub-logger for a specific namespace.

    Args:
        namespace (str): The namespace for the sub-logger.

    Returns:
        tuple[BaseLogger, SubConsoleLogger]: A tuple containing the base logger and the sub-logger.
    """
    base_logger = BaseLogger.get_instance(init=True)
    sub_logger = SubConsoleLogger(logger=base_logger, namespace=namespace)
    return base_logger, sub_logger


def get_sub_logger(
    logger: BaseLogger | ConsoleLogger | Any,
    namespace: str,
) -> SubConsoleLogger[BaseLogger | ConsoleLogger]:
    """Get a sub-logger for a specific namespace.

    Args:
        logger (BaseLogger): The parent logger.
        namespace (str): The namespace for the sub-logger.

    Returns:
        SubConsoleLogger: A sub-logger instance.
    """
    if not isinstance(logger, (BaseLogger | ConsoleLogger)):
        raise TypeError("Expected logger to be an instance of BaseLogger or ConsoleLogger")

    return SubConsoleLogger(logger=logger, namespace=namespace)


__all__ = [
    "DEBUG",
    "DEFAULT_THEME",
    "ERROR",
    "FAILURE",
    "INFO",
    "SUCCESS",
    "VERBOSE",
    "VERBOSE_CONSOLE_FORMAT",
    "WARNING",
    "AsyncLoggerProtocol",
    "BaseLogger",
    "BufferLogger",
    "ConsoleLogger",
    "FileLogger",
    "LogConsole",
    "LogLevel",
    "LoggerProtocol",
    "LoggingClient",
    "LoggingServer",
    "SimpleLogger",
    "SubConsoleLogger",
    "get_console",
    "get_logger",
    "get_sub_logger",
]
