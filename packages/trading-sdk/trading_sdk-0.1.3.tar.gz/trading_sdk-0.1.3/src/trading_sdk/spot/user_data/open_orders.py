from typing_extensions import Protocol, Sequence
from .query_order import OrderState

class OpenOrders(Protocol):
  async def open_orders(self, symbol: str) -> Sequence[OrderState]:
    """Fetch currently open orders (of your account) on a given symbol.
    
    - `symbol`: The symbol being traded, e.g. `BTCUSDT`
    """
    ...