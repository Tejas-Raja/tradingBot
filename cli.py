#!/usr/bin/env python3
"""
CLI entry point for the Binance Futures Testnet trading bot.

Usage examples:
    python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
    python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 80000
    python cli.py --symbol BTCUSDT --side SELL --type STOP_MARKET --quantity 0.001 --stop-price 75000
"""

import argparse
import os
import sys

from bot.client import BinanceClient, BinanceAPIError, NetworkError
from bot.logging_config import setup_logging, get_logger
from bot.orders import place_order, build_order_params, format_order_summary, format_order_response
from bot.validators import (
    validate_symbol,
    validate_side,
    validate_order_type,
    validate_quantity,
    validate_price,
    validate_stop_price,
    ValidationError,
)

# Initialise logging before anything else
setup_logging()
logger = get_logger(__name__)


def get_credentials() -> tuple[str, str]:
    """Read API key/secret from env vars or prompt the user."""
    api_key = os.environ.get("BINANCE_API_KEY", "").strip()
    api_secret = os.environ.get("BINANCE_API_SECRET", "").strip()

    if not api_key:
        api_key = input("Enter your Binance Testnet API Key: ").strip()
    if not api_secret:
        api_secret = input("Enter your Binance Testnet API Secret: ").strip()

    if not api_key or not api_secret:
        print("❌  API key and secret are required.")
        sys.exit(1)

    return api_key, api_secret


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trading_bot",
        description="🤖  Binance Futures Testnet Trading Bot",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("--symbol",     required=True,  help="Trading pair, e.g. BTCUSDT")
    parser.add_argument("--side",       required=True,  help="BUY or SELL")
    parser.add_argument("--type",       required=True,  dest="order_type", help="MARKET | LIMIT | STOP_MARKET")
    parser.add_argument("--quantity",   required=True,  help="Order quantity")
    parser.add_argument("--price",      default=None,   help="Limit price (required for LIMIT orders)")
    parser.add_argument("--stop-price", default=None,   dest="stop_price", help="Stop price (required for STOP_MARKET)")
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    # ── Validate inputs ──────────────────────────────────────────────────────
    try:
        symbol     = validate_symbol(args.symbol)
        side       = validate_side(args.side)
        order_type = validate_order_type(args.order_type)
        quantity   = validate_quantity(args.quantity)
        price      = validate_price(args.price, order_type)
        stop_price = validate_stop_price(args.stop_price, order_type)
    except ValidationError as e:
        print(f"\n❌  Validation Error: {e}\n")
        logger.error("Validation failed: %s", e)
        sys.exit(1)

    # ── Print order summary ──────────────────────────────────────────────────
    preview_params = build_order_params(symbol, side, order_type, quantity, price, stop_price)
    print()
    print(format_order_summary(preview_params))

    # ── Confirm before placing ───────────────────────────────────────────────
    confirm = input("\nProceed with this order? [y/N]: ").strip().lower()
    if confirm != "y":
        print("Order cancelled.")
        logger.info("Order cancelled by user.")
        sys.exit(0)

    # ── Get credentials & create client ─────────────────────────────────────
    api_key, api_secret = get_credentials()
    client = BinanceClient(api_key, api_secret)

    # ── Place the order ──────────────────────────────────────────────────────
    try:
        print("\n⏳  Placing order...")
        response = place_order(client, symbol, side, order_type, quantity, price, stop_price)
        print()
        print(format_order_response(response))
        print("\n✅  Order placed successfully!\n")

    except BinanceAPIError as e:
        print(f"\n❌  API Error: {e}\n")
        logger.error("API error placing order: %s", e)
        sys.exit(1)

    except NetworkError as e:
        print(f"\n❌  Network Error: {e}\n")
        logger.error("Network error placing order: %s", e)
        sys.exit(1)

    except Exception as e:
        print(f"\n❌  Unexpected error: {e}\n")
        logger.exception("Unexpected error: %s", e)
        sys.exit(1)

    finally:
        client.close()


if __name__ == "__main__":
    main()
