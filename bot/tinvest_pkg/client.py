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

def get_stocks():
    return client.get_market_stocks().payload.instruments

def load_stocks():
    return client.get_market_stocks().payload.instruments


def get_figi_by_ticker(ticker: str) -> str:
    if ticker == '':
        return ''
    payload = client.get_market_search_by_ticker(ticker)
    if len(payload.payload.instruments) >= 1:
        return payload.payload.instruments[0].figi
    return ''

def process_by_period(
    ticker: str,
    from_: datetime,
    to: datetime,
    interval: ti.CandleResolution,
 ):
    figi = get_figi_by_ticker(ticker)
    if figi == '':
        return []

    payload = client.get_market_candles(
        figi=figi,
        from_=from_,
        to=to,
        interval=interval,
    ).payload
    return payload.candles


def process_by_period_data_fram(
    ticker: str,
    from_: datetime,
    to: datetime,
    interval: ti.CandleResolution,
 ) -> pd.DataFrame:
    return pd.DataFrame(c.dict() for c in process_by_period(ticker, from_, to, interval))


def process_by_period_map(
    ticker: str,
    from_: datetime,
    to: datetime,
    interval: ti.CandleResolution,
 ):
    payload = process_by_period(ticker, from_, to, interval)
    m = {}
    for c in payload.candles:
        m[c.time] = c.c
    return m
