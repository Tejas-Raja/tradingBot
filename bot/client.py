"""
Binance Futures Testnet client wrapper.
Handles authentication, request signing, and HTTP communication.
"""

import hashlib
import hmac
import time
from urllib.parse import urlencode

import httpx

from bot.logging_config import get_logger

logger = get_logger(__name__)

BASE_URL = "https://testnet.binancefuture.com"


class BinanceClient:
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.session = httpx.Client(
            base_url=BASE_URL,
            headers={"X-MBX-APIKEY": self.api_key},
            timeout=10.0,
        )

    def _sign(self, params: dict) -> dict:
        """Add timestamp and HMAC-SHA256 signature to params."""
        params["timestamp"] = int(time.time() * 1000)
        query_string = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        params["signature"] = signature
        return params

    def _request(self, method: str, endpoint: str, params: dict = None, sign: bool = True):
        """Generic signed/unsigned HTTP request with logging."""
        params = params or {}
        if sign:
            params = self._sign(params)

        logger.info("REQUEST %s %s | params: %s", method.upper(), endpoint, {k: v for k, v in params.items() if k != "signature"})

        try:
            response = self.session.request(method, endpoint, params=params)
            data = response.json()
            logger.info("RESPONSE %s %s | status: %d | body: %s", method.upper(), endpoint, response.status_code, data)

            if response.status_code != 200:
                error_msg = data.get("msg", "Unknown API error")
                error_code = data.get("code", response.status_code)
                raise BinanceAPIError(f"[{error_code}] {error_msg}")

            return data

        except httpx.TimeoutException:
            logger.error("TIMEOUT calling %s %s", method.upper(), endpoint)
            raise NetworkError("Request timed out. Check your connection.")
        except httpx.RequestError as e:
            logger.error("NETWORK ERROR calling %s %s: %s", method.upper(), endpoint, str(e))
            raise NetworkError(f"Network error: {str(e)}")

    def get_exchange_info(self, symbol: str) -> dict:
        """Fetch symbol metadata (tick size, lot size, etc.)."""
        return self._request("GET", "/fapi/v1/exchangeInfo", sign=False)

    def place_order(self, **kwargs) -> dict:
        """Place a futures order."""
        return self._request("POST", "/fapi/v1/order", params=kwargs)

    def get_account(self) -> dict:
        """Fetch account information."""
        return self._request("GET", "/fapi/v2/account")

    def close(self):
        self.session.close()


class BinanceAPIError(Exception):
    """Raised when Binance returns a non-200 response."""
    pass


class NetworkError(Exception):
    """Raised on network/timeout failures."""
    pass
