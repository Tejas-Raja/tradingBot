"""
Logging configuration for the trading bot.
Logs to both console (INFO+) and a rotating file (DEBUG+).
"""

import logging
import logging.handlers
import os

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "trading_bot.log")


def setup_logging():
    os.makedirs(LOG_DIR, exist_ok=True)

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    # --- File handler (DEBUG and above, rotating) ---
    file_handler = logging.handlers.RotatingFileHandler(
        LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(file_fmt)

    # --- Console handler (INFO and above, clean) ---
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_fmt = logging.Formatter("%(levelname)-8s %(message)s")
    console_handler.setFormatter(console_fmt)

    root.addHandler(file_handler)
    root.addHandler(console_handler)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
