from typing_extensions import Protocol, Literal
from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime
from trading_sdk.types import Side

OrderStatus = Literal['NEW', 'PARTIALLY_FILLED', 'FILLED', 'CANCELED', 'PARTIALLY_CANCELED']

@dataclass
class OrderState:
  id: str
  price: Decimal
  qty: Decimal
  filled_qty: Decimal
  time: datetime
  side: Side
  status: OrderStatus

  @property
  def quote_qty(self) -> Decimal:
    return self.qty * self.price

  @property
  def unfilled_qty(self) -> Decimal:
    return self.qty - self.filled_qty
  
class QueryOrder(Protocol):
  async def query_order(self, symbol: str, *, id: str) -> OrderState:
    """Query an order.
    
    - `symbol`: The symbol to query the order for.
    - `id`: The ID of the order to query.
    """
    ...