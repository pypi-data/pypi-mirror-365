"""
vimeodlpy.downloader
=======================
Handles the Vimeo video downloading process using a scraper, player config parsing,
and FFmpeg. It includes all the logic to:
- Access the video page using a Cloudflare bypass scraper
- Extract the player config JSON and HLS stream URL
- Determine video duration using FFprobe
- Download the video using FFmpeg and optionally display a custom progress bar

Classes:
--------
- VimeoDownloader: Main class that manages the download process and error handling.

Exceptions:
-----------
- VideoNotFound: Raised when the video page or player config can't be retrieved.
- StreamUrlExtractionError: Raised when the HLS stream URL can't be extracted.

Usage:
------
from vimeodlpy.downloader import VimeoDownloader

downloader = VimeoDownloader(show_progress=True)
downloader.download("https://vimeo.com/123456789", "output.mp4")
"""

import os
import re
import subprocess
import shlex
from typing import Optional

import ffmpeg
import cloudscraper
from tqdm import tqdm

from vimeodlpy.logger import get_logger
from vimeodlpy.parser import extract_player_config, extract_stream_url
from vimeodlpy.exceptions import VideoNotFound, StreamUrlExtractionError

logger = get_logger()


class VimeoDownloader:
    """
    Downloads videos from Vimeo using a scraper, HLS stream extraction, and FFmpeg.

    Attributes
    ----------
    scraper : cloudscraper.CloudScraper
        A scraper instance that bypasses Cloudflare protection.
    show_progress : bool
        Whether to display a custom progress bar during the FFmpeg download.

    Methods
    -------
    download(url: str, output_path: str, referer: Optional[str] = None) -> None
        Downloads the video from Vimeo and saves it to the given path.
    """

    def __init__(self, proxies: Optional[dict] = None, show_progress: bool = False):
        logger.debug("Initializing VimeoDownloader (show_progress=%s)", show_progress)
        self.scraper = cloudscraper.create_scraper()
        self.show_progress = show_progress
        if proxies:
            logger.debug("Applying proxies: %s", proxies)
            self.scraper.proxies.update(proxies)

    def _get_page(self, url: str, referer: Optional[str] = None) -> str:
        """
        Fetch the HTML content of the Vimeo video page.

        Parameters
        ----------
        url : str
            Full Vimeo video URL.
        referer : str, optional
            Optional HTTP referer header to include in the request.

        Returns
        -------
        str
            Raw HTML of the page.

        Raises
        ------
        VideoNotFound
            If the page fails to load or is inaccessible.
        """
        logger.debug("Fetching page: %s (referer=%s)", url, referer)
        try:
            headers = self.scraper.headers.copy()
            if referer:
                headers["Referer"] = referer
            response = self.scraper.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error("Failed to access the page: %s", e)
            raise VideoNotFound(f"Failed to access video page: {e}") from e

    def _get_duration(self, stream_url: str) -> float:
        """
        Extract the duration of the video using ffprobe.

        Parameters
        ----------
        stream_url : str
            Direct HLS stream URL.

        Returns
        -------
        float
            Duration in seconds. Returns 0.0 if duration could not be determined.
        """
        try:
            logger.debug("Probing video duration using FFprobe")
            probe = ffmpeg.probe(stream_url)
            return float(probe['format']['duration'])
        except ffmpeg.Error as e:
            logger.warning("FFmpeg error while probing video duration: %s", e)
            return 0.0
        except KeyError as e:
            logger.warning("Missing duration key in FFprobe output: %s", e)
            return 0.0
        except ValueError as e:
            logger.warning("Invalid duration value in FFprobe output: %s", e)
            return 0.0

    def _validate_output_path(self, output_path: str) -> None:
        if not output_path.lower().endswith(".mp4"):
            raise ValueError("Output path must end with '.mp4'")
        output_dir = os.path.dirname(output_path) or "."
        if not os.path.exists(output_dir):
            raise FileNotFoundError("The destination directory does not exist.")

    def _extract_stream_url(self, html: str) -> str:
        json_data = extract_player_config(html)
        if not json_data:
            raise VideoNotFound("Failed to extract playerConfig from HTML page.")
        stream_url = extract_stream_url(json_data)
        if not stream_url:
            raise StreamUrlExtractionError("Failed to extract HLS stream URL.")
        return stream_url

    def _run_ffmpeg(self, stream_url: str, output_path: str, duration: float) -> None:
        cmd = [
            "ffmpeg", "-y",
            "-i", stream_url,
            "-c", "copy",
            "-bsf:a", "aac_adtstoasc",
            "-loglevel", "info",
            output_path
        ]

        logger.debug("Running FFmpeg command: %s", " ".join(shlex.quote(c) for c in cmd))

        try:
            with subprocess.Popen(cmd, stderr=subprocess.PIPE, universal_newlines=True, bufsize=1) as proc:
                if self.show_progress and duration > 0:
                    self._show_progress_bar(proc, duration)
                else:
                    for line in proc.stderr:
                        logger.debug("FFmpeg: %s", line.strip())

                proc.wait()
                if proc.returncode != 0:
                    raise RuntimeError(f"FFmpeg exited with code {proc.returncode}")
        except Exception as e:
            logger.error("FFmpeg error: %s", e)
            raise RuntimeError(f"FFmpeg download failed: {e}") from e

    def _show_progress_bar(self, proc: subprocess.Popen, duration: float) -> None:
        pattern = re.compile(r'time=(\d+):(\d+):(\d+).(\d+)')
        pbar = tqdm(
            total=duration,
            desc="⬇️  Downloading",
            unit="s",
            dynamic_ncols=False,
            ncols=60,
            bar_format="{desc} |{bar}| {percentage:3.0f}% [{elapsed}<{remaining}]"
        )

        for line in proc.stderr:
            match = pattern.search(line)
            if match:
                h, m, s, ms = map(int, match.groups())
                current_time = h * 3600 + m * 60 + s + ms / 100
                pbar.n = min(current_time, duration)
                pbar.refresh()
        pbar.close()

    def download(self, url: str, output_path: str, referer: Optional[str] = None) -> None:
        """
        Download a Vimeo video and save it as an MP4 file.

        Parameters
        ----------
        url : str
            Full Vimeo video URL.
        output_path : str
            Output path for the downloaded MP4 file (must end with .mp4).
        referer : str, optional
            Optional referer header to include in the HTTP request.

        Raises
        ------
        ValueError
            If the output path does not end with .mp4.
        FileNotFoundError
            If the destination directory does not exist.
        VideoNotFound
            If the video page or player config could not be retrieved.
        StreamUrlExtractionError
            If the HLS stream URL could not be extracted.
        RuntimeError
            If FFmpeg fails to complete the download.
        """
        logger.info("Starting download: %s → %s", url, output_path)

        self._validate_output_path(output_path)
        html = self._get_page(url, referer)
        stream_url = self._extract_stream_url(html)
        duration = self._get_duration(stream_url)
        self._run_ffmpeg(stream_url, output_path, duration)

        logger.info("Download successfully completed → %s", output_path)
