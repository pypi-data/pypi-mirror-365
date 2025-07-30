from typing_extensions import Protocol, Mapping, TypeVar
from dataclasses import dataclass
from decimal import Decimal

S = TypeVar('S', bound=str, default=str)

@dataclass
class Balance:
  free: Decimal
  locked: Decimal

  @property
  def total(self) -> Decimal:
    return self.free + self.locked

class Balances(Protocol):

  async def balance(self, currency: S, /) -> Balance:
    """Get the balance of the given currency."""
    return (await self.balances(currency))[currency]

  async def balances(self, *currencies: S) -> Mapping[S, Balance]:
    """Get the balances of the given currencies."""
    ...