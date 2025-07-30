from typing_extensions import Protocol, TypeVar, Mapping
from dataclasses import dataclass
from decimal import Decimal

S = TypeVar('S', bound=str)

@dataclass
class Info:
  base_asset: str
  """Code of the base asset."""
  quote_asset: str
  """Code of the quote asset."""
  tick_size: Decimal
  """Tick size of the price (in quote units)."""
  step_size: Decimal
  """Step size of the quantity (in base units)."""
  min_qty: Decimal | None = None
  """Minimum quantity of the order (in base units)."""
  max_qty: Decimal | None = None
  """Maximum quantity of the order (in base units)."""
  min_price: Decimal | None = None
  """Minimum price of the order (in quote units)."""
  max_price: Decimal | None = None
  """Maximum price of the order (in quote units)."""

class ExchangeInfo(Protocol):
  async def exchange_info(self, symbol: str) -> Info:
    """Get the exchange info for the given symbol."""
    return (await self.exchange_infos(symbol))[symbol]

  async def exchange_infos(self, *symbols: S) -> Mapping[S, Info]:
    """Get the exchange info for the given symbols."""
    ...