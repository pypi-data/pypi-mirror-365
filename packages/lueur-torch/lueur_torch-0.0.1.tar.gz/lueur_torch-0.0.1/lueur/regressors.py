"""
Linear decoding utilities for evaluating L1, L2, or ElasticNet regressors.
"""

import numpy as np
from sklearn.linear_model import Lasso, Ridge, ElasticNet
from sklearn.model_selection import train_test_split
from scipy.stats import pearsonr
from tqdm import tqdm


def evaluate_regressor(model, X_train, Y_train, X_test, Y_test):
    """
    Fit a regressor and compute Pearson correlations per target dimension.

    Parameters
    ----------
    model : sklearn regressor
        Instantiated sklearn model (e.g., Ridge).
    X_train : ndarray
        Training inputs, shape (n_samples, n_features).
    Y_train : ndarray
        Training targets, shape (n_samples, n_targets).
    X_test : ndarray
        Test inputs.
    Y_test : ndarray
        Test targets.

    Returns
    -------
    correlations : ndarray
        Pearson correlations per output dimension.
    model : sklearn regressor
        The fitted model.
    """
    model.fit(X_train, Y_train)
    preds = model.predict(X_test)
    corrs = [pearsonr(Y_test[:, i], preds[:, i])[0] for i in range(Y_test.shape[1])]
    return np.nan_to_num(corrs), model


def sweep_regressors(
    X, Y, alphas=None, fit_type="all", test_size=0.2, random_state=42, verbose=True
):
    """
    Evaluate linear regressors over a range of alphas.

    Parameters
    ----------
    X : ndarray
        Input features, shape (n_samples, n_features).
    Y : ndarray
        Output targets, shape (n_samples, n_targets).
    alphas : list or ndarray, optional
        Regularization strengths. Default is logspace from 1e-2 to 1e2.
    fit_type : str
        One of {"l1", "l2", "elasticnet", "all"}.
    test_size : float
        Fraction of data used for testing.
    random_state : int
        Seed for reproducibility.
    verbose : bool
        Whether to display a progress bar.

    Returns
    -------
    results : dict
        Mapping from model name to (correlations, model).
    best : tuple
        (name, correlations, model) for best-performing regressor.
    """
    if alphas is None:
        alphas = np.logspace(-3, 3, 10)

    fit_type = fit_type.lower()
    assert fit_type in {"l1", "l2", "elasticnet", "all"}

    X_train, X_test, Y_train, Y_test = train_test_split(
        X, Y, test_size=test_size, random_state=random_state
    )

    results = {}
    loop = tqdm(alphas, disable=not verbose, desc=f"Fitting {fit_type}")

    for alpha in loop:
        models = []

        if fit_type in {"l1", "all"}:
            models.append(("l1", Lasso(alpha=alpha, max_iter=500, tol=1e-3)))

        if fit_type in {"l2", "all"}:
            models.append(("l2", Ridge(alpha=alpha)))

        if fit_type in {"elasticnet", "all"}:
            models.append(("elasticnet", ElasticNet(alpha=alpha, l1_ratio=0.5, max_iter=500, tol=1e-3)))

        for name, model in models:
            corrs, fitted = evaluate_regressor(model, X_train, Y_train, X_test, Y_test)
            results[f"{name}_{alpha:.1e}"] = (corrs, fitted)

    best_name = max(results, key=lambda k: np.mean(results[k][0]))
    best_corrs, best_model = results[best_name]

    return results, (best_name, best_corrs, best_model)
