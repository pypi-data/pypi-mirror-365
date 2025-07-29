"""
Labeling techniques used in financial machine learning.
"""

from quantmllib.labeling.bull_bear import lunde_timmermann, pagan_sossounov
from quantmllib.labeling.excess_over_mean import excess_over_mean
from quantmllib.labeling.excess_over_median import excess_over_median
from quantmllib.labeling.fixed_time_horizon import fixed_time_horizon
from quantmllib.labeling.labeling import (
                                        add_vertical_barrier,
                                        apply_pt_sl_on_t1,
                                        barrier_touched,
                                        drop_labels,
                                        get_bins,
                                        get_events,
)
from quantmllib.labeling.matrix_flags import MatrixFlagLabels
from quantmllib.labeling.raw_return import raw_return
from quantmllib.labeling.return_vs_benchmark import return_over_benchmark
from quantmllib.labeling.tail_sets import TailSetLabels
from quantmllib.labeling.trend_scanning import trend_scanning_labels
