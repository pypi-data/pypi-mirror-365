"""
vimeodlpy
=======

A lightweight Python library and CLI to download Vimeo videos using FFmpeg.

Features:
---------
- Supports direct and embedded Vimeo player URLs.
- Automatically extracts HLS stream URLs from video pages.
- Uses FFmpeg for fast, reliable downloads with progress bar support.
- Proxy and referer support for restricted or embedded videos.

Quick Example:
--------------
>>> from vimeodlpy import downloader
>>> downloader.download("https://vimeo.com/123456789", "output.mp4")

Requirements:
-------------
- FFmpeg must be installed and accessible in your system PATH.

Author:
-------
- moijesuis2enmoi — https://github.com/moijesuis2enmoi

License:
--------
Apache License 2.0
https://www.apache.org/licenses/LICENSE-2.0
"""

from vimeodlpy.downloader import VimeoDownloader

__version__ = "0.1.0"
__author__ = "moijesuis2enmoi"
__license__ = "Apache-2.0"
__all__ = ["VimeoDownloader", "downloader"]

downloader = VimeoDownloader()
