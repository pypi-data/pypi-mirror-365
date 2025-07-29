"""
vimeodlpy.logger
==============
Provides a preconfigured logger for the `vimeodlpy` package.

Functions:
----------
- get_logger(name: str = "vimeodlpy") -> logging.Logger:
    Returns a logger with a consistent format and error-level logging by default.

Dependencies:
-------------
- logging: Standard Python logging module.
"""

import logging

def get_logger(name: str = "vimeodlpy") -> logging.Logger:
    """
    Create and return a preconfigured logger for the given name.

    The logger uses the following format:
        [timestamp] - [log level] - [message]

    Args:
        name (str): The name of the logger. Defaults to "vimeodlpy".

    Returns:
        logging.Logger: A logger instance configured with basic settings.
    """
    logging.basicConfig(
        level=logging.WARNING,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(name)
