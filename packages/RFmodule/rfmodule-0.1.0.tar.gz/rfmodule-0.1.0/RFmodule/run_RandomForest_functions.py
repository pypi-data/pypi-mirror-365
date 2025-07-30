#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Soukaina Timouma
@email: soukaina.timouma@well.OX.AC.UK
"""
#%%
def run_RandomForest_classification_model(
    X, y, testSize,
    n_opt=None,
    max_depth_opt=None, 
    min_samples_split_opt=None, 
    min_samples_leaf_opt=None,
    max_features_opt=None, 
    bootstrap=True,
    outdir=None, 
    top_n_features=20, 
    class_weight=None, 
    cv=None
):
    """
    Run a Random Forest classifier with optional hyperparameter tuning and cross-validation.

    Parameters:
        X (pd.DataFrame): Feature matrix
        y (pd.Series): Target vector
        testSize (float): Fraction for test split
        n_opt (int or None): Number of trees (n_estimators)
        max_depth_opt (int or None): Max depth
        min_samples_split_opt (int or None): Min samples split
        min_samples_leaf_opt (int or None): Min samples leaf
        max_features_opt (str, float, int, or None): max_features
        bootstrap (bool or None): bootstrap
        outdir (str): Directory to store results
        top_n_features (int): Number of top features to plot/save
        class_weight: RF class_weight
        cv (int or None): if None, only train/test split. Otherwise, number of folds.

    Returns:
        tuple:
            - Predicted labels y_pred (np.ndarray)
            - trained classifier rf_pipeline (PMMLPipeline)
            - feature importance DataFrame
    """

    import os
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns
    from sklearn.model_selection import (
        train_test_split, 
        cross_val_predict, 
        cross_val_score, 
        StratifiedKFold
        )
    from sklearn.metrics import (
        classification_report,
        accuracy_score,
        f1_score,
        precision_score,
        recall_score,
        roc_auc_score,
        precision_recall_curve,
        roc_curve,
        confusion_matrix,
        ConfusionMatrixDisplay
        )
    from sklearn.preprocessing import label_binarize
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.pipeline import Pipeline
    from sklearn2pmml import sklearn2pmml, PMMLPipeline
    import joblib
    import warnings
    warnings.filterwarnings("ignore")

    ########################################
    # Helper functions:
    # - plot_confusion_matrix()
    # - plot_multiclass_roc()
    # - plot_multiclass_pr()
    # - plot_binary_roc()
    # - plot_binary_pr()
    # - plot_feature_importances()
    # - run_cross_validation()
    
    # -------------------------------
    # Functions
    # -------------------------------
    def plot_binary_roc(y_true, y_prob, outdir, n_opt, cw_str):
        print("Plot ROC curve (binary classes)")
        fpr, tpr, thresholds = roc_curve(y_true, y_prob)
        plt.figure()
        plt.plot(fpr, tpr, label="ROC curve")
        plt.plot([0, 1], [0, 1], linestyle="--", color="gray")
        plt.xlabel("False Positive rate")
        plt.ylabel("True Positive rate")
        plt.title("ROC curve")
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(outdir, f"roc_curve_RF_n{n_opt}_cw_{cw_str}.png"))
        plt.close()
        # Save ROC curve data
        roc_df = pd.DataFrame({
            "FalsePositiveRate": fpr,
            "TruePositiveRate": tpr,
            "Threshold": thresholds
        })
        roc_df.to_csv(
            os.path.join(outdir, f"roc_curve_data_RF_n{n_opt}_cw_{cw_str}.csv"),
            index=False
        )


    def plot_binary_pr(y_true, y_prob, outdir, n_opt, cw_str):
        print("Plot PR curve (binary classes)")
        precision, recall, thresholds = precision_recall_curve(y_true, y_prob)
        plt.figure()
        plt.plot(recall, precision, label="PR curve")
        plt.xlabel("Recall")
        plt.ylabel("Precision")
        plt.title("Precision-Recall curve")
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(outdir, f"precision_recall_curve_RF_n{n_opt}_cw_{cw_str}.png"))
        plt.close()
        # Save PR curve data
        pr_df = pd.DataFrame({
            "Threshold": np.append(thresholds, 1.0),  # PR thresholds length is N-1, append 1.0 for last point
            "Precision": precision,
            "Recall": recall
        })
        pr_df.to_csv(
            os.path.join(outdir, f"precision_recall_curve_data_RF_n{n_opt}_cw_{cw_str}.csv"),
            index=False
        )


    def plot_multiclass_roc(y_test_bin, test_probs, classes, outdir, n_opt, cw_str):
        plt.figure(figsize=(8,6))
        all_roc_data = []
        for i, cls in enumerate(classes):
            fpr, tpr, thresholds = roc_curve(y_test_bin[:, i], test_probs[:, i])
            auc_val = roc_auc_score(y_test_bin[:, i], test_probs[:, i])
            plt.plot(fpr, tpr, label=f"ROC class {cls} (AUC={auc_val:.3f})")

            # Append data for CSV
            roc_data = pd.DataFrame({
                "Class": cls,
                "FalsePositiveRate": fpr,
                "TruePositiveRate": tpr,
                "Threshold": thresholds
            })
            all_roc_data.append(roc_data)

        plt.plot([0, 1], [0, 1], linestyle="--", color="gray")
        plt.xlabel("False Positive rate")
        plt.ylabel("True Positive rate")
        plt.title("Multiclass ROC curves")
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(outdir, f"roc_curve_RF_n{n_opt}_cw_{cw_str}.png"))
        plt.close()

        roc_df = pd.concat(all_roc_data, ignore_index=True)
        roc_df.to_csv(
            os.path.join(outdir, f"roc_curve_data_RF_n{n_opt}_cw_{cw_str}.csv"),
            index=False
        )


    def plot_multiclass_pr(y_test_bin, test_probs, classes, outdir, n_opt, cw_str):
        plt.figure(figsize=(8,6))
        all_pr_data = []
        for i, cls in enumerate(classes):
            precision, recall, thresholds = precision_recall_curve(y_test_bin[:, i], test_probs[:, i])
            plt.plot(recall, precision, label=f"PR class {cls}")

            pr_data = pd.DataFrame({
                "Class": cls,
                "Threshold": np.append(thresholds, 1.0),  # Append 1.0 for last threshold
                "Precision": precision,
                "Recall": recall
            })
            all_pr_data.append(pr_data)

        plt.xlabel("Recall")
        plt.ylabel("Precision")
        plt.title("Multiclass Precision-Recall curves")
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(outdir, f"precision_recall_curve_RF_n{n_opt}_cw_{cw_str}.png"))
        plt.close()

        pr_df = pd.concat(all_pr_data, ignore_index=True)
        pr_df.to_csv(
            os.path.join(outdir, f"precision_recall_curve_data_RF_n{n_opt}_cw_{cw_str}.csv"),
            index=False
        )


    def plot_confusion_matrix(y_true, y_pred, classes, outdir, n_opt, cw_str):
        """
        Plot and save confusion matrix and also save raw matrix as CSV.
        """
        cm = confusion_matrix(y_true, y_pred, labels=classes)
        disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=classes)
        fig, ax = plt.subplots(figsize=(8,6))
        disp.plot(ax=ax, cmap="Blues", colorbar=False)
        plt.title("Confusion matrix")
        plt.tight_layout()
        plt.savefig(os.path.join(outdir, f"confusion_matrix_RF_n{n_opt}_cw_{cw_str}.png"))
        plt.close()
        # Save confusion matrix
        cm_df = pd.DataFrame(cm, index=[f"True_{cls}" for cls in classes],
                                columns=[f"Pred_{cls}" for cls in classes])
        cm_df.to_csv(
            os.path.join(outdir, f"confusion_matrix_data_RF_n{n_opt}_cw_{cw_str}.csv")
        )

    def plot_feature_importances(importance_df, top_n, outdir, n_opt, cw_str):
        """
        Plot top-N feature importances and save to PNG.
        """
        top = importance_df.head(top_n)
        plt.figure(figsize=(10,6))
        plt.barh(top["Feature"], top["Importance"])
        plt.gca().invert_yaxis()
        plt.title(f"Top {top_n} Feature importances")
        plt.tight_layout()
        plt.savefig(os.path.join(outdir, f"feature_importances_top{top_n}_RF_n{n_opt}_cw_{cw_str}.png"))
        plt.close()

    def run_cross_validation(rf_pipeline, X, y, cv, outdir, n_opt, cw_str):
        # Cross-validated accuracy
        scores = cross_val_score(rf_pipeline, X, y, cv=cv, scoring="accuracy")
        mean_acc = scores.mean()
        std_acc = scores.std()
        print(f"Mean accuracy: {mean_acc:.4f} ± {std_acc:.4f}")
        scores_df = pd.DataFrame({
            "Fold": range(1, cv+1),
            "Accuracy": scores,
            "MeanAccuracy": mean_acc,
            "StdAccuracy": std_acc
        })
        scores_df.to_csv(
            os.path.join(outdir, f"cross_val_accuracy_RF_n{n_opt}_cw_{cw_str}.csv"),
            index=False
        )
        plt.figure(figsize=(6,4))
        sns.boxplot(y=scores)
        plt.title(f"Cross-Validation accuracy (cv={cv})")
        plt.ylabel("Accuracy")
        plt.tight_layout()
        plt.savefig(os.path.join(outdir, f"cross_val_accuracy_boxplot_RF_n{n_opt}_cw_{cw_str}.png"))
        plt.close()

        # Cross-validated predictions for confusion matrix
        y_cv_pred = cross_val_predict(rf_pipeline, X, y, cv=cv)
        plot_confusion_matrix(y, y_cv_pred, np.unique(y), outdir, f"{n_opt}_cv{cv}", cw_str)
        
        
    ########################### RF Classifier ###########################
    
    os.makedirs(outdir, exist_ok=True)
    cw_str = str(class_weight).replace(" ", "").replace("{", "").replace("}", "").replace("'", "")

    # how many classes - binary or multiclass
    classes = np.unique(y)
    is_multiclass = len(classes) > 2

    # Prepare stratified split --> to make it robust to class imbalance
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=testSize,
        stratify=y,
        random_state=42
    )

    # Build kwargs dictionary with parameters (not "None") given in the function call
    rf_params = {}
    rf_params["random_state"] = 42
    if n_opt is not None:
        rf_params["n_estimators"] = n_opt
    if max_depth_opt is not None:
        rf_params["max_depth"] = max_depth_opt
    if min_samples_split_opt is not None:
        rf_params["min_samples_split"] = min_samples_split_opt
    if min_samples_leaf_opt is not None:
        rf_params["min_samples_leaf"] = min_samples_leaf_opt
    if max_features_opt is not None:
        rf_params["max_features"] = max_features_opt
    if bootstrap is not None:
        rf_params["bootstrap"] = bootstrap
    if class_weight is not None:
        rf_params["class_weight"] = class_weight

    rf_base = RandomForestClassifier(**rf_params)

    rf_pipeline = PMMLPipeline([
        ("classifier", rf_base)
    ])

    # Fit model
    rf_pipeline.fit(X_train, y_train)

    # Predict test set
    y_pred = rf_pipeline.predict(X_test)

    # Feature importance
    importances = rf_pipeline.named_steps["classifier"].feature_importances_
    importance_df = pd.DataFrame({
        "Feature": X.columns,
        "Importance": importances
    }).sort_values("Importance", ascending=False)
    importance_df.to_csv(
        os.path.join(outdir, f"feature_importances_RF_n{n_opt}_cw_{cw_str}.csv"),
        index=False
    )
    plot_feature_importances(importance_df, top_n_features, outdir, n_opt, cw_str)

    # cross-validation
    if cv is not None and cv > 1:
        run_cross_validation(rf_pipeline, X, y, cv, outdir, n_opt, cw_str)
        
    # Compute metrics
    results = {}
    
    #########################
    #### Overall metrics ####
    #########################
    
    ## Overall accuracy
    overall_acc = accuracy_score(y_test, y_pred)
    results["overall_accuracy"] = overall_acc
    print(f"Overall accuracy: {overall_acc:.4f}")
    # plot accuracy distribution
    plt.figure(figsize=(6,4))
    sns.countplot(x=y_pred)
    plt.title("Predicted labels distribution")
    plt.xlabel("Predicted labels")
    plt.ylabel("Frequency")
    plt.tight_layout()
    plt.savefig(os.path.join(outdir, f"predicted_labels_distribution_RF_n{n_opt}_cw_{cw_str}.png"))
    plt.close()
    
    ## Overall F1 Score
    overall_f1 = f1_score(y_test, y_pred, average="macro" if is_multiclass else "binary")
    results["overall_f1"] = overall_f1
    print(f"Overall F1 Score: {overall_f1:.4f}")
    # plot F1 score distribution
    f1_scores = f1_score(y_test, y_pred, average=None, labels=classes)
    plt.figure(figsize=(6,4))
    sns.barplot(x=classes, y=f1_scores)
    plt.title("F1 Score distribution")
    plt.xlabel("Classes")
    plt.ylabel("Score")
    plt.tight_layout()
    plt.savefig(os.path.join(outdir, f"f1_score_distribution_RF_n{n_opt}_cw_{cw_str}.png"))
    plt.close()
    
    ## Overall Precision
    overall_precision = precision_score(y_test, y_pred, average="macro" if is_multiclass else "binary")
    results["overall_precision"] = overall_precision
    print(f"Overall Precision: {overall_precision:.4f}")
    # plot precision distribution
    precision_scores = precision_score(y_test, y_pred, average=None, labels=classes)
    plt.figure(figsize=(6,4))
    sns.barplot(x=classes, y=precision_scores)
    plt.title("Precision distribution")
    plt.xlabel("Classes")
    plt.ylabel("Score")
    plt.tight_layout()
    plt.savefig(os.path.join(outdir, f"precision_distribution_RF_n{n_opt}_cw_{cw_str}.png"))
    plt.close()
    
    ## Overall Recall
    overall_recall = recall_score(y_test, y_pred, average="macro" if is_multiclass else "binary")
    results["overall_recall"] = overall_recall
    print(f"Overall Recall: {overall_recall:.4f}")
    # plot recall distribution
    recall_scores = recall_score(y_test, y_pred, average=None, labels=classes)
    plt.figure(figsize=(6,4))
    sns.barplot(x=classes, y=recall_scores)
    plt.title("Recall distribution")
    plt.xlabel("Classes")
    plt.ylabel("Score")
    plt.tight_layout()
    plt.savefig(os.path.join(outdir, f"recall_distribution_RF_n{n_opt}_cw_{cw_str}.png"))
    plt.close()
    
    ## Overall AUC
    if is_multiclass:
        y_test_bin = label_binarize(y_test, classes=classes)
        test_probs = rf_pipeline.predict_proba(X_test)
        overall_auc = roc_auc_score(y_test_bin, test_probs, average="macro", multi_class="ovr")
        # plot AUC distribution
        auc_scores = {}
        for i, cls in enumerate(classes):
            auc = roc_auc_score(y_test_bin[:, i], test_probs[:, i])
            auc_scores[f"class_{cls}"] = auc
    else:
        test_probs = rf_pipeline.predict_proba(X_test)[:, 1]
        overall_auc = roc_auc_score(y_test, test_probs)
        
    results["overall_auc"] = overall_auc
    print(f"Overall AUC: {overall_auc:.4f}")
    
    ############################
    #### Per-class metrics  ####
    ############################
    print(f"----Per class metrics")
    if is_multiclass:
        print(f"MULTICLASS")
        y_test_bin = label_binarize(y_test, classes=classes)
        
        # Per-class F1 score
        f1_per_class = f1_score(y_test, y_pred, average=None, labels=classes)
        results["f1_per_class"] = f1_per_class
        print("Per-class F1 Scores:")
        for cls, f1 in zip(classes, f1_per_class):
            print(f"Class {cls}: {f1:.4f}")
        
        # Per-class accuracy
        cm = confusion_matrix(y_test, y_pred, labels=classes)
        accuracy_per_class = []
        for i, cls in enumerate(classes):
            TP = cm[i, i]
            FN = cm[i, :].sum() - TP
            FP = cm[:, i].sum() - TP
            TN = cm.sum() - (TP + FN + FP)
            
            sensitivity = TP / (TP + FN) if (TP + FN) > 0 else 0.0
            specificity = TN / (TN + FP) if (TN + FP) > 0 else 0.0
            
            balanced_acc = (sensitivity + specificity) / 2
            accuracy_per_class.append(balanced_acc)
        for cls, acc in zip(classes, accuracy_per_class):
            print(f"Balanced accuracy for class {cls}: {acc:.4f}")

        # Per-class precision
        precision_per_class = precision_score(y_test, y_pred, average=None, labels=classes)
        results["precision_per_class"] = precision_per_class
        print("Per-class Precision:")
        for cls, prec in zip(classes, precision_per_class):
            print(f"Class {cls}: {prec:.4f}")
        
        # Per-class recall
        recall_per_class = recall_score(y_test, y_pred, average=None, labels=classes)
        results["recall_per_class"] = recall_per_class
        print("Per-class Recall:")
        for cls, rec in zip(classes, recall_per_class):
            print(f"Class {cls}: {rec:.4f}")
        
        # Per-class AUC
        auc_per_class = {}
        for i, cls in enumerate(classes):
            auc = roc_auc_score(
                (y_test == cls).astype(int),
                test_probs[:, i]
            )
            auc_per_class[f"class_{cls}"] = auc
            
        results["auc_per_class"] = auc_per_class
        print("Per-class AUC:")
        for cls, auc in auc_per_class.items():
            print(f"Class {cls}: {auc:.4f}")
            
        # ROC curves
        plot_multiclass_roc(y_test_bin, test_probs, classes, outdir, n_opt, cw_str)
        # PR curves
        plot_multiclass_pr(y_test_bin, test_probs, classes, outdir, n_opt, cw_str)
        
        # save metrics per class
        with open(os.path.join(outdir, f"metrics_results_RF_n{n_opt}_cw_{cw_str}.txt"), "w") as f:
            f.write("Overall metrics:\n")
            f.write(f"Overall AUC: {overall_auc:.4f}\n")
            f.write(f"Overall accuracy: {overall_acc:.4f}\n")
            f.write(f"Overall F1 Score: {overall_f1:.4f}\n")
            f.write(f"Overall Precision: {overall_precision:.4f}\n")
            f.write(f"Overall Recall: {overall_recall:.4f}\n")
            f.write("\nPer-class metrics:\n")
            for cls, auc, f1, prec, rec, acc in zip(classes, [auc_per_class[f"class_{cls}"] for cls in classes], f1_per_class, precision_per_class, recall_per_class, accuracy_per_class):
                f.write(f"Class {cls} - AUC: {auc:.4f}, F1: {f1:.4f}, Precision: {prec:.4f}, Recall: {rec:.4f}, Accuracy: {acc:.4f}\n")
        
    else: ## Binary classification
        print(f"BINARY CLASSIFICATION")
        # Per-class accuracy
        cm = confusion_matrix(y_test, y_pred)
        accuracy_per_class = []
        for i, cls in enumerate(classes):
            TP = cm[i, i]
            FN = cm[i, :].sum() - TP
            FP = cm[:, i].sum() - TP
            TN = cm.sum() - (TP + FN + FP)
            
            sensitivity = TP / (TP + FN) if (TP + FN) > 0 else 0.0
            specificity = TN / (TN + FP) if (TN + FP) > 0 else 0.0
            
            balanced_acc = (sensitivity + specificity) / 2
            accuracy_per_class.append(balanced_acc)
        for cls, acc in zip(classes, accuracy_per_class):
            print(f"Balanced accuracy for class {cls}: {acc:.4f}")
        
        # Per-class F1 Score
        f1_per_class = f1_score(y_test, y_pred, average=None, labels=classes)
        results["f1_per_class"] = f1_per_class
        print("Per-class F1 Scores:")
        for cls, f1 in zip(classes, f1_per_class):
            print(f"Class {cls}: {f1:.4f}")
        
        # Per-class Precision
        precision_per_class = precision_score(y_test, y_pred, average=None, labels=classes)
        results["precision_per_class"] = precision_per_class
        print("Per-class Precision:")
        for cls, prec in zip(classes, precision_per_class):
            print(f"Class {cls}: {prec:.4f}")
        
        # Per-class Recall
        recall_per_class = recall_score(y_test, y_pred, average=None, labels=classes)
        results["recall_per_class"] = recall_per_class
        print("Per-class Recall:")
        for cls, rec in zip(classes, recall_per_class):
            print(f"Class {cls}: {rec:.4f}")
        
        
        # ROC curves
        print("################plot_binary_roc")
        plot_binary_roc(y_test, test_probs, outdir, n_opt, cw_str)
        
        # PR curves
        plot_binary_pr(y_test, test_probs, outdir, n_opt, cw_str)
        
        # save metrics per class
        with open(os.path.join(outdir, f"metrics_results_RF_n{n_opt}_cw_{cw_str}.txt"), "w") as f:
            f.write("Overall metrics:\n")
            f.write(f"Overall AUC: {overall_auc:.4f}\n")
            f.write(f"Overall accuracy: {overall_acc:.4f}\n")
            f.write(f"Overall F1 Score: {overall_f1:.4f}\n")
            f.write(f"Overall Precision: {overall_precision:.4f}\n")
            f.write(f"Overall Recall: {overall_recall:.4f}\n")
            f.write("\nPer-class metrics:\n")
            for cls, f1, prec, rec, acc in zip(classes, f1_per_class, precision_per_class, recall_per_class, accuracy_per_class):
                f.write(f"Class {cls} - F1: {f1:.4f}, Precision: {prec:.4f}, Recall: {rec:.4f}, Accuracy: {acc:.4f}\n")
    
    ## Save classification report
    report = classification_report(y_test, y_pred, output_dict=True)
    pd.DataFrame(report).transpose().to_csv(
        os.path.join(outdir, f"classification_report_RF_n{n_opt}_cw_{cw_str}.csv")
    )
    
    # Confusion Matrix
    plot_confusion_matrix(y_test, y_pred, classes, outdir, n_opt, cw_str)

    # Save true labels and predictions for reproducibility
    pd.DataFrame({
        "TrueLabel": y_test,
        "PredictedLabel": y_pred
    }).to_csv(os.path.join(outdir, f"test_predictions_RF_n{n_opt}_cw_{cw_str}.csv"), index=False)

    probs_df = pd.DataFrame(test_probs, columns=[f"Prob_class_{cls}" for cls in classes])
    probs_df["TrueLabel"] = y_test.reset_index(drop=True)
    probs_df.to_csv(os.path.join(outdir, f"test_set_predicted_probabilities_RF_n{n_opt}_cw_{cw_str}.csv"), index=False)

    # Save the model
    try:
        joblib.dump(rf_pipeline, os.path.join(outdir, f"rf_model_n{n_opt}_cw_{cw_str}.joblib"))
    except:
        print("Model has not been saved in joblib format.")
        
    try:
        pmml_path = os.path.join(outdir, f"rf_model_n{n_opt}_cw_{cw_str}.pmml")
        sklearn2pmml(rf_pipeline, pmml_path, java_opts=["-Xms4096m","-Xmx16384m"])
    except:
        print("Model has not been saved in pmml format.")

    return y_pred, rf_pipeline, importance_df


#%%

#############################################################
#############################################################
#############################################################

#%%

def run_rf_regression_model(
    X, y, testSize,
    outDir,
    top_n_features=5
    ):
    import os
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns
    from sklearn.model_selection import train_test_split, KFold
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.pipeline import Pipeline
    from sklearn.compose import ColumnTransformer
    from sklearn.preprocessing import StandardScaler, OneHotEncoder
    from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
    from sklearn.model_selection import RandomizedSearchCV
    from scipy.stats import uniform, randint
    import joblib
    from sklearn2pmml import sklearn2pmml
    from sklearn2pmml.pipeline import PMMLPipeline

    os.makedirs(outDir, exist_ok=True)

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=testSize, random_state=42)

    # Identify categorical and numerical columns
    categorical_features = X.select_dtypes(include=['object', 'category']).columns
    numeric_features = X.select_dtypes(include=['int64', 'float64']).columns

    # Preprocessing: scale numeric features, encode categorical features
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numeric_features),
            ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), categorical_features)
        ]
    )
    
    # Define the Random Forest pipeline
    rf = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('regressor', RandomForestRegressor(random_state=42, n_jobs=-1))
    ])
    
    
    # Define the parameter grid (parameters must start with 'regressor__')
    p = X_train.shape[1]
    
    log2_features = int(np.log2(p)) if p > 1 else 1
    offset = 5

    param_grid = {
        'regressor__n_estimators': randint(10, 1500),
        'regressor__max_depth': [*range(2, log2_features + offset)] + [None],
        'regressor__max_features': [max(1, int(p / x)) for x in [3, 5, 10]] + ['sqrt', 'log2', None],
        'regressor__bootstrap': [True],
        'regressor__min_samples_split': randint(2, max(5, int(p / 2) + 1)),
        'regressor__min_samples_leaf': randint(1, max(3, int(p / 2) + 1))
    }
    
    # Run RandomizedSearchCV
    search = RandomizedSearchCV(
        rf, param_distributions=param_grid, 
        n_iter=100, cv=10, scoring='r2', 
        n_jobs=-1, verbose=0, random_state=42
    )
    
    search.fit(X_train, y_train)
    
    
    
    # Best Parameters
    print("Best Parameters:", search.best_params_)


    n_opt=search.best_params_['regressor__n_estimators']
    max_depth=search.best_params_['regressor__max_depth']
    minSample_split=search.best_params_['regressor__min_samples_split']
    minSample_leaf=search.best_params_['regressor__min_samples_leaf']
    max_features=search.best_params_['regressor__max_features']
    bootstrap=search.best_params_['regressor__bootstrap']
    
    with open(str(outDir)+"selected_hyperparameters.txt","w") as out:
        out.write('regressor__n_estimators : '+str(n_opt)+"\n")
        out.write('regressor__max_depth : '+str(max_depth)+"\n")
        out.write('regressor__min_samples_split : '+str(minSample_split)+"\n")
        out.write('regressor__min_samples_leaf : '+str(minSample_leaf)+"\n")
        out.write('regressor__max_features : '+str(max_features)+"\n")
        out.write('regressor__bootstrap : '+str(bootstrap))
        
        

    ##############################
    #--- Regression
    ##############################
    
    # Define the Random Forest pipeline
    model = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('regressor', RandomForestRegressor(n_estimators=n_opt, criterion='squared_error', max_depth=max_depth, min_samples_split=minSample_split, min_samples_leaf=minSample_leaf, max_features=max_features, bootstrap=bootstrap, random_state=42, verbose=0))
    ])

    # Train the model
    model.fit(X_train, y_train)

    print("Model fitted.")
    
    # Get feature importances
    rf_model = model.named_steps['regressor']
    
    # Get the fitted OneHotEncoder from the preprocessor
    cat_transformer_tuple = next(
        (t for t in model.named_steps['preprocessor'].transformers if t[0] == 'cat'),
        None
    )

    if cat_transformer_tuple is not None:
        cat_transformer = cat_transformer_tuple[1]
    else:
        cat_transformer = None
    
    print("Done: cat_transformer = dict(model.named_steps['preprocessor'].transformers).get('cat').")
    cat_feature_names = []
    if cat_transformer is not None:
        try:
            cat_feature_names = cat_transformer.get_feature_names_out(input_features=categorical_features)
        except Exception as e:
            print("Could not extract categorical feature names:", e)
            cat_feature_names = []
    
    
    preprocessed_features = numeric_features.tolist()
    if len(cat_feature_names) > 0:
        preprocessed_features += cat_feature_names.tolist()
    
    print("Done: preprocessed_features.")
    
    feature_importances = pd.DataFrame({
        'Feature': preprocessed_features,
        'Importance': rf_model.feature_importances_
    }).sort_values(by='Importance', ascending=False)

    print("Done: feature_importances.")
    
    # Save feature importances to a file
    feature_importances.to_csv(str(outDir)+"feature_importances.csv", index=False)
    
    # Save zero-importance features to a separate file
    zero_importance_features = feature_importances[feature_importances['Importance'] == 0]
    zero_importance_features_names = zero_importance_features['Feature']
    zero_importance_features_names.to_csv(str(outDir)+"zero_importance.txt", index=False, header=False)

    # Plot feature importances
    plt.figure(figsize=(10, 6))
    sns.barplot(data=feature_importances.head(top_n_features), x='Importance', y='Feature', palette='viridis')
    plt.title('Top '+str(top_n_features)+' feature importances')
    plt.xlabel('Importance')
    plt.ylabel('Feature')
    plt.tight_layout()
    plt.savefig(str(outDir)+"top_"+str(top_n_features)+"_important_features.png")
    
    
    # Evaluate the model
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    
    
    
    print(f"Mean Squared Error (MSE): {mse:.4f}")
    print(f"R-squared (R²): {r2:.4f}")

    with open(str(outDir)+"Performance.txt", 'w') as file:
        file.write(f"Mean Squared Error (MSE): {mse:.4f}"+"\n")
        file.write(f"R-squared (R²): {r2:.4f}"+"\n")
        file.write(f"Mean Absolute Error (MAE): {mae:.4f}\n")

    # Plot residuals
    residuals = y_test - y_pred
    plt.figure(figsize=(8, 5))
    sns.histplot(residuals, bins=30, kde=True, color='blue')
    plt.title("Residuals distribution")
    plt.xlabel("Residuals")
    plt.ylabel("Frequency")
    plt.tight_layout()
    plt.savefig(str(outDir)+"residuals_histogram.png")
    
    
    # Scatter plot of actual vs predicted values
    plt.figure(figsize=(8, 6))
    sns.scatterplot(x=y_test, y=y_pred, alpha=0.7)
    plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], color='red', linestyle='--')
    plt.xlim([y_test.min(), y_test.max()])
    plt.ylim([y_test.min(), y_test.max()])
    plt.legend(['Perfect prediction', 'Model prediction'])
    plt.title("Actual vs predicted values")
    plt.xlabel("Actual values")
    plt.ylabel("Predicted values")
    plt.tight_layout()
    plt.savefig(str(outDir)+"actual_vs_predicted.png")

    # save df of Actual vs predicted values
    results_df = pd.DataFrame({
        'Actual': y_test,
        'Predicted': y_pred,
        'Residuals': residuals
    })
    results_df.to_csv(str(outDir)+"actual_vs_predicted.csv", index=False)
    
    
    try:
        model_path = os.path.join(outDir, f"rf_model_n{n_opt}.joblib")
        joblib.dump(model, model_path)
        print(f"Model saved as joblib: {model_path}")
    except Exception as e:
        print(f"Model has not been saved in joblib format. Reason: {e}")

    try:
        sklearn2pmml(model, os.path.join(outDir, f"rf_model_n{n_opt}.pmml"),
                     java_opts=["-Xms4096m", "-Xmx16384m"])
        print("Model exported to PMML.")
    except Exception as e:
        print(f"Model has not been saved in PMML format. Reason: {e}")

    return model, feature_importances, {'mse': mse, 'r2': r2, 'mae': mae}
    

#%%