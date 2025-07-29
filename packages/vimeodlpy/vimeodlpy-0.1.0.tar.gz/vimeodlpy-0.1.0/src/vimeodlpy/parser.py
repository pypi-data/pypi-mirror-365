"""
vimeodlpy.parser
==============
This module provides helper functions to extract player configuration data and streaming URLs
from the HTML content of Vimeo video pages.

Functions:
----------
- extract_player_config(html: str) -> dict | None:
    Parses the HTML and extracts the `window.playerConfig` JavaScript object.

- extract_stream_url(json_data: dict) -> str | None:
    Extracts the HLS stream URL from the parsed player config JSON.

Dependencies:
-------------
- json: For decoding the embedded JavaScript object.
- bs4 (BeautifulSoup): For parsing HTML.
- logging: For logging debug, info, and error messages.
"""

import json
import logging
from bs4 import BeautifulSoup

logger = logging.getLogger("vimeodlpy.parser")


def extract_player_config(html: str) -> dict | None:
    """
    Extracts the `window.playerConfig` JavaScript object from the HTML page.

    Args:
        html (str): The HTML content of the Vimeo video page.

    Returns:
        dict | None: The extracted player config as a dictionary, or None if extraction fails.

    Logs:
        - DEBUG when a relevant script tag is found.
        - ERROR if JSON parsing fails.
        - WARNING if no playerConfig is found in the HTML.
    """
    logger.debug("Parsing HTML to locate playerConfig script...")
    soup = BeautifulSoup(html, "html.parser")

    for script in soup.find_all("script"):
        if script.string and "window.playerConfig" in script.string:
            logger.debug("Found script containing playerConfig.")
            try:
                json_string = script.string.split("window.playerConfig = ", 1)[1]
                config = json.loads(json_string)
                logger.debug("Successfully parsed playerConfig JSON.")
                return config
            except json.JSONDecodeError as e:
                logger.error("Failed to parse playerConfig JSON: %s", e)
                return None

    logger.warning("No 'playerConfig' data found in the HTML page.")
    return None


def extract_stream_url(json_data: dict) -> str | None:
    """
    Extracts the HLS stream URL from the player configuration JSON.

    Args:
        json_data (dict): The parsed player configuration data.

    Returns:
        str | None: The HLS stream URL if available, or None if extraction fails.

    Logs:
        - DEBUG when URL is successfully extracted.
        - ERROR if the expected keys are missing or data is invalid.
    """
    try:
        stream_url = json_data["request"]["files"]["hls"]["captions"]
        logger.debug("Extracted HLS stream URL: %s", stream_url)
        return stream_url
    except (TypeError, KeyError) as e:
        logger.error("Failed to extract HLS stream URL from player config: %s", e)
        return None
