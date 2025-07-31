from typing_extensions import Protocol, AsyncIterable
from trading_sdk.spot.market_data.depth import Book

class Depth(Protocol):
  def depth(self, symbol: str, *, limit: int | None = None) -> AsyncIterable[Book]:
    ...