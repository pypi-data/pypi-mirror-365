"""
Tools for synthetic data generation.
"""

from quantmllib.data_generation.bootstrap import block_bootstrap, pair_bootstrap, row_bootstrap
from quantmllib.data_generation.correlated_random_walks import generate_cluster_time_series
from quantmllib.data_generation.corrgan import sample_from_corrgan
from quantmllib.data_generation.data_verification import (
                                                        plot_eigenvalues,
                                                        plot_eigenvectors,
                                                        plot_hierarchical_structure,
                                                        plot_mst_degree_count,
                                                        plot_optimal_hierarchical_cluster,
                                                        plot_pairwise_dist,
                                                        plot_stylized_facts,
                                                        plot_time_series_dependencies,
)
from quantmllib.data_generation.hcbm import generate_hcmb_mat, time_series_from_dist
from quantmllib.data_generation.vines import sample_from_cvine, sample_from_dvine, sample_from_ext_onion
