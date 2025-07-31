from typing_extensions import Protocol
from trading_sdk.spot.user_data.query_order import OrderState

class CancelOrder(Protocol):
  async def cancel_order(self, symbol: str, *, id: str) -> OrderState:
    """Cancel an order.
    
    - `symbol`: The symbol to cancel the order for.
    - `id`: The ID of the order to cancel.
    """
    ...