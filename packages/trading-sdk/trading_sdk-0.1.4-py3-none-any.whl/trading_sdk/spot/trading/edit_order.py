from typing_extensions import Protocol
from trading_sdk.types import Num

class EditOrder(Protocol):
  async def edit_order(self, symbol: str, *, id: str, qty: Num) -> str:
    """Edit an existing order.
    
    - `symbol`: The symbol to edit the order for.
    - `id`: The ID of the order to edit.
    - `quantity`: The new quantity of the order.

    Returns the new ID of the order.
    """
    ...