"""
Detection of bull and bear markets.
"""
import numpy as np
import pandas as pd
from pandas.tseries.offsets import DateOffset
from scipy.signal import argrelextrema


def pagan_sossounov(prices: pd.DataFrame, window=8, censor=6, cycle=16, phase=4, threshold=0.2):
    """
    Pagan and Sossounov's labeling method. Sourced from `Pagan, Adrian R., and Kirill A. Sossounov. "A simple framework
    for analysing bull and bear markets." Journal of applied econometrics 18.1 (2003): 23-46.
    <https://onlinelibrary.wiley.com/doi/pdf/10.1002/jae.664>`__

    Returns a DataFrame with labels of 1 for Bull and -1 for Bear.

    :param prices: (pd.DataFrame) Close prices of all tickers in the market. Assumed to have a DatetimeIndex
                   with a frequency (e.g., monthly).
    :param window: (int) Rolling window length to determine local extrema. Paper suggests 8 months for monthly obs.
    :param censor: (int) Number of months to eliminate for start and end. Paper suggests 6 months for monthly obs.
    :param cycle: (int) Minimum length for a complete cycle. Paper suggests 16 months for monthly obs.
    :param phase: (int) Minimum length for a phase. Paper suggests 4 months for monthly obs.
    :param threshold: (double) Minimum threshold for phase change. Paper suggests 0.2.
    :return: (pd.DataFrame) Labeled pd.DataFrame. 1 for Bull, -1 for Bear.
    """
    if not isinstance(prices.index, pd.DatetimeIndex):
        raise ValueError("Input 'prices' DataFrame must have a DatetimeIndex.")

    result_df = pd.DataFrame(index=prices.index)
    for ticker in prices.columns:
        result_df[ticker] = _apply_pagan_sossounov(prices[ticker].dropna(), window, censor, cycle, phase, threshold)
    return result_df


def _alternation(tps: pd.DataFrame) -> pd.DataFrame:
    """
    Helper function to enforce peak and trough alternation.

    It iterates through a sorted list of turning points (TPs) and ensures that
    no two consecutive TPs are of the same type. If they are, it keeps the
    more extreme one (highest peak, lowest trough).

    :param tps: (pd.DataFrame) DataFrame of turning points with columns 'price' and 'type' ('P' or 'T').
    :return: (pd.DataFrame) A new DataFrame with strictly alternating TPs.
    """
    if tps.empty:
        return tps

    new_tps = [tps.iloc[0]]
    for i in range(1, len(tps)):
        current_tp = tps.iloc[i]
        last_tp = new_tps[-1]

        if current_tp["type"] == last_tp["type"]:
            if current_tp["type"] == "P" and current_tp["price"] > last_tp["price"]:
                new_tps[-1] = current_tp
            elif current_tp["type"] == "T" and current_tp["price"] < last_tp["price"]:
                new_tps[-1] = current_tp
        else:
            new_tps.append(current_tp)

    return pd.DataFrame(new_tps)


def _apply_pagan_sossounov(price: pd.Series, window, censor, cycle, phase, threshold):
    """
    Helper function for Pagan and Sossounov labeling method.

    :param price: (pd.Series) Close prices of a ticker.
    :param window: (int) Rolling window length to determine local extrema.
    :param censor: (int) Number of months to eliminate for start and end.
    :param cycle: (int) Minimum length for a complete cycle.
    :param phase: (int) Minimum length for a phase.
    :param threshold: (double) Minimum threshold for phase change.
    :return: (pd.Series) Labeled pd.Series. 1 for Bull, -1 for Bear.
    """
    log_price = np.log(price)

    # 1. Initial Turning Points
    peak_indices = argrelextrema(log_price.values, np.greater, order=window)[0]
    trough_indices = argrelextrema(log_price.values, np.less, order=window)[0]

    peaks = pd.DataFrame({"price": log_price.iloc[peak_indices], "type": "P"})
    troughs = pd.DataFrame({"price": log_price.iloc[trough_indices], "type": "T"})

    tps = pd.concat([peaks, troughs]).sort_index()

    # 2. Censoring
    if censor > 0 and len(price.index) > censor * 2:
        censor_start = price.index[0] + DateOffset(months=censor)
        censor_end = price.index[-1] - DateOffset(months=censor)
        tps = tps[(tps.index >= censor_start) & (tps.index <= censor_end)]

    if tps.empty:
        return pd.Series(np.nan, index=price.index)

    # 3. Iterative Filtering
    while True:
        start_len = len(tps)
        tps = _alternation(tps)

        # Enforce cycle length
        peaks, troughs = tps[tps["type"] == "P"], tps[tps["type"] == "T"]
        if len(peaks) > 1:
            peak_cycles = (peaks.index[1:] - peaks.index[:-1])
            short_cycles = peak_cycles < DateOffset(months=cycle)
            if np.any(short_cycles):
                idx = np.where(short_cycles)[0][0]
                p1_idx, p2_idx = peaks.index[idx], peaks.index[idx + 1]
                trough_between = tps.loc[p1_idx:p2_idx].query("type == 'T'")
                drop_indices = trough_between.index.tolist()
                drop_indices.append(p1_idx if peaks.loc[p1_idx].price < peaks.loc[p2_idx].price else p2_idx)
                tps = tps.drop(drop_indices)
                continue

        if len(troughs) > 1:
            trough_cycles = (troughs.index[1:] - troughs.index[:-1])
            short_cycles = trough_cycles < DateOffset(months=cycle)
            if np.any(short_cycles):
                idx = np.where(short_cycles)[0][0]
                t1_idx, t2_idx = troughs.index[idx], troughs.index[idx + 1]
                peak_between = tps.loc[t1_idx:t2_idx].query("type == 'P'")
                drop_indices = peak_between.index.tolist()
                drop_indices.append(t1_idx if troughs.loc[t1_idx].price > troughs.loc[t2_idx].price else t2_idx)
                tps = tps.drop(drop_indices)
                continue

        tps = _alternation(tps)
        if len(tps) < 2: break

        # Enforce phase length
        phase_lengths = (tps.index[1:] - tps.index[:-1])
        short_phases = phase_lengths < DateOffset(months=phase)
        if np.any(short_phases):
            idx = np.where(short_phases)[0][0]
            tps = tps.drop(tps.index[idx:idx + 2])
            continue

        if len(tps) == start_len: break

    # Enforce threshold
    if len(tps) > 1:
        amplitudes = tps["price"].diff().abs()
        small_amplitudes = amplitudes < np.log(1 + threshold)
        if np.any(small_amplitudes):
             idx_to_remove = np.where(small_amplitudes)[0][0]
             tps = tps.drop(tps.index[idx_to_remove-1:idx_to_remove+1])

    # 4. Create final labels
    labels = pd.Series(np.nan, index=price.index)
    if tps.empty: return labels

    for i in range(len(tps) - 1):
        start_date, end_date = tps.index[i], tps.index[i+1]
        regime = 1 if tps.iloc[i]["type"] == "T" else -1
        labels.loc[start_date:end_date] = regime

    # Determine first and last regimes
    first_tp_type = tps.iloc[0]["type"]
    first_regime = -1 if first_tp_type == "P" else 1
    labels.loc[:tps.index[0]] = first_regime

    last_tp_type = tps.iloc[-1]["type"]
    last_regime = 1 if last_tp_type == "T" else -1 # The regime *after* the last TP
    labels.loc[tps.index[-1]:] = last_regime


    return labels.ffill().bfill().astype(int)


def lunde_timmermann(prices: pd.DataFrame, bull_threshold=0.15, bear_threshold=0.15):
    """
    Lunde and Timmermann's labeling method. Sourced from `Lunde, Asger, and Allan Timmermann. "Duration dependence
    in stock prices: An analysis of bull and bear markets." Journal of Business & Economic Statistics 22.3 (2004): 253-273.
    <https://repec.cepr.org/repec/cpr/ceprdp/DP4104.pdf>`__

    Returns a DataFrame with labels of 1 for Bull and -1 for Bear.

    :param prices: (pd.DataFrame) Close prices of all tickers in the market.
    :param bull_threshold: (double) Threshold to identify bull market. Paper suggests 0.15.
    :param bear_threshold: (double) Threshold to identify bear market. Paper suggests 0.15.
    :return: (pd.DataFrame) Labeled pd.DataFrame. 1 for Bull, -1 for Bear.
    """
    result_df = pd.DataFrame(index=prices.index)
    for ticker in prices.columns:
        result_df[ticker] = _apply_lunde_timmermann(prices[ticker].dropna(), bull_threshold, bear_threshold)
    return result_df


def _apply_lunde_timmermann(price, bull_threshold, bear_threshold):
    """
    Helper function for Lunde and Timmermann labeling method.

    :param price: (pd.Series) Close prices of a ticker.
    :param bull_threshold: (double) Threshold to identify bull market. Paper suggests 0.15.
    :param bear_threshold: (double) Threshold to identify bear market. Paper suggests 0.15.
    :return: (pd.Series) Labeled pd.Series. 1 for Bull, -1 for Bear.
    """
    n = len(price)
    if n < 2:
        return pd.Series(np.nan, index=price.index)

    # 1. Find turning points
    tps = []

    # Initialize state
    current_regime = 1 if price.iloc[1] > price.iloc[0] else -1
    last_peak, last_trough = (price.iloc[0], price.iloc[0])
    last_peak_idx, last_trough_idx = (price.index[0], price.index[0])

    if current_regime == 1: # Initial move is up
        tps.append((last_trough_idx, "T"))
        last_peak = price.iloc[1]
        last_peak_idx = price.index[1]
    else: # Initial move is down
        tps.append((last_peak_idx, "P"))
        last_trough = price.iloc[1]
        last_trough_idx = price.index[1]

    for i in range(1, n):
        current_price = price.iloc[i]
        current_idx = price.index[i]

        if current_regime == 1:  # Bull Market
            if current_price > last_peak:
                last_peak, last_peak_idx = current_price, current_idx
            elif current_price < last_peak * (1 - bear_threshold):
                tps.append((last_peak_idx, "P"))
                current_regime = -1
                last_trough, last_trough_idx = current_price, current_idx
        else:  # Bear Market
            if current_price < last_trough:
                last_trough, last_trough_idx = current_price, current_idx
            elif current_price > last_trough * (1 + bull_threshold):
                tps.append((last_trough_idx, "T"))
                current_regime = 1
                last_peak, last_peak_idx = current_price, current_idx

    # 2. Generate labels from turning points
    labels = pd.Series(np.nan, index=price.index)
    if not tps:
        return labels

    for i in range(len(tps) - 1):
        start_date, tp_type = tps[i]
        end_date, _ = tps[i + 1]
        regime = 1 if tp_type == "T" else -1
        labels.loc[start_date:end_date] = regime

    # Label the last segment
    last_tp_date, last_tp_type = tps[-1]
    regime = 1 if last_tp_type == "T" else -1
    labels.loc[last_tp_date:] = regime

    return labels.ffill().bfill().astype(int)


