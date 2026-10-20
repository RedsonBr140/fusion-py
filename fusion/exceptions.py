from __future__ import annotations

import requests


class FusionError(Exception):
    """Base exception for all fusion-py errors."""


class FusionHTTPError(FusionError):
    """Raised when a request to the Fusion DMS portal returns an error status."""

    def __init__(self, message: str, *, status_code: int, response: requests.Response):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class FusionAuthError(FusionError):
    """Raised when login to the Fusion DMS portal fails."""
