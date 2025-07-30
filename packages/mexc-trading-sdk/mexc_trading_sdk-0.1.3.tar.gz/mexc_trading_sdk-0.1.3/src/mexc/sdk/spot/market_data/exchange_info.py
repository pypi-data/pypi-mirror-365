from dataclasses import dataclass
from decimal import Decimal
from trading_sdk.spot.market_data.exchange_info import ExchangeInfo as ExchangeInfoTDK, Info
from mexc.sdk import SdkMixin

@dataclass
class ExchangeInfo(ExchangeInfoTDK, SdkMixin):
  async def exchange_infos(self, *symbols: str) -> dict[str, Info]:
    r = await self.client.spot.exchange_info(*symbols)
    if 'code' in r:
      raise RuntimeError(r)
    else:
      return {
        k: Info(
          base_asset=v['baseAsset'],
          quote_asset=v['quoteAsset'],
          tick_size=Decimal(1) / Decimal(10 ** v['quotePrecision']),
          step_size=Decimal(v['baseSizePrecision']),
        ) for k, v in r.items()
      }
