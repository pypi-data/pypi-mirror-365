from typing_extensions import Protocol, TypedDict, Literal
from trading_sdk.types import Side, Num

class BaseOrder(TypedDict):
  side: Side
  qty: Num
  """Quantity of the order in the base asset."""

class LimitOrder(BaseOrder):
  price: Num
  type: Literal['LIMIT']

class MarketOrder(BaseOrder):
  type: Literal['MARKET']

Order = LimitOrder | MarketOrder

class PlaceOrder(Protocol):
  async def place_order(self, symbol: str, order: Order) -> str:
    """Place an order.
    
    - `symbol`: The symbol to place the order for.
    - `order`: The order to place.

    Returns the order ID.
    """
    ...