from typing_extensions import Protocol, AsyncIterable
from trading_sdk.spot.user_data.my_trades import Trade

class MyTrades(Protocol):
  def my_trades(self, symbol: str) -> AsyncIterable[Trade]:
    ...