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
from sklearn.metrics import accuracy_score, roc_curve, auc
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.preprocessing import label_binarize
from sklearn.metrics import roc_auc_score
#%%
#############################################################################################################

#### Random forest functions

#############################################################################################################

def estimate_ntree(X, y, testSize, outdir):
    """
    Estimates the optimal number of trees for a RandomForestClassifier
    based on accuracy and AUC.

    Parameters:
        X (np.array): Feature matrix
        y (np.array): Labels
        testSize (float): Fraction for test split
        outdir (str): Output directory to save plots and results

    Returns:
        tuple: (best_ntree_by_auc, best_ntree_by_accuracy)
    """

    # Create output directory
    param_dir = os.path.join(outdir, "Parameters_estimation")
    os.makedirs(param_dir, exist_ok=True)

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=testSize, random_state=42)

    classes = np.unique(y)
    is_multiclass = len(classes) > 2


    # Range of tree numbers to test
    n_trees = list(range(5, 1501, 5))
    accuracy_scores = []
    train_aucs = []
    test_aucs = []
    per_class_auc_results = []

    # Evaluate each tree count
    for n in n_trees:
        rf = RandomForestClassifier(n_estimators=n, random_state=42)
        rf.fit(X_train, y_train)

        # Accuracy
        y_pred_test = rf.predict(X_test)
        accuracy_scores.append(accuracy_score(y_test, y_pred_test))

        # AUC
        if is_multiclass:
            y_train_bin = label_binarize(y_train, classes=classes)
            y_test_bin = label_binarize(y_test, classes=classes)

            train_probs = rf.predict_proba(X_train)
            test_probs = rf.predict_proba(X_test)

            train_auc = roc_auc_score(y_train_bin, train_probs, average='macro', multi_class='ovr')
            test_auc = roc_auc_score(y_test_bin, test_probs, average='macro', multi_class='ovr')

            per_class_auc = {
                f'class_{cls}': roc_auc_score(y_test_bin[:, i], test_probs[:, i])
                for i, cls in enumerate(classes)
            }

        else:
            train_probs = rf.predict_proba(X_train)[:, 1]
            test_probs = rf.predict_proba(X_test)[:, 1]

            train_auc = roc_auc_score(y_train, train_probs)
            test_auc = roc_auc_score(y_test, test_probs)

            per_class_auc = {'class_1': test_auc}

        train_aucs.append(train_auc)
        test_aucs.append(test_auc)
        per_class_auc_results.append(per_class_auc)

    # Best number of trees by accuracy and AUC
    best_idx_auc = np.argmax(test_aucs)
    best_ntree_by_accuracy = n_trees[np.argmax(accuracy_scores)]
    best_ntree_by_auc = n_trees[best_idx_auc]
    best_per_class_auc = per_class_auc_results[best_idx_auc]
    
    # Plot Accuracy vs Number of Trees
    plt.figure(figsize=(8, 6))
    plt.plot(n_trees, accuracy_scores, marker='o', label="Accuracy")
    plt.xlabel('Number of trees')
    plt.ylabel('Accuracy')
    plt.title("Random forest accuracy vs number of trees")
    plt.grid(True)
    plt.savefig(os.path.join(param_dir, 'RF_accuracy_per_ntree.png'))
    plt.close()

    # Plot AUC vs Number of Trees
    plt.figure(figsize=(8, 6))
    plt.plot(n_trees, train_aucs, label="Train AUC", color='blue')
    plt.plot(n_trees, test_aucs, label="Test AUC", color='red')
    plt.xlabel('Number of trees')
    plt.ylabel('AUC score')
    plt.title("AUC scores vs number of trees")
    plt.legend()
    plt.grid(True)
    plt.savefig(os.path.join(param_dir, 'RF_AUC_score_per_ntree.png'))
    plt.close()

    # Save results to CSV
    df = pd.DataFrame({
        'n_trees': n_trees,
        'accuracy': accuracy_scores,
        'train_auc': train_aucs,
        'test_auc': test_aucs
    })
    df.to_csv(os.path.join(param_dir, 'RF_scores_per_ntree.csv'), index=False)

    # Save per-class AUCs
    per_class_df = pd.DataFrame(per_class_auc_results)
    per_class_df.insert(0, 'n_trees', n_trees)
    per_class_df.to_csv(os.path.join(param_dir, 'RF_per_class_auc_per_ntree.csv'), index=False)

    # Plot best per-class AUC
    plt.figure(figsize=(8, 4))
    plt.bar(best_per_class_auc.keys(), best_per_class_auc.values(), color='black')
    plt.ylabel('AUC score')
    plt.title(f'Per-class AUC at best n_trees = {best_ntree_by_auc}')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(param_dir, 'RF_per_class_auc_best_ntree.png'))
    plt.close()

    return best_ntree_by_auc, best_ntree_by_accuracy