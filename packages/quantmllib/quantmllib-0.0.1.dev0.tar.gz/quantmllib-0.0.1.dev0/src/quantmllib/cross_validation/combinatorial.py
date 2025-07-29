"""
Implements the Combinatorial Purged Cross-Validation class from Chapter 12
"""

from itertools import combinations

import numpy as np
import pandas as pd
from scipy.special import comb
from sklearn.model_selection import KFold

from .cross_validation import ml_get_train_times


def _get_number_of_backtest_paths(n_train_splits: int, n_test_splits: int) -> float:
    """
    Number of combinatorial paths for CPCV(N,K)
    :param n_train_splits: (int) number of train splits
    :param n_test_splits: (int) number of test splits
    :return: (int) number of backtest paths for CPCV(N,k)
    """
    return int(comb(n_train_splits, n_train_splits - n_test_splits) * n_test_splits / n_train_splits)


class CombinatorialPurgedKFold(KFold):
    """
    Advances in Financial Machine Learning, Chapter 12.

    Implements Combinatial Purged Cross Validation (CPCV)

    The train is purged of observations overlapping test-label intervals
    Test set is assumed contiguous (shuffle=False), w/o training samples in between

    :param n_splits: (int) The number of splits. Default to 3
    :param samples_info_sets: (pd.Series) The information range on which each record is constructed from
        *samples_info_sets.index*: Time when the information extraction started.
        *samples_info_sets.value*: Time when the information extraction ended.
    :param pct_embargo: (float) Percent that determines the embargo size.
    """

    def __init__(self,
                 n_splits: int = 3,
                 n_test_splits: int = 2,
                 samples_info_sets: pd.Series = None,
                 pct_embargo: float = 0.):

        if not isinstance(samples_info_sets, pd.Series):
            raise ValueError("The samples_info_sets param must be a pd.Series")
        super().__init__(n_splits, shuffle=False, random_state=None)

        self.samples_info_sets = samples_info_sets
        self.pct_embargo = pct_embargo
        self.n_test_splits = n_test_splits
        self.num_backtest_paths = _get_number_of_backtest_paths(self.n_splits, self.n_test_splits)
        self.backtest_paths = []  # Array of backtest paths

    def _generate_combinatorial_test_ranges(self, splits_indices: dict) -> list:
        """
        Using start and end indices of test splits from KFolds and number of test_splits (self.n_test_splits),
        generates combinatorial test ranges splits

        :param splits_indices: (dict) Test fold integer index: [start test index, end test index]
        :return: (list) Combinatorial test splits ([start index, end index])
        """

        # Possible test splits for each fold
        combinatorial_splits = list(combinations(list(splits_indices.keys()), self.n_test_splits))
        combinatorial_test_ranges = []  # List of test indices formed from combinatorial splits
        for combination in combinatorial_splits:
            temp_test_indices = []  # Array of test indices for current split combination
            for int_index in combination:
                temp_test_indices.append(splits_indices[int_index])
            combinatorial_test_ranges.append(temp_test_indices)
        return combinatorial_test_ranges

    def _fill_backtest_paths(self, train_indices: list, test_splits: list):
        """
        Using start and end indices of test splits and purged/embargoed train indices from CPCV, find backtest path and
        place in the path where these indices should be used.

        :param test_splits: (list) of lists with first element corresponding to test start index and second - test end
        """
        # Fill backtest paths using train/test splits from CPCV
        for split in test_splits:
            found = False  # Flag indicating that split was found and filled in one of backtest paths
            for path in self.backtest_paths:
                for path_el in path:
                    if path_el["train"] is None and split == path_el["test"] and found is False:
                        path_el["train"] = np.array(train_indices)
                        path_el["test"] = list(range(split[0], split[-1]))
                        found = True

    # noinspection PyPep8Naming
    def split(self,
              X: pd.DataFrame,
              y: pd.Series = None,
              groups=None):
        """
        The main method to call for the PurgedKFold class

        :param X: (pd.DataFrame) Samples dataset that is to be split
        :param y: (pd.Series) Sample labels series
        :param groups: (array-like), with shape (n_samples,), optional
            Group labels for the samples used while splitting the dataset into
            train/test set.
        :return: (tuple) [train list of sample indices, and test list of sample indices]
        """
        if X.shape[0] != self.samples_info_sets.shape[0]:
            raise ValueError("X and the 'samples_info_sets' series param must be the same length")

        test_ranges: [(int, int)] = [(ix[0], ix[-1] + 1) for ix in np.array_split(np.arange(X.shape[0]), self.n_splits)]
        splits_indices = {}
        for index, [start_ix, end_ix] in enumerate(test_ranges):
            splits_indices[index] = [start_ix, end_ix]

        combinatorial_test_ranges = self._generate_combinatorial_test_ranges(splits_indices)
        # Prepare backtest paths
        for _ in range(self.num_backtest_paths):
            path = []
            for split_idx in splits_indices.values():
                path.append({"train": None, "test": split_idx})
            self.backtest_paths.append(path)

        embargo: int = int(X.shape[0] * self.pct_embargo)
        for test_splits in combinatorial_test_ranges:

            # Embargo
            test_times = pd.Series(index=[self.samples_info_sets[ix[0]] for ix in test_splits], data=[
                self.samples_info_sets[ix[1] - 1] if ix[1] - 1 + embargo >= X.shape[0] else self.samples_info_sets[
                    ix[1] - 1 + embargo]
                for ix in test_splits])

            test_indices = []
            for [start_ix, end_ix] in test_splits:
                test_indices.extend(list(range(start_ix, end_ix)))

            # Purge
            train_times = ml_get_train_times(self.samples_info_sets, test_times)

            # Get indices
            train_indices = []
            for train_ix in train_times.index:
                train_indices.append(self.samples_info_sets.index.get_loc(train_ix))

            self._fill_backtest_paths(train_indices, test_splits)

            yield np.array(train_indices), np.array(test_indices)


# FIXME: Stacked Combinatorial Purged KFold implemented by ChatGPT is not tested and may not work as expected.
class StackedCombinatorialPurgedKFold(KFold):
    """
    Implements Stacked Combinatorial Purged Cross Validation (CPCV) for multi-asset datasets.
    Ensures that training samples are purged of overlap with test label intervals,
    and that embargo periods are respected.
    """

    def __init__(self,
                 n_splits: int = 3,
                 n_test_splits: int = 2,
                 samples_info_sets_dict: dict[str, pd.Series] = None,
                 pct_embargo: float = 0.):
        """
        Initialize.

        :param n_splits: Number of total KFold splits.
        :param n_test_splits: Number of splits to use as test in each combination.
        :param samples_info_sets_dict: Dictionary of {asset: sample_info_sets}, where
                                       sample_info_sets is a pd.Series with:
                                         index -> info start time,
                                         values -> info end time.
        :param pct_embargo: Embargo percentage to apply between training and test sets.
        """
        super().__init__(n_splits=n_splits, shuffle=False)
        self.n_test_splits = n_test_splits
        self.samples_info_sets_dict = samples_info_sets_dict
        self.pct_embargo = pct_embargo

    def _generate_combinatorial_test_ranges(self, splits_indices: dict[int, list[int]]) -> list[list[int]]:
        """
        Generate all combinations of test splits.

        :param splits_indices: Dict of split_idx -> [start_idx, end_idx]
        :return: List of test index ranges: [start_idx, end_idx]
        """
        comb = combinations(splits_indices.keys(), self.n_test_splits)
        test_ranges = []
        for c in comb:
            combined = [splits_indices[k] for k in c]
            start = min(i[0] for i in combined)
            end = max(i[1] for i in combined)
            test_ranges.append([start, end])
        return test_ranges

    def _purge(self, train_idx, test_start, test_end, info_start, info_end, embargo_size):
        """
        Purge training indices that overlap with test label periods or embargo.

        :param train_idx: Train index array.
        :param test_start: Start of test window.
        :param test_end: End of test window.
        :param info_start: Array of info start times.
        :param info_end: Array of info end times.
        :param embargo_size: Number of samples to embargo after test.
        :return: Purged training index array.
        """
        mask = np.ones(len(train_idx), dtype=bool)
        for i, idx in enumerate(train_idx):
            if info_start[idx] <= test_end and info_end[idx] >= test_start:
                mask[i] = False
            if idx >= test_end and idx <= test_end + embargo_size:
                mask[i] = False
        return train_idx[mask]

    def split(self,
              X_dict: dict[str, np.ndarray],
              y_dict: dict[str, np.ndarray] = None,
              groups=None):
        """
        Generator yielding train-test indices per CPCV logic.

        :param X_dict: Dictionary of {asset: X matrix}.
        :param y_dict: Not used directly here (optional).
        :param groups: Not used.
        :yield: Tuple (train_indices_dict, test_indices_dict)
        """
        for asset, X in X_dict.items():
            n_samples = X.shape[0]
            embargo_size = int(n_samples * self.pct_embargo)
            sample_info = self.samples_info_sets_dict[asset]

            # Convert index to positional index
            info_start = sample_info.index.values
            info_end = sample_info.values

            kf = super().split(X)
            splits = {i: [test_idx[0], test_idx[-1]] for i, (_, test_idx) in enumerate(kf)}

            test_ranges = self._generate_combinatorial_test_ranges(splits)

            for test_start, test_end in test_ranges:
                all_indices = np.arange(n_samples)
                test_idx = np.arange(test_start, test_end + 1)

                # Training indices before test_start
                train_idx = np.setdiff1d(all_indices, test_idx)
                train_idx = self._purge(train_idx, test_start, test_end,
                                        info_start, info_end, embargo_size)

                yield {asset: train_idx}, {asset: test_idx}

    def _fill_backtest_paths(self, asset, train_indices: list, test_splits: list):
        """
        For a given asset, associate the backtest paths (train/test segments) for CPCV evaluation.

        :param asset: Asset identifier.
        :param train_indices: List of (train_start_idx, train_end_idx).
        :param test_splits: List of (test_start_idx, test_end_idx).
        :return: None (intended for storing backtest path positions or visualization).
        """
        # This method would typically log or store these splits in a tracking structure.
        # Could be implemented to populate self.asset_backtest_paths[asset] for later use.
        pass
