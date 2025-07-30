#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Soukaina Timouma
@email: soukaina.timouma@well.OX.AC.UK
"""

#%%
import os
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, RandomizedSearchCV
import math
import pandas as pd
from sklearn.preprocessing import label_binarize
from sklearn.metrics import roc_auc_score
#%%
#############################################################################################################

#### Random forest functions

#############################################################################################################

def runRandomizedSearchCV(X, y, testSize, outdir, n_iter=5000, scoring='accuracy', class_weight=None):
    """
    Perform RandomizedSearchCV to tune hyperparameters of RandomForestClassifier.

    Parameters:
        X (array-like): Features.
        y (array-like): Target labels.
        testSize (float): Fraction of data to use for testing.
        outdir (str): Output directory for results.
        n_iter (int): Number of parameter combinations to try. Default is 5000.
        scoring (str): Scoring metric to optimise. Default is 'accuracy'.

    Returns:
        tuple: Optimal parameters for RandomForestClassifier.
    """
    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=testSize, random_state=42)

    # Define the parameter distributions
    p = X_train.shape[1]
    n_samples = X_train.shape[0]
    log2_features = int(np.log2(p))
    k = 5  # You can set k as needed
    # max_depth range (adjusted with k and +5 as you wrote)
    max_depths = list(range(1, log2_features + k + 5))
    # max_features values from core values + small + evenly spaced
    core_values = [
        max(1, int(np.sqrt(p))),
        max(1, int(np.log2(p))),
        max(1, int(p / 10)),
        max(1, int(p / 3))
    ]
    small_values = list(range(1, min(20, p)))
    evenly_spaced = list(np.linspace(1, p, num=10, dtype=int))
    max_features_values = sorted(set(core_values + small_values + evenly_spaced))
    # min_samples_leaf values
    min_samples_leafs = sorted(set(
        list(range(1, min(11, n_samples))) +                             # Fine-grained small values
        list(range(max(10, n_samples // 100), n_samples // 10, max(1, n_samples // 100))) +  # Moderate
        list(range(n_samples // 10, n_samples // 2, max(1, n_samples // 10)))    # Large leaves
    ))
    # min_samples_split values
    min_samples_split_values = sorted(set(
        list(range(2, min(20, n_samples))) +                              # fine small values
        list(range(max(20, n_samples // 100), max(21, n_samples // 10), max(1, n_samples // 100))) +  # moderate values
        list(range(max(21, n_samples // 10), max(22, n_samples // 2), max(1, n_samples // 10)))        # large values
    ))
    # n_estimators values
    n_trees = list(range(5, 1501, 5))

    param_dist = {
        'n_estimators': n_trees,
        'max_depth': max_depths,
        'min_samples_split': min_samples_split_values,
        'min_samples_leaf': min_samples_leafs,
        'max_features': max_features_values,
        'bootstrap': [True, False]
    }

    # Create the model
    rf = RandomForestClassifier(random_state=42, class_weight=class_weight)

    # Set up RandomizedSearchCV
    random_search = RandomizedSearchCV(
        estimator=rf,
        param_distributions=param_dist,
        n_iter=n_iter,
        scoring=scoring,
        cv=10,  # 10-fold cross-validation
        random_state=42,  # Reproducibility
        n_jobs=-1,  # Use all available processors
        verbose=2  # Display progress
    )

    # Fit RandomizedSearchCV on training data
    random_search.fit(X_train, y_train)

    # Best parameters and score
    best_params = random_search.best_params_
    best_score = random_search.best_score_

    print("Best Parameters:", best_params)
    print(f"Best Cross-Validation {scoring.capitalize()}:", best_score)

    # Prepare output directory
    paramDir = os.path.join(outdir, "Parameters_estimation")
    os.makedirs(paramDir, exist_ok=True)

    # Save detailed results
    cv_results = pd.DataFrame(random_search.cv_results_)
    cv_results.to_csv(os.path.join(paramDir, 'random_search_full_results.csv'), index=False)

    # Save best parameters
    results_df = pd.DataFrame([best_params])
    results_df['best_score'] = best_score
    results_df.to_csv(os.path.join(paramDir, 'random_search_best_params.csv'), index=False)
    
    # Extract optimal parameters
    n_opt = best_params['n_estimators']
    max_depth = best_params['max_depth']
    min_samples_split = best_params['min_samples_split']
    min_samples_leaf = best_params['min_samples_leaf']
    max_features = best_params['max_features']
    bootstrap = best_params['bootstrap']

    return n_opt, max_depth, min_samples_split, min_samples_leaf, max_features, bootstrap
