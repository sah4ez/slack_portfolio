"""Show portfolio candles.
    python -m examples.portfolio_candles
"""

import os

from datetime import datetime, timedelta
from typing import List, Tuple

import pandas as pd

import tinvest as ti

client = ti.SyncClient(os.getenv('TINVEST_TOKEN', ''))

# def main() -> None:
#     print(process_by_period("AAPL", datetime.now() - timedelta(days=31 * 12), datetime.now(), ti.CandleResolution.week))


def get_figi_by_ticker(ticker: str) -> str:
    return client.get_market_search_by_ticker("AAPL").payload.instruments[0].figi


def process_by_period(
    ticker: str,
    from_: datetime,
    to: datetime,
    interval: ti.CandleResolution,
 ) -> pd.DataFrame:
    payload = client.get_market_candles(
        figi=get_figi_by_ticker(ticker),
        from_=from_,
        to=to,
        interval=interval,
    ).payload
    return pd.DataFrame(c.dict() for c in payload.candles)
