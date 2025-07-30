from dataclasses import dataclass
from trading_sdk.spot.trading import PlaceOrders
from .place_order import PlaceOrder
from .edit_order import EditOrder

@dataclass
class Trading(PlaceOrder, PlaceOrders, EditOrder):
  ...