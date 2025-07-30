#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Soukaina Timouma
@email: soukaina.timouma@well.OX.AC.UK
"""

#%%
import os
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_curve, auc
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.preprocessing import label_binarize
from sklearn.metrics import roc_auc_score

#%%
#############################################################################################################

#### Random forest functions

#############################################################################################################

def estimate_max_features(X, y, testSize, outdir):
    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=testSize, random_state=42)
    
    classes = np.unique(y)
    is_multiclass = len(classes) > 2

    #########
    # Estimation of the minimum number of features to consider when looking for the best split
    #########
    
    p = X_train.shape[1]  # Number of features

    # Core heuristic values (ensuring at least 1)
    core_values = [
        max(1, int(np.sqrt(p))),
        max(1, int(np.log2(p))),
        max(1, int(p / 10)),
        max(1, int(p / 3))
    ]

    #small values for fine granularity near the lower end
    small_values = list(range(1, min(20, p)))

    #values evenly spaced across the feature range
    evenly_spaced = list(np.linspace(1, p, num=10, dtype=int))

    #all, remove duplicates and sort
    max_features_values = sorted(set(core_values + small_values + evenly_spaced))

    # max_features_values = list(range(1, p))
    
    train_results = []
    test_results = []
    per_class_auc_results = []

    for max_feature in max_features_values:
        rf = RandomForestClassifier(max_features=max_feature, random_state=42)
        rf.fit(X_train, y_train)
        
        train_probs = rf.predict_proba(X_train)
        test_probs = rf.predict_proba(X_test)

        if is_multiclass:
            y_train_bin = label_binarize(y_train, classes=classes)
            y_test_bin = label_binarize(y_test, classes=classes)

            train_auc = roc_auc_score(y_train_bin, train_probs, average='macro', multi_class='ovr')
            test_auc = roc_auc_score(y_test_bin, test_probs, average='macro', multi_class='ovr')

            # Per-class AUC
            per_class_auc = {}
            for i, cls in enumerate(classes):
                cls_auc = roc_auc_score(y_test_bin[:, i], test_probs[:, i])
                per_class_auc[f'class_{cls}'] = cls_auc
            per_class_auc_results.append(per_class_auc)

        else:
            train_auc = roc_auc_score(y_train, train_probs[:, 1])
            test_auc = roc_auc_score(y_test, test_probs[:, 1])
            per_class_auc_results.append({'class_1': test_auc})
        
        train_results.append(train_auc)
        test_results.append(test_auc)

    # Find the optimal max_features based on test AUC
    best_max_feature_idx = np.argmax(test_results)  # Get the index of the highest AUC
    best_max_feature = max_features_values[best_max_feature_idx]  # Map index to max_features value
    
    # Calculate sqrt of features for diversity
    features_sqrt_opt = int(np.sqrt(p))

    # Plot max_features vs AUC
    paramDir = os.path.join(outdir, "Parameters_estimation")
    os.makedirs(paramDir, exist_ok=True)

    plt.plot(max_features_values, train_results, 'b', label="Train AUC")
    plt.plot(max_features_values, test_results, 'r', label="Test AUC")
    plt.legend()
    plt.ylabel('AUC score')
    plt.xlabel('Max features')
    plt.title('Random forest AUC vs max features')
    plt.savefig(os.path.join(paramDir, 'RF_auc_per_max_features.png'))
    plt.close()

    # Save AUC scores to CSV
    auc_df = pd.DataFrame({
        'max_features': max_features_values,
        'train_auc': train_results,
        'test_auc': test_results
    })
    auc_csv_path = os.path.join(paramDir, 'RF_auc_per_max_features.csv')
    auc_df.to_csv(auc_csv_path, index=False)

    per_class_df = pd.DataFrame(per_class_auc_results)
    auc_combined_df = pd.concat([auc_df, per_class_df], axis=1)
    auc_combined_df.to_csv(os.path.join(paramDir, 'RF_auc_per_max_features_per_class.csv'), index=False)

    # Plot per-class AUC for best
    best_per_class_auc = per_class_auc_results[best_max_feature_idx]
    plt.figure(figsize=(8, 4))
    plt.bar(best_per_class_auc.keys(), best_per_class_auc.values(), color='black')
    plt.ylabel('AUC score')
    plt.title(f'AUC per-class at best max_features = {best_max_feature}')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(paramDir, 'RF_per_class_auc_best_max_features.png'))
    plt.close()
    
    # Return optimal parameters
    return best_max_feature, features_sqrt_opt
