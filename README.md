# 🤖 Binance Futures Testnet Trading Bot

A lightweight Python CLI application to place orders on the **Binance Futures Testnet (USDT-M)** with structured logging and clean error handling.

---

## Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py
│   ├── client.py          # Binance HTTP client (signing, requests)
│   ├── orders.py          # Order building, placement, formatting
│   ├── validators.py      # CLI input validation
│   └── logging_config.py  # Rotating file + console logging
├── cli.py                 # CLI entry point (argparse)
├── logs/
│   └── trading_bot.log    # Auto-created on first run
├── requirements.txt
└── README.md
```

---

## Setup

### 1. Create a Binance Futures Testnet account

1. Go to [https://testnet.binancefuture.com](https://testnet.binancefuture.com)
2. Sign in with GitHub and generate API credentials under **API Key Management**

### 2. Clone and install

```bash
git clone <your-repo-url>
cd trading_bot
pip install -r requirements.txt
```

### 3. Set your credentials

**Option A — Environment variables (recommended):**
```bash
export BINANCE_API_KEY=your_api_key_here
export BINANCE_API_SECRET=your_api_secret_here
```

**Option B — Interactive prompt:**  
Leave the env vars unset; the bot will prompt you at runtime.

---

## How to Run

### MARKET order (BUY)
```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

### LIMIT order (SELL)
```bash
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 85000
```

### STOP_MARKET order (bonus) — acts as a stop-loss
```bash
python cli.py --symbol BTCUSDT --side SELL --type STOP_MARKET --quantity 0.001 --stop-price 80000
```

### All available flags
```
--symbol        Trading pair (e.g. BTCUSDT, ETHUSDT)
--side          BUY or SELL
--type          MARKET | LIMIT | STOP_MARKET
--quantity      Order size in base asset
--price         Required for LIMIT orders
--stop-price    Required for STOP_MARKET orders
```

---

## Example Output

```
┌─── Order Request Summary ──────────────────┐
  Symbol     : BTCUSDT
  Side       : BUY
  Type       : MARKET
  Quantity   : 0.001
└────────────────────────────────────────────┘

Proceed with this order? [y/N]: y

⏳  Placing order...

┌─── Order Response ─────────────────────────┐
  Order ID   : 4751839201
  Status     : FILLED
  Exec Qty   : 0.001
  Avg Price  : 83412.50
  Client OID : bot_x7k2m
  Time       : 1743498903891
└────────────────────────────────────────────┘

✅  Order placed successfully!
```

---

## Logging

All activity is written to `logs/trading_bot.log`:
- **DEBUG+**: full request params, raw API responses
- **INFO**: order lifecycle events
- **ERROR**: validation failures, API errors, network issues

Log files rotate at 5 MB (keeps 3 backups). Sample log files for a MARKET order, LIMIT order, and STOP_MARKET order are included in `logs/`.

---

## Assumptions

- All orders are placed in **USDT-M perpetual futures** (not spot)
- Default `timeInForce` for LIMIT orders is `GTC` (Good Till Cancelled)
- No leverage management is done in the bot — set leverage on the testnet dashboard or extend `client.py` with the `/fapi/v1/leverage` endpoint
- Quantity precision must match the symbol's `stepSize` — use values the testnet accepts (e.g. `0.001` for BTCUSDT)

---

## Dependencies

| Package | Purpose |
|---------|---------|
| `httpx` | Async-ready HTTP client for REST calls |

No third-party Binance SDK is used — all API interactions are raw REST calls with HMAC-SHA256 signing.
