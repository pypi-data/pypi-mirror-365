"""
vimeodlpy.exceptions
==================
This module defines custom exceptions used throughout the `vimeodlpy` package.

Classes:
--------
- vimeodlpyError: Base class for all custom exceptions in the package.
- VideoNotFound: Raised when a Vimeo video cannot be found or accessed.
- StreamUrlExtractionError: Raised when the HLS stream URL cannot be extracted from the player config.
"""

class vimeodlpyError(Exception):
    """
    Base exception class for all errors raised by the vimeodlpy package.
    """


class VideoNotFound(vimeodlpyError):
    """
    Raised when a Vimeo video cannot be found or loaded.

    This may happen due to:
        - A non-existent or private video.
        - A network error or invalid response.
        - Failure to extract player configuration from the page.
    """


class StreamUrlExtractionError(vimeodlpyError):
    """
    Raised when the HLS stream URL could not be extracted from the player configuration.

    This usually indicates that the player config is malformed or missing required data.
    """
