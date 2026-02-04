import json
import logging
import time

import requests
from requests.auth import HTTPBasicAuth

from spi_cli.xml_utils import parse_xml_response

logger = logging.getLogger(__name__)


def _parse_response(resp):
    """Parse response as JSON or XML based on content type or content."""
    content_type = resp.headers.get("Content-Type", "")
    text = resp.text.strip()
    # Check content type or if content starts with XML declaration
    if "xml" in content_type or text.startswith("<?xml"):
        logger.debug("Response is XML, converting to dict")
        return parse_xml_response(text)
    # Try JSON first, fall back to plain text wrapper
    try:
        return resp.json()
    except Exception:
        logger.debug("Response is plain text, wrapping in dict")
        return {"rl": {"message": text}}


class SPIClient:
    """Central client for ReversingLabs Spectra Intelligence API calls.

    Provides:
    - Authenticated requests.Session for direct API calls
    - Request logging (URL, status, size, duration)
    """

    def __init__(self, host, username, password):
        self.host = host.rstrip("/")
        self.username = username
        self.password = password
        self.auth = HTTPBasicAuth(username, password)

        self.session = requests.Session()
        self.session.auth = self.auth
        self.session.headers.update({
            "User-Agent": "SPI-CLI/1.0",
            "Accept": "application/json",
        })

    # -- Direct API helpers --------------------------------------------------

    def get(self, path, params=None):
        """Perform authenticated GET request and return parsed JSON/XML as dict."""
        url = f"{self.host}{path}"
        logger.debug("GET %s params=%s", url, params)
        start = time.time()

        resp = self.session.get(url, params=params)
        elapsed = time.time() - start

        logger.debug(
            "Response: status=%d size=%d bytes duration=%.2fs",
            resp.status_code, len(resp.content), elapsed,
        )
        resp.raise_for_status()
        return _parse_response(resp)

    def post(self, path, json_body=None, data=None, params=None, headers=None):
        """Perform authenticated POST request and return parsed JSON/XML as dict."""
        url = f"{self.host}{path}"
        logger.debug("POST %s params=%s body_size=%s", url, params,
                      len(json.dumps(json_body)) if json_body else len(data) if data else 0)
        start = time.time()

        resp = self.session.post(url, json=json_body, data=data, params=params, headers=headers)
        elapsed = time.time() - start

        logger.debug(
            "Response: status=%d size=%d bytes duration=%.2fs",
            resp.status_code, len(resp.content), elapsed,
        )
        resp.raise_for_status()
        return _parse_response(resp)

    def get_raw(self, path, params=None):
        """Perform authenticated GET and return raw Response (for binary downloads)."""
        url = f"{self.host}{path}"
        logger.debug("GET (raw) %s", url)
        start = time.time()

        resp = self.session.get(url, params=params, stream=True)
        elapsed = time.time() - start

        logger.debug(
            "Response: status=%d duration=%.2fs",
            resp.status_code, elapsed,
        )
        resp.raise_for_status()
        return resp

    def post_raw(self, path, json_body=None, data=None, params=None, headers=None):
        """Perform authenticated POST and return raw Response (for XML/text responses)."""
        url = f"{self.host}{path}"
        logger.debug("POST (raw) %s params=%s", url, params)
        start = time.time()

        resp = self.session.post(url, json=json_body, data=data, params=params, headers=headers)
        elapsed = time.time() - start

        logger.debug(
            "Response: status=%d size=%d bytes duration=%.2fs",
            resp.status_code, len(resp.content), elapsed,
        )
        resp.raise_for_status()
        return resp

