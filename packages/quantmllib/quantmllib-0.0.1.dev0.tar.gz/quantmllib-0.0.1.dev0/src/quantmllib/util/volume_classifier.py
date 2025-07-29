"""
Volume classification methods (BVC and tick rule)
"""

import pandas as pd
from scipy.stats import norm


def get_bvc_buy_volume(close: pd.Series, volume: pd.Series, window: int = 20) -> pd.Series:
    """
    Calculates the BVC buy volume

    :param close: (pd.Series): Close prices
    :param volume: (pd.Series): Bar volumes
    :param window: (int): Window for std estimation uses in BVC calculation
    :return: (pd.Series) BVC buy volume
    """
    # .apply(norm.cdf) is used to omit Warning for norm.cdf(pd.Series with NaNs)

    return volume * (close.diff() / close.diff().rolling(window=window).std()).apply(norm.cdf)
