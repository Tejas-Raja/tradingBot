"""
Order placement logic — sits between the CLI and the Binance client.
"""

from bot.client import BinanceClient
from bot.logging_config import get_logger

logger = get_logger(__name__)


def build_order_params(
    symbol: str,
    side: str,
    order_type: str,
    quantity: str,
    price: str = None,
    stop_price: str = None,
    time_in_force: str = "GTC",
) -> dict:
    params = {
        "symbol": symbol,
        "side": side,
        "type": order_type,
        "quantity": quantity,
    }

    if order_type == "LIMIT":
        params["price"] = price
        params["timeInForce"] = time_in_force

    elif order_type == "STOP_MARKET":
        params["stopPrice"] = stop_price

    return params


def place_order(
    client: BinanceClient,
    symbol: str,
    side: str,
    order_type: str,
    quantity: str,
    price: str = None,
    stop_price: str = None,
) -> dict:
    """Build params and submit order; return parsed response."""
    params = build_order_params(symbol, side, order_type, quantity, price, stop_price)

    logger.info(
        "Placing %s %s order | symbol=%s qty=%s price=%s stop=%s",
        side, order_type, symbol, quantity, price or "-", stop_price or "-",
    )

    response = client.place_order(**params)
    logger.info("Order placed successfully | orderId=%s status=%s", response.get("orderId"), response.get("status"))
    return response


def format_order_summary(params: dict) -> str:
    lines = [
        "┌─── Order Request Summary ──────────────────┐",
        f"  Symbol     : {params.get('symbol')}",
        f"  Side       : {params.get('side')}",
        f"  Type       : {params.get('type')}",
        f"  Quantity   : {params.get('quantity')}",
    ]
    if params.get("price"):
        lines.append(f"  Price      : {params['price']}")
    if params.get("stopPrice"):
        lines.append(f"  Stop Price : {params['stopPrice']}")
    lines.append("└────────────────────────────────────────────┘")
    return "\n".join(lines)


def format_order_response(response: dict) -> str:
    lines = [
        "┌─── Order Response ─────────────────────────┐",
        f"  Order ID   : {response.get('orderId')}",
        f"  Status     : {response.get('status')}",
        f"  Exec Qty   : {response.get('executedQty', '0')}",
        f"  Avg Price  : {response.get('avgPrice', 'N/A')}",
        f"  Client OID : {response.get('clientOrderId', 'N/A')}",
        f"  Time       : {response.get('updateTime', 'N/A')}",
        "└────────────────────────────────────────────┘",
    ]
    return "\n".join(lines)
