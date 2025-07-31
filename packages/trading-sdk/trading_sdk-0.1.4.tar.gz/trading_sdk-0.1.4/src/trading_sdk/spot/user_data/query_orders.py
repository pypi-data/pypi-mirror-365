import asyncio
from typing_extensions import Sequence, Protocol
from .query_order import QueryOrder, OrderState

class QueryOrders(QueryOrder, Protocol):
  async def query_orders(self, symbol: str, *, ids: Sequence[str]) -> Sequence[OrderState]:
    """Query multiple orders by symbol and ID.
    
    - `symbol`: The symbol to query orders for.
    - `ids`: The IDs of the orders to query.

    Returns the states of the orders.
    """
    return await asyncio.gather(*[self.query_order(symbol, id=id) for id in ids])