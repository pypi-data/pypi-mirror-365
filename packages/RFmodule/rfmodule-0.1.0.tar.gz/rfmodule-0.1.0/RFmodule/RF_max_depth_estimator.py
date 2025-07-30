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
import math
import pandas as pd

from sklearn.preprocessing import label_binarize
from sklearn.metrics import roc_auc_score

#%%
#############################################################################################################

#### Random forest functions

#############################################################################################################

def estimate_max_depth(X, y, testSize, outdir):

    classes = np.unique(y)
    is_multiclass = len(classes) > 2

    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=testSize, random_state=42)  # 42 is a reference from Hitchhikers guide to galaxy book. The answer to life universe and everything and is meant as a joke

    #########
    # Estimation of optimal depth of trees
    #########

    # Baseline and adjustment for tree depth
    log2_features = int(math.log2(X_train.shape[1]))  # log2​(n_features) gives a baseline estimate of how many splits are needed to explore a meaningful number of feature combinations
    k=5 # Adding k allows the model to explore deeper relationships in the data without being overly restricted by log⁡2(n_features)
    # with our data, k small (1-3) can lead to under fitting, while k large (10-20) can lead to over fitting, k=5 works well is a reasonable starting point
    # small features (<100) k between 1 and 3 to avoid overly deep trees
    # large features (>10000) k between 3 and 10 to avoid overly deep trees, we can consider k when extra large and complex dataset (millions of features)
    
    max_depths = list(range(1, log2_features + k + 5))  # Initial Depth range to explore
    # max_depths = list(range(1, log2_features))  # Depth range to explore

    train_results = []
    test_results = []
    per_class_auc_results = [] 

    for max_depth in max_depths:
        rf = RandomForestClassifier(max_depth=max_depth, random_state=42)
        rf.fit(X_train, y_train)

        # Use predicted probabilities for each class
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

    # Optimal depth and adjusted depth
    best_depth_idx = np.argmax(test_results)
    best_max_depth = max_depths[best_depth_idx]  # Map index to depth value
    # depth_log2_opt = max(10, log2_features + k)  # Ensure minimum reasonable depth
    depth_log2_opt = max(10, log2_features)  # Ensure minimum reasonable depth

    # Plot AUC vs Tree Depth
    paramDir = os.path.join(outdir, "Parameters_estimation")
    os.makedirs(paramDir, exist_ok=True)

    plt.plot(max_depths, train_results, 'b', label='Train AUC')
    plt.plot(max_depths, test_results, 'r', label='Test AUC')
    plt.legend()
    plt.ylabel('AUC score')
    plt.xlabel('Tree depth')
    plt.title('Random forest AUC vs tree depth')
    plt.savefig(os.path.join(paramDir, 'RF_auc_per_tree_depth.png'))
    plt.close()

    # Save AUC scores to CSV
    auc_df = pd.DataFrame({
        'max_depth': max_depths,
        'train_auc': train_results,
        'test_auc': test_results
    })
    auc_csv_path = os.path.join(paramDir, 'RF_auc_per_tree_depth.csv')
    auc_df.to_csv(auc_csv_path, index=False)

    per_class_df = pd.DataFrame(per_class_auc_results)
    auc_combined_df = pd.concat([auc_df, per_class_df], axis=1)
    auc_combined_df.to_csv(os.path.join(paramDir, 'RF_auc_per_tree_depth_per_class.csv'), index=False)

    # Plot per-class AUC at best depth
    best_per_class_auc = per_class_auc_results[best_depth_idx]
    plt.figure(figsize=(8, 4))
    plt.bar(best_per_class_auc.keys(), best_per_class_auc.values(), color='black')
    plt.ylabel('AUC score')
    plt.title(f'AUC per-class at best depth = {best_max_depth}')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(paramDir, 'RF_per_class_auc_best_depth.png'))
    plt.close()

    # Return parameters
    return best_max_depth, depth_log2_opt
