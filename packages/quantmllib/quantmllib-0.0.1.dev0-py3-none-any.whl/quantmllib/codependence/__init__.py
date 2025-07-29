"""
Various codependence measures: mutual info, distance correlations, variation of information.
"""

from quantmllib.codependence.codependence_matrix import get_dependence_matrix, get_distance_matrix
from quantmllib.codependence.correlation import (
                                               absolute_angular_distance,
                                               angular_distance,
                                               distance_correlation,
                                               kullback_leibler_distance,
                                               norm_distance,
                                               squared_angular_distance,
)
from quantmllib.codependence.gnpr_distance import gnpr_distance, gpr_distance, spearmans_rho
from quantmllib.codependence.information import (
                                               get_mutual_info,
                                               get_optimal_number_of_bins,
                                               variation_of_information_score,
)
from quantmllib.codependence.optimal_transport import optimal_transport_dependence
