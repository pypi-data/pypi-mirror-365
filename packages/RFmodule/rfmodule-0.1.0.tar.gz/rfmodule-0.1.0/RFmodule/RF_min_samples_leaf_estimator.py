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

def estimate_min_samples_leaf(X, y, testSize, outdir):
    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=testSize, random_state=42)

    classes = np.unique(y)
    is_multiclass = len(classes) > 2 

    #########
    # Estimation of the minimum number of samples required to be at a leaf node
    #########

    # min_samples_leafs = list(range(1, 101))  # Initial Default range for min_samples_leaf
    n_samples = X_train.shape[0]
    min_samples_leafs = sorted(set(
    list(range(1, min(11, n_samples))) +                             # Fine-grained small values
    list(range(max(10, n_samples // 100), n_samples // 10, max(1, n_samples // 100))) +  # Moderate
    list(range(n_samples // 10, n_samples // 2, n_samples // 10))    # Large leaves
    ))

    train_results = []
    test_results = []
    per_class_auc_results = []

    for min_samples_leaf in min_samples_leafs:
        rf = RandomForestClassifier(min_samples_leaf=min_samples_leaf, random_state=42)
        rf.fit(X_train, y_train)

        train_probs = rf.predict_proba(X_train)
        test_probs = rf.predict_proba(X_test)

        if is_multiclass:
            y_train_bin = label_binarize(y_train, classes=classes)
            y_test_bin = label_binarize(y_test, classes=classes)

            train_auc = roc_auc_score(y_train_bin, train_probs, average='macro', multi_class='ovr')
            test_auc = roc_auc_score(y_test_bin, test_probs, average='macro', multi_class='ovr')
            
            per_class_auc = {
                f'class_{cls}': roc_auc_score(y_test_bin[:, i], test_probs[:, i])
                for i, cls in enumerate(classes)
            }
            per_class_auc_results.append(per_class_auc)

        else:
            train_auc = roc_auc_score(y_train, train_probs[:, 1])
            test_auc = roc_auc_score(y_test, test_probs[:, 1])
            per_class_auc_results.append({'class_1': test_auc})

        train_results.append(train_auc)
        test_results.append(test_auc)

    # Find optimal min_samples_leaf
    best_idx = np.argmax(test_results)
    best_min_samples_leaf = min_samples_leafs[best_idx]  # Map index to parameter value

    # Plot AUC vs min_samples_leaf
    paramDir = os.path.join(outdir, "Parameters_estimation")
    os.makedirs(paramDir, exist_ok=True)

    plt.plot(min_samples_leafs, train_results, 'b', label="Train AUC")
    plt.plot(min_samples_leafs, test_results, 'r', label="Test AUC")
    plt.legend()
    plt.ylabel('AUC Score')
    plt.xlabel('Min samples leaf')
    plt.title('Random forest AUC vs min samples leaf')
    plt.savefig(os.path.join(paramDir, 'RF_auc_per_min_sample_leaf.png'))
    plt.close()

    auc_df = pd.DataFrame({
        'min_samples_leaf': min_samples_leafs,
        'train_auc': train_results,
        'test_auc': test_results
    })
    auc_csv_path = os.path.join(paramDir, 'RF_auc_per_min_samples_leaf.csv')
    auc_df.to_csv(auc_csv_path, index=False)
    
    per_class_df = pd.DataFrame(per_class_auc_results)
    auc_combined_df = pd.concat([auc_df, per_class_df], axis=1)
    auc_combined_df.to_csv(os.path.join(paramDir, 'RF_auc_per_min_samples_leaf_per_class.csv'), index=False)

    # Plot per-class AUC for best min_samples_leaf
    best_per_class_auc = per_class_auc_results[best_idx]
    plt.figure(figsize=(8, 4))
    plt.bar(best_per_class_auc.keys(), best_per_class_auc.values(), color='black')
    plt.ylabel('AUC score')
    plt.title(f'AUC per-class at best min_samples_leaf = {best_min_samples_leaf}')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(paramDir, 'RF_per_class_auc_best_min_samples_leaf.png'))
    plt.close()

    # Return optimal parameter
    return best_min_samples_leaf
