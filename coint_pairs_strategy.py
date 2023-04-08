from tqdm import tqdm

import pandas as pd
import vectorbt as vbt
import yfinance as yf

# Cointegration and Statistics
from statsmodels.tsa.stattools import coint
import statsmodels.api as sm

# Reporting visualization
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
import matplotlib.cm as cm

# ======================================
# tickers = [x['symbol']  for x in client.get_all_tickers()]
# tickers = ["BTC-USD", "DOGE-USD"]
no_of_days = 200
timeframe = "1h"
window = 20 # Z-Score Window size
# ======================================
# Functions

# Calculate cointegration
def calculate_cointegration(series_1, series_2):
    coint_flag = 0
    coint_res = coint(series_1, series_2)
    coint_t = coint_res[0]
    p_value = coint_res[1]
    critical_value = coint_res[2][1]
    model = sm.OLS(series_1, series_2).fit()
    hedge_ratio = model.params[0]
    coint_flag = 1 if p_value < 0.05 and coint_t < critical_value else 0
    return coint_flag, hedge_ratio
# ======================================


# Loading Data
def run_coint_backtest(tickers):
    data_df = pd.DataFrame(yf.download(tickers[0], period = str(no_of_days) + "d", interval = timeframe)['Close'])
    data_df.columns = [tickers[0]]

    for i in tqdm(range(len(tickers)-1)):
        data_df.insert(len(data_df.columns), tickers[i+1], pd.DataFrame(yf.download(tickers[i], period = str(no_of_days) + "d", interval = timeframe)['Close']), True)

    data_df.dropna()

    # Processing and Stuff
    asset_1_values = data_df[tickers[0]].values / data_df[tickers[0]].iloc[0].item()
    asset_2_values = data_df[tickers[1]].values / data_df[tickers[1]].iloc[0].item()

    series_1 = data_df[tickers[0]].values.astype(float)
    series_2 = data_df[tickers[1]].values.astype(float)
    coint_flag, hedge_ratio = calculate_cointegration(series_1, series_2)
    spread = series_1 - (hedge_ratio * series_2)

    ### Z-Score
    spread_series = pd.Series(spread)
    mean = spread_series.rolling(center=False, window=window).mean()
    std = spread_series.rolling(center=False, window=window).std()
    x = spread_series.rolling(center=False, window=1).mean()
    z_score = (x - mean) / std

    capped = []
    for z in z_score:
        z = 6 if z > 6 else z
        z = -6 if z <-6 else z
        capped.append(z)

    frame = {tickers[0]:data_df[tickers[0]], tickers[1]:data_df[tickers[1]]}
    df_save = pd.DataFrame(frame)
    df_save["Spread"] = spread
    df_save["ZScore"] = capped
    df_save.dropna(inplace=True)
    df_save.describe()

    # Generating Signals / Strategy
    entries_positive = [False]*len(df_save)
    exits_positive = [False]*len(df_save)

    entries_negative = [False]*len(df_save)
    exits_negative = [False]*len(df_save)

    for i in range(len(df_save)):
        if df_save.iloc[i]["ZScore"] >= 2.5:
            entries_positive[i] = True
        elif df_save.iloc[i]["ZScore"] <= 0.5:
            exits_positive[i] = True
        
        if df_save.iloc[i]["ZScore"] <= -2.5:
            entries_negative[i] = True
        elif df_save.iloc[i]["ZScore"] >= 0.5:
            exits_negative[i] = True

    
    # pf = vbt.Portfolio.from_signals(df_save[tickers[0]], [False]*len(df_save), [False]*len(df_save), entries_positive, exits_positive, init_cash = 1000, fees=0.001)
    # pf2 = vbt.Portfolio.from_signals(df_save[tickers[1]], entries_positive, exits_positive, init_cash = 1000, fees=0.001)

    pf  = vbt.Portfolio.from_signals(df_save[tickers[0]], 
                                        entries_negative, exits_negative, 
                                        entries_positive, exits_positive, 
                                        upon_long_conflict='entry',
                                        upon_short_conflict='entry',
                                        upon_dir_conflict='short',
                                        init_cash = 1000, fees=0.001)

    pf2 = vbt.Portfolio.from_signals(df_save[tickers[1]], 
                                        entries_positive, exits_positive, 
                                        entries_negative, exits_negative, 
                                        upon_long_conflict='entry',
                                        upon_short_conflict='entry',
                                        upon_dir_conflict='short',
                                        init_cash = 1000, fees=0.001)

    return pf, pf2