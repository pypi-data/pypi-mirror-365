"""
vimeodlpy.utils.ffmpeg_check
===========================
Utility to check if FFmpeg is installed and available in the system PATH.

Functions:
----------
- ffmpeg_installed(): Returns True if FFmpeg is found in the system PATH, False otherwise.

Dependencies:
-------------
- shutil: For checking the availability of FFmpeg in the system using `which()`.
"""

import shutil

def ffmpeg_installed() -> bool:
    """
    Check whether FFmpeg is installed and available in the system PATH.

    Returns:
        bool: True if FFmpeg is found in the system PATH, False otherwise.
    """
    return shutil.which("ffmpeg") is not None
