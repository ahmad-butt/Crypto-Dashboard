import numpy as np
import pandas as pd
import yfinance as yf
import datetime
import time
import ast
import datetime
from datetime import timedelta
import json
import math
import numpy as np
import pandas as pd
import plotly
import plotly.express as px
import plotly.graph_objects as go
import sys
import ta
import talib as ta_lib
import time
import vectorbt as vbt


@staticmethod
def get_crypto_data(symbol, interval, start, end):
    data = yf.download(tickers=symbol, start=start, end=end, interval=interval)
    filename = symbol+"_"+start+"_"+end+"_"+interval+"_interval.csv"
    data.to_csv(filename)
    return data


def filter_features(fileurl):
    data = pd.read_csv('./'+fileurl)
    print(data.shape)
    return data.columns.values


@staticmethod
def calculate_technical_indicators(indicators, fileurl):
    data = pd.read_csv('./'+fileurl)
    print(data.shape)

    open_prices = data["Open"]
    high_prices = data["High"]
    low_prices = data["Low"]
    close_prices = data["Close"]
    volume = data["Volume"]
    new_data = data
    for indicator in indicators:
        if indicator == 'rsi':
            calculate_rsi(open_prices, close_prices,
                          high_prices, low_prices, volume, data)
        elif indicator == 'mfi':
            calculate_mfi(open_prices, close_prices,
                          high_prices, low_prices, volume, data)
        elif indicator == 'bb':
            calculate_bb(open_prices, close_prices,
                         high_prices, low_prices, volume, data)
        elif indicator == 'ema':
            calculate_ema(open_prices, close_prices,
                          high_prices, low_prices, volume, data)
        elif indicator == 'sma':
            new_data = calculate_sma(open_prices, close_prices,
                                     high_prices, low_prices, volume, data)
        elif indicator == 'wma':
            new_data = calculate_wma(open_prices, close_prices,
                                     high_prices, low_prices, volume, data)
        elif indicator == 'stochastic':
            new_data = calculate_stochastic(open_prices, close_prices,
                                            high_prices, low_prices, volume, data)
        elif indicator == 'macd':
            calculate_macd(open_prices, close_prices,
                           high_prices, low_prices, volume, data)
        else:
            continue
    return new_data


def calculate_sma(open_prices, close_prices, high_prices, low_prices, volume, data):
    data['sma'] = ta.trend.sma_indicator(close_prices, window=14)
    return data


def calculate_ema(open_prices, close_prices, high_prices, low_prices, volume, data):
    # TREND: EMA Exponential Moving Average (with different time windows)
    data['ema'] = ta.trend.ema_indicator(close_prices, window=28)
    data['ema_fast'] = ta.trend.ema_indicator(close_prices, window=14)
    data['ema_slow'] = ta.trend.ema_indicator(close_prices, window=50)
    return data


def calculate_wma(open_prices, close_prices, high_prices, low_prices, volume, data):
    # TREND: VMA Weighted Moving Average
    data['wma'] = ta.trend.wma_indicator(close_prices, window=14)
    return data


def calculate_stochastic(open_prices, close_prices, high_prices, low_prices, volume, data):
    # TREND: VMA Weighted Moving Average
    data['stoch'] = ta.momentum.stoch(
        high_prices, low_prices, close_prices, window=14, smooth_window=3)
    data['stoch_signal'] = ta.momentum.stoch_signal(
        high_prices, low_prices, close_prices, window=14, smooth_window=3)
    return data


def calculate_rsi(open_prices, close_prices, high_prices, low_prices, volume, data):
    data['rsi'] = ta.momentum.rsi(close_prices, window=14)
    return data


def calculate_mfi(open_prices, close_prices, high_prices, low_prices, volume, data):
    data['mfi'] = ta.volume.money_flow_index(
        high_prices, low_prices, close_prices, volume, window=14)
    return data


def calculate_bb(open_prices, close_prices, high_prices, low_prices, volume, data):
    # VOLATILITY: BB (Bollinger Bands)
    data["bb_low"] = ta.volatility.bollinger_lband(
        close_prices, window=14, window_dev=2)
    data["bb_high"] = ta.volatility.bollinger_hband(
        close_prices, window=14, window_dev=2)
    return data


def calculate_macd(open_prices, close_prices, high_prices, low_prices, volume, data):
    # TREND: MACD (Moving Average Convergence Divergence)
    data['macd'] = ta.trend.macd(close_prices, window_slow=26, window_fast=12)
    data['macd_diff'] = ta.trend.macd_diff(
        close_prices, window_slow=26, window_fast=12, window_sign=9)
    data['macd_signal'] = ta.trend.macd_signal(
        close_prices, window_slow=26, window_fast=12, window_sign=9)


class Rule:
    ticker1: str
    ticker2: str
    constant1: int
    constant2: int
    lag: int
    relation: int
    kind: str

    def __init__(self, t1, t2, c1, c2, l, r, k):
        self.ticker1 = t1
        self.ticker2 = t2
        self.constant1 = c1
        self.constant2 = c2
        self.lag = l
        self.relation = r
        self.kind = k
