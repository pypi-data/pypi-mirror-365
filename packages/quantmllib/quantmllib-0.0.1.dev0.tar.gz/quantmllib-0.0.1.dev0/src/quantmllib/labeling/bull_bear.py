"""
Detection of bull and bear markets.
"""
import numpy as np
import pandas as pd


def pagan_sossounov(prices: pd.DataFrame, window=8, censor=6, cycle=16, phase=4, threshold=0.2):
    """
    Pagan and Sossounov's labeling method. Sourced from `Pagan, Adrian R., and Kirill A. Sossounov. "A simple framework
    for analysing bull and bear markets." Journal of applied econometrics 18.1 (2003): 23-46.
    <https://onlinelibrary.wiley.com/doi/pdf/10.1002/jae.664>`__

    Returns a DataFrame with labels of 1 for Bull and -1 for Bear.

    :param prices: (pd.DataFrame) Close prices of all tickers in the market.
    :param window: (int) Rolling window length to determine local extrema. Paper suggests 8 months for monthly obs.
    :param censor: (int) Number of months to eliminate for start and end. Paper suggests 6 months for monthly obs.
    :param cycle: (int) Minimum length for a complete cycle. Paper suggests 16 months for monthly obs.
    :param phase: (int) Minimum length for a phase. Paper suggests 4 months for monthly obs.
    :param threshold: (double) Minimum threshold for phase change. Paper suggests 0.2.
    :return: (pd.DataFrame) Labeled pd.DataFrame. 1 for Bull, -1 for Bear.
    """
    labels = pd.DataFrame(index=prices.index, columns=prices.columns)
    for col in prices.columns:
        price = prices[col]
        # If all NaN or constant, fill with -1 (bear) or 1 (bull) as fallback
        if price.isnull().all():
            labels[col] = np.nan
            continue
        if price.nunique(dropna=True) == 1:
            labels[col] = 1  # treat constant as bull by default
            continue
        labels[col] = _apply_pagan_sossounov(price, window, censor, cycle, phase, threshold)
    return labels


def _alternation(price: pd.Series) -> pd.Series:
    """
    Helper function to check peak and trough alternation.

    :param price: (pd.Series) Close prices of a ticker.
    :return: (pd.Series) Labeled pd.Series. 1 for Bull, -1 for Bear.
    """
    # TODO: Validate this GPT implementation
    # Find local maxima and minima
    extrema = np.zeros(len(price))
    for i in range(1, len(price)-1):
        if price[i] > price[i-1] and price[i] > price[i+1]:
            extrema[i] = 1  # peak
        elif price[i] < price[i-1] and price[i] < price[i+1]:
            extrema[i] = -1  # trough

    # Remove consecutive peaks/troughs, keep alternation
    filtered = np.zeros_like(extrema)
    last = 0
    for i in range(len(extrema)):
        if extrema[i] != 0 and extrema[i] != last:
            filtered[i] = extrema[i]
            last = extrema[i]
    return pd.Series(filtered, index=price.index)


def _apply_pagan_sossounov(price: pd.Series, window, censor, cycle, phase, threshold):
    """
    Helper function for Pagan and Sossounov labeling method.

    :param price: (pd.Series) Close prices of a ticker.
    :param window: (int) Rolling window length to determine local extrema. Paper suggests 8 months for monthly obs.
    :param censor: (int) Number of months to eliminate for start and end. Paper suggests 6 months for monthly obs.
    :param cycle: (int) Minimum length for a complete cycle. Paper suggests 16 months for monthly obs.
    :param phase: (int) Minimum length for a phase. Paper suggests 4 months for monthly obs.
    :param threshold: (double) Minimum threshold for phase change. Paper suggests 20%.
    :return: (pd.Series) Labeled pd.Series. 1 for Bull, -1 for Bear.
    """
    # Handle all-NaN or all-constant
    if price.isnull().all():
        return pd.Series(np.nan, index=price.index)
    if price.nunique(dropna=True) == 1:
        return pd.Series(1, index=price.index)

    # Step 1: Find local maxima/minima using rolling window
    local_max = price[(price.rolling(window, center=True).max() == price)]
    local_min = price[(price.rolling(window, center=True).min() == price)]

    # Step 2: Remove peaks/troughs within censor window of start/end
    local_max = local_max.iloc[censor:-censor] if len(local_max) > 2 * censor else local_max
    local_min = local_min.iloc[censor:-censor] if len(local_min) > 2 * censor else local_min

    # Step 3: Merge and sort extrema
    extrema = pd.concat([local_max, local_min]).sort_index()
    extrema_type = pd.Series(1, index=local_max.index)
    extrema_type = pd.concat([extrema_type, pd.Series(-1, index=local_min.index)])
    extrema_type = extrema_type.sort_index()

    # Step 4: Enforce alternation
    filtered_idx = []
    last_type = 0
    for idx, t in extrema_type.items():
        if t != last_type:
            filtered_idx.append(idx)
            last_type = t
    extrema = extrema.loc[filtered_idx]
    extrema_type = extrema_type.loc[filtered_idx]

    # If no extrema found, fallback to simple regime: uptrend then downtrend
    if len(extrema) < 2:
        # Simple fallback: uptrend then downtrend split at max
        max_idx = price.idxmax()
        labels = pd.Series(-1, index=price.index)
        labels.loc[:max_idx] = 1
        labels.loc[max_idx:] = -1
        return labels.ffill().bfill()

    # Step 5: Remove cycles/phases shorter than minimum
    extrema = extrema.copy()
    extrema_type = extrema_type.copy()
    i = 1
    while i < len(extrema):
        if (extrema.index[i] - extrema.index[i-1]).days < phase * 30:
            # Remove the one with smaller price change
            if abs(extrema.iloc[i] - extrema.iloc[i-1]) < abs(extrema.iloc[i-1] - extrema.iloc[i-2] if i-2 >= 0 else 0):
                extrema = extrema.drop(extrema.index[i])
                extrema_type = extrema_type.drop(extrema_type.index[i])
            else:
                extrema = extrema.drop(extrema.index[i-1])
                extrema_type = extrema_type.drop(extrema_type.index[i-1])
            i = max(i-1, 1)
        else:
            i += 1

    # Step 6: Remove cycles with price change less than threshold
    i = 1
    while i < len(extrema):
        pct_change = abs((extrema.iloc[i] - extrema.iloc[i-1]) / extrema.iloc[i-1])
        if pct_change < threshold:
            extrema = extrema.drop(extrema.index[i])
            extrema_type = extrema_type.drop(extrema_type.index[i])
            i = max(i-1, 1)
        else:
            i += 1

    # Step 7: Assign labels
    labels = pd.Series(-1, index=price.index)
    for i in range(1, len(extrema)):
        start, end = extrema.index[i-1], extrema.index[i]
        if extrema_type.iloc[i-1] == -1 and extrema_type.iloc[i] == 1:
            labels.loc[start:end] = 1  # Bull
        elif extrema_type.iloc[i-1] == 1 and extrema_type.iloc[i] == -1:
            labels.loc[start:end] = -1  # Bear
    labels = labels.ffill().bfill()
    return labels


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
    labels = pd.DataFrame(index=prices.index, columns=prices.columns)
    for col in prices.columns:
        price = prices[col]
        # Handle all-NaN
        if price.isnull().all():
            labels[col] = np.nan
            continue
        # Handle constant series
        if price.nunique(dropna=True) == 1:
            labels[col] = 1
            continue
        labels[col] = _apply_lunde_timmermann(price, bull_threshold, bear_threshold)
    return labels


def _apply_lunde_timmermann(price, bull_threshold, bear_threshold):
    """
    Helper function for Lunde and Timmermann labeling method.

    :param price: (pd.Series) Close prices of a ticker.
    :param bull_threshold: (double) Threshold to identify bull market. Paper suggests 0.15.
    :param bear_threshold: (double) Threshold to identify bear market. Paper suggests 0.15.
    :return: (pd.Series) Labeled pd.Series. 1 for Bull, -1 for Bear.
    """
    # Handle all-NaN or all-constant
    if price.isnull().all():
        return pd.Series(np.nan, index=price.index)
    if price.nunique(dropna=True) == 1:
        return pd.Series(1, index=price.index)

    # Identify local minima and maxima
    local_max = price[(price.shift(1) < price) & (price.shift(-1) < price)]
    local_min = price[(price.shift(1) > price) & (price.shift(-1) > price)]

    # If no extrema found, fallback to uptrend then downtrend split at max
    if len(local_max) + len(local_min) < 2:
        max_idx = price.idxmax()
        labels = pd.Series(-1, index=price.index)
        labels.loc[:max_idx] = 1
        labels.loc[max_idx:] = -1
        return labels.ffill().bfill()

    extrema = pd.concat([local_max, local_min]).sort_index()
    extrema_type = pd.Series(1, index=local_max.index)
    extrema_type = extrema_type.append(pd.Series(-1, index=local_min.index))
    extrema_type = extrema_type.sort_index()

    # Enforce alternation
    filtered_idx = []
    last_type = 0
    for idx, t in extrema_type.items():
        if t != last_type:
            filtered_idx.append(idx)
            last_type = t
    extrema = extrema.loc[filtered_idx]
    extrema_type = extrema_type.loc[filtered_idx]

    # Assign labels
    labels = pd.Series(-1, index=price.index)
    for i in range(1, len(extrema)):
        start, end = extrema.index[i-1], extrema.index[i]
        pct_change = (extrema.iloc[i] - extrema.iloc[i-1]) / extrema.iloc[i-1]
        if extrema_type.iloc[i-1] == -1 and extrema_type.iloc[i] == 1 and pct_change > bull_threshold:
            labels.loc[start:end] = 1  # Bull
        elif extrema_type.iloc[i-1] == 1 and extrema_type.iloc[i] == -1 and pct_change < -bear_threshold:
            labels.loc[start:end] = -1  # Bear
        else:
            # If not enough change, assign bull if price is rising, bear if falling
            if extrema.iloc[i] > extrema.iloc[i-1]:
                labels.loc[start:end] = 1
            else:
                labels.loc[start:end] = -1
    labels = labels.ffill().bfill()
    return labels
