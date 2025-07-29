"""
Functions derived from Chapter 10: Bet Sizing
Only the highest-level user functions are included in the __init__ file.

This folder contains classes and functions for sizing bets based on a given investment strategy with given bet side
confidence, e.g. the output from a machine learning model. The approaches implemented in this module are based on
those described in Chapter 10 of "Advances in Financial Machine Learning" by Marcos López de Prado.
"""

from quantmllib.bet_sizing.bet_sizing import (
                                            bet_size_budget,
                                            bet_size_dynamic,
                                            bet_size_probability,
                                            bet_size_reserve,
                                            cdf_mixture,
                                            confirm_and_cast_to_df,
                                            get_concurrent_sides,
                                            single_bet_size_mixed,
)
from quantmllib.bet_sizing.ef3m import M2N, centered_moment, most_likely_parameters, raw_moment
