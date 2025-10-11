#!/usr/bin/env python3
"""
train_model.py

Usage:
    python train_model.py

Outputs (into ./models and ./outputs):
 - models/baseline_model.pkl
 - models/scaler.pkl
 - models/label_encoder.pkl
 - outputs/correlation_heatmap.png
 - outputs/feature_importances.png
 - outputs/classification_report.txt
"""

import os
import joblib
import argparse
from datetime import datetime

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix

# --- Config ---
DATA_PATH = os.path.join("data", "Crop Recommendation using Soil Properties and Weather Prediction.csv")
MODELS_DIR = "models"
OUTPUTS_DIR = "outputs"
RANDOM_STATE = 42

os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(OUTPUTS_DIR, exist_ok=True)

def load_data(path=DATA_PATH):
    print(f"[{datetime.now()}] Loading data from: {path}")
    df = pd.read_csv(path)
    print(f"[{datetime.now()}] Data shape: {df.shape}")
    return df

def select_target(df):
    # heuristics: look for columns like 'label' or containing 'crop' or 'recommend'
    candidates = [c for c in df.columns if 'crop' in c.lower() or 'label' in c.lower() or 'recommend' in c.lower()]
    if not candidates:
        raise ValueError("No target column found. Check column names for 'label' or 'crop'. Columns: " + ", ".join(df.columns))
    target = candidates[0]
    print(f"[{datetime.now()}] Selected target column: '{target}'")
    return target

def prepare_features(df, target_col):
    # numeric features only for baseline
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    # exclude target if numeric
    if target_col in numeric_cols:
        numeric_cols.remove(target_col)
    print(f"[{datetime.now()}] Numeric features used ({len(numeric_cols)}): {numeric_cols[:10]}{'...' if len(numeric_cols)>10 else ''}")
    X = df[numeric_cols].copy()
    # fill missing with median
    X = X.fillna(X.median())
    return X, numeric_cols

def save_plots(df, numeric_cols, model, feature_names):
    # correlation heatmap
    corr = df[numeric_cols].corr()
    plt.figure(figsize=(10,8))
    sns.heatmap(corr, cmap="vlag", center=0)
    heatmap_path = os.path.join(OUTPUTS_DIR, "correlation_heatmap.png")
    plt.title("Correlation heatmap (numeric features)")
    plt.tight_layout()
    plt.savefig(heatmap_path)
    plt.close()
    print(f"[{datetime.now()}] Saved correlation heatmap -> {heatmap_path}")

    # feature importances
    if model is not None:
        importances = model.feature_importances_
        fi = pd.Series(importances, index=feature_names).sort_values(ascending=False)
        topk = fi.head(25)
        plt.figure(figsize=(8, max(4, 0.25*len(topk))))
        topk.plot(kind='bar')
        plt.title("Feature importances (trained model)")
        plt.tight_layout()
        fi_path = os.path.join(OUTPUTS_DIR, "feature_importances.png")
        plt.savefig(fi_path)
        plt.close()
        print(f"[{datetime.now()}] Saved feature importances -> {fi_path}")

def train_and_evaluate(X, y, feature_names):
    # encode target
    le = LabelEncoder()
    y_enc = le.fit_transform(y.astype(str))

    # scale numeric features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # train/test split
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y_enc,
                                                        test_size=0.20,
                                                        random_state=RANDOM_STATE,
                                                        stratify=y_enc)
    print(f"[{datetime.now()}] Train shape: {X_train.shape}, Test shape: {X_test.shape}")

    # baseline model
    clf = RandomForestClassifier(n_estimators=200, random_state=RANDOM_STATE, class_weight='balanced', n_jobs=-1)
    clf.fit(X_train, y_train)

    # predict
    y_pred = clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, target_names=le.classes_, zero_division=0)
    cm = confusion_matrix(y_test, y_pred)

    print(f"[{datetime.now()}] Baseline accuracy: {acc:.4f}")
    # save classification report
    report_path = os.path.join(OUTPUTS_DIR, "classification_report.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"Accuracy: {acc:.4f}\n\n")
        f.write(report)
        f.write("\n\nConfusion matrix:\n")
        f.write(np.array2string(cm))
    print(f"[{datetime.now()}] Saved classification report -> {report_path}")

    # save artifacts
    joblib.dump(clf, os.path.join(MODELS_DIR, "baseline_model.pkl"))
    joblib.dump(scaler, os.path.join(MODELS_DIR, "scaler.pkl"))
    joblib.dump(le, os.path.join(MODELS_DIR, "label_encoder.pkl"))
    # save feature names
    joblib.dump(feature_names, os.path.join(MODELS_DIR, "feature_names.pkl"))

    print(f"[{datetime.now()}] Saved model & preprocessing artifacts -> {MODELS_DIR}/")
    return clf, scaler, le, acc, report, cm

def main():
    df = load_data()
    target = select_target(df)
    X, numeric_cols = prepare_features(df, target)
    y = df[target]

    clf, scaler, le, acc, report, cm = train_and_evaluate(X, y, numeric_cols)
    save_plots(df, numeric_cols, clf, numeric_cols)

    print("[DONE] Training pipeline finished. Artifacts under 'models' and 'outputs'.")

if __name__ == "__main__":
    main()
