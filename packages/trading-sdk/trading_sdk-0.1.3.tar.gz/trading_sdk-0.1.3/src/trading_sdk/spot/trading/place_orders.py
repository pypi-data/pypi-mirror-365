from typing_extensions import Sequence, Protocol
import asyncio
from .place_order import Order, PlaceOrder


class PlaceOrders(PlaceOrder, Protocol):
  async def place_orders(self, symbol: str, orders: Sequence[Order]) -> Sequence[str]:
    """Place multiple orders on a given symbol.
    
    - `symbol`: The symbol to place the orders for.
    - `orders`: The orders to place.

    Returns the order IDs.
    """
    return await asyncio.gather(*[self.place_order(symbol, order) for order in orders])