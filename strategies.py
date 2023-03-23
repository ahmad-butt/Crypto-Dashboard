import alpaca_trade_api as tradeapi
from alpaca_trade_api.rest import TimeFrame
import datetime
from datetime import timedelta
import math
import numpy as np
import pandas as pd
import sys
import ta
import talib as ta_lib
import time
import vectorbt as vbt
import warnings
warnings.filterwarnings('ignore')

# SuperAI Trading Bot
# replace it with your own KEY_ID from Alpaca: https://alpaca.markets/
APCA_API_BASE_URL = "https://paper-api.alpaca.markets"
KEY_ID = "PKFL3UGA4W9NFZMR9XGA"
# replace it with your own SECRET_KEY from Alpaca
SECRET_KEY = "7TWgwlviKE0NHkxrkDBzJL7A5GetkHAEoBVNhDed"

(asset, asset_type, rounding) = ("BTCUSD", "crypto", 0)

# SuperAI Trading Bot
api = tradeapi.REST(KEY_ID, SECRET_KEY, APCA_API_BASE_URL, "v2")

# SuperAI Trading Bot
vbt.settings.data['alpaca']['key_id'] = KEY_ID
vbt.settings.data['alpaca']['secret_key'] = SECRET_KEY

# SuperAI Trading Bot
# replace with preferable time between data: 1m, 5m, 15m, 30m, 1h, 1d
data_timeframe = '1m'
# replace with the limit of the data to download to speed up the process (500, 1000, None)
data_limit = None

crypto_data_timeframe = TimeFrame.Minute
preferred_exchange = "CBSE"

data_start = '2022-05-30'  # replace with the starting point for collecting data
data_end = '2022-06-06'  # replace with the ending point for collecting the data

# SuperAI Trading Bot
# you can unhash it if you have numba installed and imported and the bot should work a little faster, if you use njit


@staticmethod
def run_backtest():
    def create_signal(open_prices, high_prices, low_prices, close_prices, volume,
                      buylesstime, selltime,  # Time to abstain from buying and forced selling
                      ma, ma_fast, ma_slow,  # Moving Average
                      macd, macd_diff, macd_sign,  # Moving Average Convergence Divergence
                      rsi, rsi_entry, rsi_exit,  # Relative Strength Index
                      stoch, stoch_signal, stoch_entry, stoch_exit,  # Stochastic
                      bb_low, bb_high,  # Bollinger Bands
                      mfi, mfi_entry, mfi_exit,  # Money Flow Index
                      candle_buy_signal_1, candle_buy_signal_2, candle_buy_signal_3,  # Candle signals to buy
                      # Candle signals to sell
                      candle_sell_signal_1, candle_sell_signal_2, candle_sell_signal_3,
                      candle_buy_sell_signal_1, candle_buy_sell_signal_2):  # Candle signals to buy or sell

        SuperAI_signal_buy = np.where(
            (buylesstime != 1)
            &
            (
                (
                    ((ma_fast < ma_slow) & (rsi < rsi_entry))
                    |
                    (close_prices < bb_low)
                    |
                    (mfi < mfi_entry)
                    # |
                    #(close_prices > ma)
                    # |
                    #(macd < 0)
                    # |
                    #(macd_diff < 0)
                    # |
                    #(macd_sign < macd)
                    # |
                    #(stoch < stoch_entry)
                    # |
                    #(stoch_signal < stoch_entry)
                    # |
                    #((close_prices > ma) & (ma_fast > ma_slow))
                    # |
                    #(((rsi < rsi_entry) & ((close_prices < ma) | (macd < 0))))
                    # |
                    #((close_prices > ma) & (shifted(close_prices, 1) < ma))
                    # |
                    # ((stoch < stoch_entry) & (
                    # (ma > (shifted(ma, 1))) &
                    #   (shifted(ma, 1) > (shifted(ma, 2)))))
                    # |
                    # ((rsi < rsi_entry) & (
                    # ~((ma > (shifted(ma, 2) * 1.01)) &
                    #   (shifted(ma, 2) > (shifted(ma, 4)*1.01)))))
                )
                |
                ((candle_buy_signal_1 > 0) | (candle_buy_signal_2 > 0) | (candle_buy_signal_3 > 0)
                 | (candle_buy_sell_signal_1 > 0) | (candle_buy_sell_signal_2 > 0))
            ), 1, 0)  # 1 is buy, -1 is sell, 0 is do nothing
        SuperAI_signal = np.where(
            (selltime == 1)
            # |
            #(ma_fast > ma_slow)
            |
            (rsi > rsi_exit)
            |
            (close_prices > bb_high)
            |
            (mfi > mfi_exit)
            # |
            #(close_prices < ma)
            # |
            #(macd_diff > 0)
            # |
            #(macd_sign > macd)
            # |
            #(stoch > stoch_exit)
            # |
            #(stoch_signal > stoch_exit)
            # |
            #((close_prices < ma) & (rsi > rsi_exit))
            # |
            #(((rsi > rsi_exit) & ((close_prices < ma) | (macd > 3))))
            # |
            #((close_prices < ma) & (shifted(close_prices, 1) > ma))
            # |
            # ((stoch > stoch_exit) & (
            # (ma > (shifted(ma, 1))) &
            #   (shifted(ma, 1) > (shifted(ma, 2)))))
            |
            ((candle_sell_signal_1 < 0) | (candle_sell_signal_2 < 0) | (candle_buy_signal_3 < 0)
             | (candle_buy_sell_signal_1 < 0) | (candle_buy_sell_signal_2 < 0)), -1, SuperAI_signal_buy)  # 1 is buy, -1 is sell, 0 is do nothing
        return SuperAI_signal

    # SuperAI Trading Bot
    take_profit_percent = 0.05  # 5%
    stop_loss_percent = 0.001  # 0.1%

    # SuperAI Trading Bot

    def trading_buy_sell_time():
        if asset_type == 'stock':
            # more about trading hours at: https://alpaca.markets/docs/trading/orders/#extended-hours-trading
            trading_hour_start = "09:30"
            trading_hour_stop = "16:00"
            # time when you don't want to buy at the beginning of the day
            buyless_time_start_1 = "09:30"
            buyless_time_end_1 = "09:45"
            buyless_time_start_2 = "15:55"
            buyless_time_end_2 = "16:00"
            # time when you want to sell by the end of the day
            selltime_start = "15:55"
            selltime_end = "16:00"

        elif asset_type == 'crypto':
            trading_hour_start = "00:00"
            trading_hour_stop = "23:59"
            # time when you don't want to buy at the beginning of the day
            buyless_time_start_1 = "23:59"
            buyless_time_end_1 = "00:01"
            buyless_time_start_2 = "23:58"
            buyless_time_end_2 = "23:59"
            # time when you want to sell by the end of the day
            selltime_start = "23:59"
            selltime_end = "00:00"
        return (trading_hour_start, trading_hour_stop,
                buyless_time_start_1, buyless_time_end_1, buyless_time_start_2, buyless_time_end_2,
                selltime_start, selltime_end)

    # SuperAI Trading Bot
    (trading_hour_start, trading_hour_stop,
     buyless_time_start_1, buyless_time_end_1, buyless_time_start_2, buyless_time_end_2,
     selltime_start, selltime_end) = trading_buy_sell_time()

    (trading_hour_start, trading_hour_stop,
     buyless_time_start_1, buyless_time_end_1, buyless_time_start_2, buyless_time_end_2,
     selltime_start, selltime_end)

    # SuperAI Trading Bot
    # helper function to shift data in order to test differences between data from x min and data from x-time min

    def shifted(data, shift_window):
        data_shifted = np.roll(data, shift_window)
        if shift_window >= 0:
            data_shifted[:shift_window] = np.NaN
        elif shift_window < 0:
            data_shifted[shift_window:] = np.NaN
        return data_shifted

    # SuperAI Trading Bot
    # Moving Average
    ma_timeframe = 28
    ma_fast_timeframe = 14
    ma_slow_timeframe = 50

    # SuperAI Trading Bot
    # Moving Average Convergence Divergence
    macd_slow_timeframe = 26
    macd_fast_timeframe = 12
    macd_signal_timeframe = 9

    # SuperAI Trading Bot
    # Relative Strength Index
    rsi_timeframe = 14
    rsi_oversold_threshold = 30
    rsi_overbought_threshold = 70

    # SuperAI Trading Bot
    # Stochastic Indicator
    stoch_timeframe = 14
    stoch_smooth_timeframe = 3
    stoch_oversold_threshold = 20
    stoch_overbought_threshold = 80

    # SuperAI Trading Bot
    # Bollinger Bands
    bb_timeframe = 10
    bb_dev = 2

    # SuperAI Trading Bot
    # Money Flow Index
    mfi_timeframe = 14
    mfi_oversold_threshold = 20
    mfi_overbought_threshold = 80

    # SuperAI Trading Bot
    ma_window = ma_timeframe
    ma_fast_window = ma_fast_timeframe
    ma_slow_window = ma_slow_timeframe
    macd_slow_window = macd_slow_timeframe
    macd_fast_window = macd_fast_timeframe
    macd_sign_window = macd_signal_timeframe
    rsi_window = rsi_timeframe
    rsi_entry = rsi_oversold_threshold
    rsi_exit = rsi_overbought_threshold
    stoch_window = stoch_timeframe
    stoch_smooth_window = stoch_smooth_timeframe
    stoch_entry = stoch_oversold_threshold
    stoch_exit = stoch_overbought_threshold
    bb_window = bb_timeframe
    bb_dev = bb_dev
    mfi_window = mfi_timeframe
    mfi_entry = mfi_oversold_threshold
    mfi_exit = mfi_overbought_threshold

    # SuperAI Trading Bot
    (ma_window_max, ma_fast_window_max, ma_slow_window_max,
     macd_slow_window_max, macd_fast_window_max, macd_sign_window_max,
     rsi_window_max, rsi_entry_max, rsi_exit_max,
     stoch_window_max, stoch_smooth_window_max, stoch_entry_max, stoch_exit_max,
     bb_window_max, bb_dev_max, mfi_window_max,
     mfi_entry_max, mfi_exit_max) = (ma_window, ma_fast_window, ma_slow_window,
                                     macd_slow_window, macd_fast_window, macd_sign_window,
                                     rsi_window, rsi_entry, rsi_exit,
                                     stoch_window, stoch_smooth_window, stoch_entry, stoch_exit,
                                     bb_window, bb_dev, mfi_window,
                                     mfi_entry, mfi_exit)

    (ma_window_max, ma_fast_window_max, ma_slow_window_max,
     macd_slow_window_max, macd_fast_window_max, macd_sign_window_max,
     rsi_window_max, rsi_entry_max, rsi_exit_max,
     stoch_window_max, stoch_smooth_window_max, stoch_entry_max, stoch_exit_max,
     bb_window_max, bb_dev_max, mfi_window_max,
     mfi_entry_max, mfi_exit_max)

    # SuperAI Trading Bot
    # preparing data in one function

    def prepare_data(start_date, end_date):
        data_start = start_date
        data_end = end_date

        crypto_data = api.get_crypto_bars(
            asset, crypto_data_timeframe, start=data_start, end=data_end).df
        full_crypto_data = crypto_data[crypto_data['exchange']
                                       == preferred_exchange]
        full_data = full_crypto_data.rename(str.capitalize, axis=1).drop(
            ["Exchange", "Trade_count", "Vwap"], axis=1)

        full_data.index = full_data.index.tz_convert('America/New_York')

        (trading_hour_start, trading_hour_stop,
         buyless_time_start_1, buyless_time_end_1, buyless_time_start_2, buyless_time_end_2,
         selltime_start, selltime_end) = trading_buy_sell_time()

        data = full_data.copy()
        data = data.between_time(trading_hour_start, trading_hour_stop)

        not_time_to_buy_1 = data.index.indexer_between_time(
            buyless_time_start_1, buyless_time_end_1)
        not_time_to_buy_2 = data.index.indexer_between_time(
            buyless_time_start_2, buyless_time_end_2)
        not_time_to_buy = np.concatenate(
            (not_time_to_buy_1, not_time_to_buy_2), axis=0)
        not_time_to_buy = np.unique(not_time_to_buy)
        data["NotTimeToBuy"] = 1
        data["BuylessTime"] = data.iloc[not_time_to_buy, 5]
        data["BuylessTime"] = np.where(
            np.isnan(data["BuylessTime"]), 0, data["BuylessTime"])
        data = data.drop(["NotTimeToBuy"], axis=1)

        time_to_sell = data.index.indexer_between_time(
            selltime_start, selltime_end)

        data["TimeToSell"] = 1
        data["SellTime"] = data.iloc[time_to_sell, 6]
        data["SellTime"] = np.where(
            np.isnan(data["SellTime"]), 0, data["SellTime"])
        data = data.drop(["TimeToSell"], axis=1)

        open_prices = data["Open"]
        high_prices = data["High"]
        low_prices = data["Low"]
        close_prices = data["Close"]
        volume = data["Volume"]
        buylesstime = data["BuylessTime"]
        selltime = data["SellTime"]

        return open_prices, high_prices, low_prices, close_prices, volume, buylesstime, selltime

    #open_prices, high_prices, low_prices, close_prices, volume, buylesstime, selltime = prepare_data(data_start, data_end)

    full_data = vbt.AlpacaData.download(
        asset, start=data_start, end=data_end, timeframe=data_timeframe, limit=data_limit).get()

    full_data.index = full_data.index.tz_convert('America/New_York')

    data = full_data.copy()
    data = data.between_time(trading_hour_start, trading_hour_stop)

    not_time_to_buy_1 = data.index.indexer_between_time(
        buyless_time_start_1, buyless_time_end_1)
    not_time_to_buy_2 = data.index.indexer_between_time(
        buyless_time_start_2, buyless_time_end_2)
    not_time_to_buy = np.concatenate(
        (not_time_to_buy_1, not_time_to_buy_2), axis=0)
    not_time_to_buy = np.unique(not_time_to_buy)

    data["NotTimeToBuy"] = 1
    data["BuylessTime"] = data.iloc[not_time_to_buy, 5]
    data["BuylessTime"] = np.where(
        np.isnan(data["BuylessTime"]), 0, data["BuylessTime"])
    data = data.drop(["NotTimeToBuy"], axis=1)

    time_to_sell = data.index.indexer_between_time(
        selltime_start, selltime_end)

    data["TimeToSell"] = 1
    data["SellTime"] = data.iloc[time_to_sell, 6]
    data["SellTime"] = np.where(
        np.isnan(data["SellTime"]), 0, data["SellTime"])
    data = data.drop(["TimeToSell"], axis=1)

    open_prices = data["Open"]
    high_prices = data["High"]
    low_prices = data["Low"]
    close_prices = data["Close"]
    volume = data["Volume"]
    buylesstime = data["BuylessTime"]
    selltime = data["SellTime"]

    # CandleStick Patterns Signals

    # candle buy signal 'Hammer'
    data["c_buy_1"] = ta_lib.CDLHAMMER(
        open_prices, high_prices, low_prices, close_prices)

    # candle buy signal 'Morning Star'
    data["c_buy_2"] = ta_lib.CDLMORNINGSTAR(
        open_prices, high_prices, low_prices, close_prices)

    # candle buy signal '3 White Soldiers'
    data["c_buy_3"] = ta_lib.CDL3WHITESOLDIERS(
        open_prices, high_prices, low_prices, close_prices)

    # candle sell signal 'Shooting Star'
    data["c_sell_1"] = ta_lib.CDLSHOOTINGSTAR(
        open_prices, high_prices, low_prices, close_prices)

    # candle sell signal 'Evening Star'
    data["c_sell_2"] = ta_lib.CDLEVENINGSTAR(
        open_prices, high_prices, low_prices, close_prices)

    # candle sell signal '3 Black Crows'
    data["c_sell_3"] = ta_lib.CDL3BLACKCROWS(
        open_prices, high_prices, low_prices, close_prices)

    # candle buy/sell signal 'Engulfing Bullish / Bearish'
    data["c_bs_1"] = ta_lib.CDLENGULFING(
        open_prices, high_prices, low_prices, close_prices)

    # candle buy/sell signal '3 Outside Up / Down'
    data["c_bs_2"] = ta_lib.CDL3OUTSIDE(
        open_prices, high_prices, low_prices, close_prices)

    def superai_signals(open_prices, high_prices, low_prices, close_prices, volume, buylesstime, selltime,
                        ma_window=ma_timeframe,
                        ma_fast_window=ma_fast_timeframe,
                        ma_slow_window=ma_slow_timeframe,
                        macd_slow_window=macd_slow_timeframe,
                        macd_fast_window=macd_fast_timeframe,
                        macd_sign_window=macd_signal_timeframe,
                        rsi_window=rsi_timeframe,
                        rsi_entry=rsi_oversold_threshold,
                        rsi_exit=rsi_overbought_threshold,
                        stoch_window=stoch_timeframe,
                        stoch_smooth_window=stoch_smooth_timeframe,
                        stoch_entry=stoch_oversold_threshold,
                        stoch_exit=stoch_overbought_threshold,
                        bb_window=bb_timeframe,
                        bb_dev=bb_dev,
                        mfi_window=mfi_timeframe,
                        mfi_entry=mfi_oversold_threshold,
                        mfi_exit=mfi_overbought_threshold):

        rsi = vbt.IndicatorFactory.from_ta('RSIIndicator').run(
            close_prices, window=rsi_window).rsi.to_numpy()

        stoch = vbt.IndicatorFactory.from_ta('StochasticOscillator').run(
            high_prices, low_prices, close_prices, window=stoch_window, smooth_window=stoch_smooth_window).stoch.to_numpy()
        stoch_signal = vbt.IndicatorFactory.from_ta('StochasticOscillator').run(
            high_prices, low_prices, close_prices, window=stoch_window,
            smooth_window=stoch_smooth_window).stoch_signal.to_numpy()

        ma = vbt.IndicatorFactory.from_ta('EMAIndicator').run(
            close_prices, window=ma_window).ema_indicator.to_numpy()
        ma_fast = vbt.IndicatorFactory.from_ta('EMAIndicator').run(
            close_prices, window=ma_fast_window).ema_indicator.to_numpy()
        ma_slow = vbt.IndicatorFactory.from_ta('EMAIndicator').run(
            close_prices, window=ma_slow_window).ema_indicator.to_numpy()

        macd = vbt.IndicatorFactory.from_ta('MACD').run(
            close_prices, window_slow=macd_slow_window, window_fast=macd_fast_window,
            window_sign=macd_sign_window).macd.to_numpy()
        macd_diff = vbt.IndicatorFactory.from_ta('MACD').run(
            close_prices, macd_slow_window, window_fast=macd_fast_window,
            window_sign=macd_sign_window).macd_diff.to_numpy()
        macd_sign = vbt.IndicatorFactory.from_ta('MACD').run(
            close_prices, macd_slow_window, window_fast=macd_fast_window,
            window_sign=macd_sign_window).macd_signal.to_numpy()

        bb_low = vbt.IndicatorFactory.from_ta('BollingerBands').run(
            close_prices, window=bb_window, window_dev=bb_dev).bollinger_lband.to_numpy()
        bb_high = vbt.IndicatorFactory.from_ta('BollingerBands').run(
            close_prices, window=bb_window, window_dev=bb_dev).bollinger_hband.to_numpy()

        mfi = vbt.IndicatorFactory.from_ta('MFIIndicator').run(
            high_prices, low_prices, close_prices, volume, window=mfi_timeframe).money_flow_index.to_numpy()

        candle_buy_signal_1 = vbt.IndicatorFactory.from_talib('CDLHAMMER').run(
            open_prices, high_prices, low_prices, close_prices).integer.to_numpy()  # 'Hammer'
        candle_buy_signal_2 = vbt.IndicatorFactory.from_talib('CDLMORNINGSTAR').run(
            open_prices, high_prices, low_prices, close_prices).integer.to_numpy()  # 'Morning star'
        candle_buy_signal_3 = vbt.IndicatorFactory.from_talib('CDL3WHITESOLDIERS').run(
            open_prices, high_prices, low_prices, close_prices).integer.to_numpy()  # 'Three White Soldiers'
        candle_sell_signal_1 = vbt.IndicatorFactory.from_talib('CDLSHOOTINGSTAR').run(
            open_prices, high_prices, low_prices, close_prices).integer.to_numpy()  # 'Shooting star'
        candle_sell_signal_2 = vbt.IndicatorFactory.from_talib('CDLEVENINGSTAR').run(
            open_prices, high_prices, low_prices, close_prices).integer.to_numpy()  # 'Evening star'
        candle_sell_signal_3 = vbt.IndicatorFactory.from_talib('CDL3BLACKCROWS').run(
            open_prices, high_prices, low_prices, close_prices).integer.to_numpy()  # '3 Black Crows'
        candle_buy_sell_signal_1 = vbt.IndicatorFactory.from_talib('CDLENGULFING').run(
            open_prices, high_prices, low_prices, close_prices).integer.to_numpy()  # 'Engulfing: Bullish (buy) / Bearish (sell)'
        candle_buy_sell_signal_2 = vbt.IndicatorFactory.from_talib('CDL3OUTSIDE').run(
            open_prices, high_prices, low_prices, close_prices).integer.to_numpy()  # 'Three Outside: Up (buy) / Down (sell)'

        SuperAI_signal = create_signal(open_prices, high_prices, low_prices, close_prices, volume,
                                       buylesstime, selltime,
                                       ma, ma_fast, ma_slow,
                                       macd, macd_diff, macd_sign,
                                       rsi, rsi_entry, rsi_exit,
                                       stoch, stoch_signal, stoch_entry, stoch_exit,
                                       bb_low, bb_high,
                                       mfi, mfi_entry, mfi_exit,
                                       candle_buy_signal_1, candle_buy_signal_2, candle_buy_signal_3,
                                       candle_sell_signal_1, candle_sell_signal_2, candle_sell_signal_3,
                                       candle_buy_sell_signal_1, candle_buy_sell_signal_2)
        return SuperAI_signal

    parameters_names = ["ma_window", "ma_fast_window", "ma_slow_window",
                        "macd_slow_window", "macd_fast_window", "macd_sign_window",
                        "rsi_window", "rsi_entry", "rsi_exit",
                        "stoch_window", "stoch_smooth_window", "stoch_entry", "stoch_exit",
                        "bb_window", "bb_dev",
                        "mfi_window", "mfi_entry", "mfi_exit"]

    SuperAI_Ind = vbt.IndicatorFactory(
        class_name="SuperAI_Ind",
        short_name="SuperInd",
        input_names=["open", "high", "low", "close",
                     "volume", "buylesstime", "selltime"],
        param_names=parameters_names,
        output_names=["output"]).from_apply_func(superai_signals,
                                                 ma_window=ma_timeframe,
                                                 ma_fast_window=ma_fast_timeframe,
                                                 ma_slow_window=ma_slow_timeframe,

                                                 macd_slow_window=macd_slow_timeframe,
                                                 macd_fast_window=macd_fast_timeframe,
                                                 macd_sign_window=macd_signal_timeframe,

                                                 rsi_window=rsi_timeframe,
                                                 rsi_entry=rsi_oversold_threshold,
                                                 rsi_exit=rsi_overbought_threshold,

                                                 stoch_window=stoch_timeframe,
                                                 stoch_smooth_window=stoch_smooth_timeframe,
                                                 stoch_entry=stoch_oversold_threshold,
                                                 stoch_exit=stoch_overbought_threshold,

                                                 bb_window=bb_timeframe,
                                                 bb_dev=bb_dev,

                                                 mfi_window=mfi_timeframe,
                                                 mfi_entry=mfi_oversold_threshold,
                                                 mfi_exit=mfi_overbought_threshold)

    open_prices, high_prices, low_prices, close_prices, volume, buylesstime, selltime = prepare_data(
        data_start, data_end)

    trading_signals = SuperAI_Ind.run(open_prices, high_prices, low_prices, close_prices, volume, buylesstime, selltime,

                                      ma_window=ma_timeframe,
                                      ma_fast_window=ma_fast_timeframe,
                                      ma_slow_window=ma_slow_timeframe,

                                      macd_slow_window=macd_slow_timeframe,
                                      macd_fast_window=macd_fast_timeframe,
                                      macd_sign_window=macd_signal_timeframe,

                                      rsi_window=rsi_timeframe,
                                      rsi_entry=rsi_oversold_threshold,
                                      rsi_exit=rsi_overbought_threshold,

                                      stoch_window=stoch_timeframe,
                                      stoch_smooth_window=stoch_smooth_timeframe,
                                      stoch_entry=stoch_oversold_threshold,
                                      stoch_exit=stoch_overbought_threshold,

                                      bb_window=bb_timeframe,
                                      bb_dev=bb_dev,

                                      mfi_window=mfi_timeframe,
                                      mfi_entry=mfi_oversold_threshold,
                                      mfi_exit=mfi_overbought_threshold,

                                      param_product=True)

    entries = trading_signals.output == 1.0
    exits = trading_signals.output == -1.0

    SuperAI_portfolio = vbt.Portfolio.from_signals(close_prices,
                                                   entries,
                                                   exits,
                                                   init_cash=100000,
                                                   tp_stop=take_profit_percent,
                                                   sl_stop=stop_loss_percent,
                                                   fees=0.00)

    return SuperAI_portfolio
