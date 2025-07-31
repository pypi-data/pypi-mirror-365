import numpy as np
import pandas as pd
import optuna
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import roc_curve, auc, roc_auc_score
from hep_ml import reweight

def evaluate_reweighting(mc, data, weights_mc, weights_data, label, ax, score_dict=None):
    """
    Evaluate the reweighting performance using ROC curve and AUC.

    Args:
        mc (np.ndarray): MC data features.
        data (np.ndarray): Data features.
        weights_mc (np.ndarray): Weights for MC data.
        weights_data (np.ndarray): Weights for Data.
        label (str): Label for the plot.
        ax (matplotlib.axes.Axes): Axes to plot the ROC curve on.
        score_dict (dict, optional): Dictionary to store scores for MC and Data.
    """
    X = np.vstack([mc, data])
    y = np.hstack([np.zeros(len(mc)), np.ones(len(data))])
    sample_weight = np.hstack([weights_mc, weights_data])

    clf = GradientBoostingClassifier(n_estimators=50, max_depth=3)
    clf.fit(X, y, sample_weight=sample_weight)
    y_scores = clf.predict_proba(X)[:, 1]

    if score_dict is not None:
        score_dict["MC"] = y_scores[:len(mc)]
        score_dict["Data"] = y_scores[len(mc):]

    fpr, tpr, _ = roc_curve(y, y_scores, sample_weight=sample_weight)
    auc_val = auc(fpr, tpr)
    if ax is not None:
        ax.plot(fpr, tpr, label=f"{label} (AUC = {auc_val:.3f})")
    return auc_val

def weighted_corr_matrix(df, columns, weights):
    """Compute (weighted) correlation matrix for a DataFrame.
    
    Args:
        df (pd.DataFrame): DataFrame containing the data.
        columns (list): List of column names to include in the correlation matrix.
        weights (np.ndarray, optional): Weights for the correlation calculation. 
    """
    data = df[columns].values
    weights = np.asarray(weights)

    # Weighted mean
    mean = np.average(data, axis=0, weights=weights)

    # Weighted covariance matrix (signed weights)
    xm = data - mean
    cov = np.dot(weights * xm.T, xm) / np.sum(weights)

    # Standard deviations
    stddev = np.sqrt(np.diag(cov))

    # Correlation matrix
    corr = cov / np.outer(stddev, stddev)
    corr = np.clip(corr, -1, 1)  # ensure numerical stability

    return pd.DataFrame(corr, index=columns, columns=columns)

def run_optuna(mc_train, data_train, mc_test, data_test, mcweights_train, mcweights_test, sweights_train, sweights_test, columns, n_trials):
    """    
    Run Optuna hyperparameter optimization for Gradient Boosting Reweighter.

    Args:
        mc_train (pd.DataFrame): MC training data.
        data_train (pd.DataFrame): Data training data.  
        mc_test (pd.DataFrame): MC test data.
        data_test (pd.DataFrame): Data test data.
        mcweights_train (np.ndarray): Weights for training MC data.
        mcweights_test (np.ndarray): Weights for test MC data.
        sweights_train (np.ndarray): Sweights for training data.
        sweights_test (np.ndarray): Sweights for test data.
        columns (list): List of column names to use for training.
        n_trials (int): Number of trials for hyperparameter optimization.
    """
    def objective(trial):
        params = {
            "n_estimators": trial.suggest_int("n_estimators", 40, 100),
            "learning_rate": trial.suggest_float("learning_rate", 0.05, 0.2),
            "max_depth": trial.suggest_int("max_depth", 2, 5),
            "min_samples_leaf": trial.suggest_int("min_samples_leaf", 1000, 3000),
            "subsample": trial.suggest_float("subsample", 0.3, 0.5),
        }

        gb = reweight.GBReweighter(
            n_estimators=params["n_estimators"],
            learning_rate=params["learning_rate"],
            max_depth=params["max_depth"],
            min_samples_leaf=params["min_samples_leaf"],
            gb_args={"subsample": params["subsample"]},
        )

        gb.fit(mc_train[columns], data_train[columns],
               original_weight=mcweights_train,
               target_weight=sweights_train)

        weights_pred = gb.predict_weights(mc_test[columns])
        # Train classifier to evaluate how well MC is reweighted to look like data
        X_clf = pd.concat([mc_test[columns], data_test[columns]])
        y_clf = np.concatenate([np.zeros(len(mc_test)), np.ones(len(data_test))])
        w_clf = np.concatenate([weights_pred, sweights_test])

        clf = GradientBoostingClassifier(random_state=42)
        clf.fit(X_clf, y_clf, sample_weight=w_clf)

        y_score = clf.predict_proba(X_clf)[:, 1]

        return roc_auc_score(y_clf, y_score)

    study = optuna.create_study(direction="minimize")
    study.optimize(objective, n_trials=n_trials)

    return study