"""
Implements the book chapter 7 on Cross Validation for financial data.
"""

from collections.abc import Callable

import numpy as np
import pandas as pd
from sklearn.base import ClassifierMixin
from sklearn.metrics import log_loss
from sklearn.model_selection import BaseCrossValidator, KFold


def ml_get_train_times(samples_info_sets: pd.Series, test_times: pd.Series) -> pd.Series:
    # pylint: disable=invalid-name
    """
    Advances in Financial Machine Learning, Snippet 7.1, page 106.

    Purging observations in the training set

    This function find the training set indexes given the information on which each record is based
    and the range for the test set.
    Given test_times, find the times of the training observations.

    :param samples_info_sets: (pd.Series) The information range on which each record is constructed from
        *samples_info_sets.index*: Time when the information extraction started.
        *samples_info_sets.value*: Time when the information extraction ended.
    :param test_times: (pd.Series) Times for the test dataset.
    :return: (pd.Series) Training set
    """

    train = samples_info_sets.copy(deep=True)
    for start_ix, end_ix in test_times.items():
        df0 = train[(start_ix <= train.index) & (train.index <= end_ix)].index  # Train starts within test
        df1 = train[(start_ix <= train) & (train <= end_ix)].index  # Train ends within test
        df2 = train[(train.index <= start_ix) & (end_ix <= train)].index  # Train envelops test
        train = train.drop(df0.union(df1).union(df2))
    return train


class PurgedKFold(KFold):
    """
    Extend KFold class to work with labels that span intervals.

    The train is purged of observations overlapping test-label intervals.
    Test set is assumed contiguous (shuffle=False), w/o training samples in between.
    """

    def __init__(self,
                 n_splits: int = 3,
                 samples_info_sets: pd.Series = None,
                 pct_embargo: float = 0.):
        """
        Initialize.

        :param n_splits: (int) The number of splits. Default to 3
        :param samples_info_sets: (pd.Series) The information range on which each record is constructed from
            *samples_info_sets.index*: Time when the information extraction started.
            *samples_info_sets.value*: Time when the information extraction ended.
        :param pct_embargo: (float) Percent that determines the embargo size.
        """

        if not isinstance(samples_info_sets, pd.Series):
            raise ValueError("The samples_info_sets param must be a pd.Series")
        super().__init__(n_splits, shuffle=False, random_state=None)

        self.samples_info_sets = samples_info_sets
        self.pct_embargo = pct_embargo

    # noinspection PyPep8Naming
    def split(self,
              X: pd.DataFrame,
              y: pd.Series = None,
              groups=None) -> tuple:
        """
        The main method to call for the PurgedKFold class.

        :param X: (pd.DataFrame) Samples dataset that is to be split.
        :param y: (pd.Series) Sample labels series.
        :param groups: (array-like), with shape (n_samples,), optional
            Group labels for the samples used while splitting the dataset into
            train/test set.
        :return: (tuple) [train list of sample indices, and test list of sample indices].
        """

        if X.shape[0] != self.samples_info_sets.shape[0]:
            raise ValueError("X and the 'samples_info_sets' series param must be the same length")

        indices: np.ndarray = np.arange(X.shape[0])
        embargo: int = int(X.shape[0] * self.pct_embargo)

        test_ranges: [(int, int)] = [(ix[0], ix[-1] + 1) for ix in np.array_split(np.arange(X.shape[0]), self.n_splits)]
        for start_ix, end_ix in test_ranges:
            test_indices = indices[start_ix:end_ix]

            if end_ix < X.shape[0]:
                end_ix += embargo

            test_times = pd.Series(index=[self.samples_info_sets[start_ix]], data=[self.samples_info_sets[end_ix-1]])
            train_times = ml_get_train_times(self.samples_info_sets, test_times)

            train_indices = []
            for train_ix in train_times.index:
                train_indices.append(self.samples_info_sets.index.get_loc(train_ix))
            yield np.array(train_indices), test_indices


# noinspection PyPep8Naming
def ml_cross_val_score(
        classifier: ClassifierMixin,
        X: pd.DataFrame,
        y: pd.Series,
        cv_gen: BaseCrossValidator,
        sample_weight_train: np.ndarray = None,
        sample_weight_score: np.ndarray = None,
        scoring: Callable[[np.array, np.array], float] = log_loss,
        require_proba: bool = True,
        n_jobs_score: int = 1) -> np.array:
    """
    Advances in Financial Machine Learning, Snippet 7.4, page 110.
    Using the PurgedKFold Class.

    Function to run a cross-validation evaluation of the using sample weights and a custom CV generator.
    Note: This function is different to the book in that it requires the user to pass through a CV object. The book
    will accept a None value as a default and then resort to using PurgedCV, this also meant that extra arguments had to
    be passed to the function. To correct this we have removed the default and require the user to pass a CV object to
    the function.

    Example:

    .. code-block:: python

        cv_gen = PurgedKFold(n_splits=n_splits, samples_info_sets=samples_info_sets,
                             pct_embargo=pct_embargo)

        scores_array = ml_cross_val_score(classifier, X, y, cv_gen, sample_weight_train=sample_train,
                                          sample_weight_score=sample_score, scoring=accuracy_score)

    :param classifier: (ClassifierMixin) A sk-learn Classifier object instance.
    :param X: (pd.DataFrame) The dataset of records to evaluate.
    :param y: (pd.Series) The labels corresponding to the X dataset.
    :param cv_gen: (BaseCrossValidator) Cross Validation generator object instance.
    :param sample_weight_train: (np.array) Sample weights used to train the model for each record in the dataset.
    :param sample_weight_score: (np.array) Sample weights used to evaluate the model quality.
    :param scoring: (Callable) A metric scoring, can be custom sklearn metric.
    :param require_proba: (bool) Boolean flag indicating that scoring function requires probabilities.
    :param n_jobs_score: (int) Number of cores used in score function calculation.
    :return: (np.array) The computed score.
    """

    # If no sample_weight then broadcast a value of 1 to all samples (full weight).
    if sample_weight_train is None:
        sample_weight_train = np.ones((X.shape[0],))

    if sample_weight_score is None:
        sample_weight_score = np.ones((X.shape[0],))

    # Score model on KFolds
    ret_scores = []
    for train, test in cv_gen.split(X=X, y=y):
        fit = classifier.fit(X=X.iloc[train, :], y=y.iloc[train], sample_weight=sample_weight_train[train])
        if scoring == log_loss:
            prob = fit.predict_proba(X.iloc[test, :])
            score = -1 * scoring(y.iloc[test], prob, sample_weight=sample_weight_score[test], labels=classifier.classes_)
        else:
            pred = fit.predict(X.iloc[test, :])
            score = scoring(y.iloc[test], pred, sample_weight=sample_weight_score[test])
        ret_scores.append(score)
    return np.array(ret_scores)

def _score_model(
        classifier: ClassifierMixin,
        X: pd.DataFrame,
        y: pd.Series,
        train,
        test,
        sample_weight_train: np.ndarray,
        sample_weight_score: np.ndarray,
        scoring: Callable[[np.array, np.array], float],
        require_proba: bool) -> np.array:
    """
    Helper function used in multi-core ml_cross_val_score.

    :param classifier: (ClassifierMixin) A sk-learn Classifier object instance.
    :param X: (pd.DataFrame) The dataset of records to evaluate.
    :param y: (pd.Series) The labels corresponding to the X dataset.
    :param sample_weight_train: (np.array) Sample weights used to train the model for each record in the dataset.
    :param sample_weight_score: (np.array) Sample weights used to evaluate the model quality.
    :param scoring: (Callable) A metric scoring, can be custom sklearn metric.
    :param require_proba: (bool) Boolean flag indicating that scoring function requires probabilities.
    :return: (np.array) The computed score.
    """

    pass


class StackedPurgedKFold(KFold):
    """
    Extend KFold class to work with labels that span intervals in multi-asset datasets.

    The train is purged of observations overlapping test-label intervals.
    Test set is assumed contiguous (shuffle=False), w/o training samples in between.
    """

    def __init__(self,
                 n_splits: int = 3,
                 samples_info_sets_dict: dict = None,
                 pct_embargo: float = 0.):
        """
        Initialize.

        :param n_splits: (int) The number of splits. Default to 3.
        :param samples_info_sets_dict: (dict) Dictionary of asset: the information range on which each record is
            *constructed from samples_info_sets.index*: Time when the information extraction started.
            *samples_info_sets.value*: Time when the information extraction ended.
        :param pct_embargo: (float) Percent that determines the embargo size.
        """

        pass

    def split(self,
              X_dict: dict,
              y_dict: dict = None,
              groups=None) -> dict:
        # pylint: disable=arguments-differ, unused-argument
        """
        The main method to call for the StackedPurgedKFold class.

        :param X_dict: (dict) Dictionary of asset: X(features).
        :param y_dict: (dict) Dictionary of asset: y(features).
        :param groups: (array-like), with shape (n_samples,), optional
            Group labels for the samples used while splitting the dataset into
            train/test set.
        :return: (dict) Dictionary of asset: [train list of sample indices, and test list of sample indices].
        """

        pass


def stacked_ml_cross_val_score(
        classifier: ClassifierMixin,
        X_dict: dict,
        y_dict: dict,
        cv_gen: BaseCrossValidator,
        sample_weight_train_dict: dict = None,
        sample_weight_score_dict: dict = None,
        scoring: Callable[[np.array, np.array], float] = log_loss,
        require_proba: bool = True,
        n_jobs_score: int = 1) -> np.array:
    """
    Implements ml_cross_val_score (quantmllib.cross_validation.ml_cross_val_score) for multi-asset dataset.

    Function to run a cross-validation evaluation of the using sample weights and a custom CV generator.
    Note: This function is different to the book in that it requires the user to pass through a CV object. The book
    will accept a None value as a default and then resort to using PurgedCV, this also meant that extra arguments had to
    be passed to the function. To correct this we have removed the default and require the user to pass a CV object to
    the function.

    Example:

    .. code-block:: python

        cv_gen = PurgedKFold(n_splits=n_splits, samples_info_sets=samples_info_sets,
                             pct_embargo=pct_embargo)

        scores_array = ml_cross_val_score(classifier, X, y, cv_gen, sample_weight_train=sample_train,
                                          sample_weight_score=sample_score, scoring=accuracy_score)

    :param classifier: (ClassifierMixin) A sk-learn Classifier object instance.
    :param X_dict: (dict) Dictionary of asset : X_{asset}.
    :param y_dict: (dict) Dictionary of asset : y_{asset}
    :param cv_gen: (BaseCrossValidator) Cross Validation generator object instance.
    :param sample_weight_train_dict: Dictionary of asset: sample_weights_train_{asset}
    :param sample_weight_score_dict: Dictionary of asset: sample_weights_score_{asset}
    :param scoring: (Callable) A metric scoring, can be custom sklearn metric.
    :param require_proba: (bool) Boolean flag indicating that scoring function requires probabilities.
    :param n_jobs_score: (int) Number of cores used in score function calculation.
    :return: (np.array) The computed score.
    """

    pass


def stacked_dataset_from_dict(X_dict: dict, y_dict: dict, sample_weights_train_dict: dict,
                              sample_weights_score_dict: dict,
                              index: dict) -> tuple:
    """
    Helper function used to create appended dataset (X, y, sample weights train/score) using dictionary of train/test
    indices.

    :param X_dict: (dict) Dictionary of asset : X_{asset}.
    :param y_dict: (dict) Dictionary of asset : y_{asset}
    :param sample_weights_train_dict: Dictionary of asset: sample_weights_train_{asset}
    :param sample_weights_score_dict: Dictionary of asset: sample_weights_score_{asset}
    :param index: (dict) Dictionary of asset: int indices (it may be either train or test indices).
    :return: (tuple) Tuple of appended datasets: X, y, sample weights train, sample_weights score.
    """

    pass


def _stacked_score_model(classifier, X_dict, y_dict, train, test, sample_weight_train_dict, sample_weight_score_dict,
                         scoring, require_proba):
    """
    Helper function used in multi-core ml_cross_val_score.

    :param classifier: (ClassifierMixin) A sk-learn Classifier object instance.
    :param X_dict: (dict) Dictionary of asset : X_{asset}.
    :param y_dict: (dict) Dictionary of asset : y_{asset}
    :param sample_weight_train_dict: (np.array) Sample weights used to train the model for each record in the dataset.
    :param sample_weight_score_dict: (np.array) Sample weights used to evaluate the model quality.
    :param scoring: (Callable) A metric scoring, can be custom sklearn metric.
    :param require_proba: (bool) Boolean flag indicating that scoring function requires probabilities.
    :return: (np.array) The computed score.
    """

    pass
