#!/usr/bin/env python3
"""
Çoklu model eğitim pipeline'ı:
- Logistic Regression
- Küçük MLP (8 nöron)
- Küçük Decision Tree
Her biri için accuracy, precision, recall, F1 ve parametre sayısını karşılaştırır.
"""
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    confusion_matrix,
    precision_recall_fscore_support,
    accuracy_score
)
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn.tree import DecisionTreeClassifier
import pickle

from features import load_dataset_from_csv


def evaluate_model(name, model, X_train, y_train, X_val, y_val):
    """
    Modeli eğit ve validation set'te değerlendir.
    """
    print(f"\n{'='*60}")
    print(f"Training: {name}")
    print('='*60)
    
    model.fit(X_train, y_train)
    y_pred = model.predict(X_val)

    acc = accuracy_score(y_val, y_pred)
    precision, recall, f1, _ = precision_recall_fscore_support(
        y_val, y_pred, average="binary", zero_division=0
    )
    cm = confusion_matrix(y_val, y_pred)

    print(f"\nConfusion matrix (Val):")
    print(cm)
    print(f"\nMetrics:")
    print(f"  Accuracy:  {acc:.4f}")
    print(f"  Precision: {precision:.4f}")
    print(f"  Recall:    {recall:.4f}")
    print(f"  F1-score:  {f1:.4f}")

    # Parametre sayısı tahmini
    n_params = None
    if isinstance(model, LogisticRegression):
        n_params = model.coef_.size + model.intercept_.size
    elif isinstance(model, MLPClassifier):
        n_params = 0
        for w, b in zip(model.coefs_, model.intercepts_):
            n_params += w.size + b.size
    elif isinstance(model, DecisionTreeClassifier):
        n_params = model.tree_.node_count * 4  # yaklaşık

    if n_params is not None:
        size_bytes = n_params * 4  # float32
        print(f"\nModel size:")
        print(f"  Param count: {n_params}")
        print(f"  Float32 size: {size_bytes} bytes (~{size_bytes/1024:.2f} KB)")

    return {
        "name": name,
        "model": model,
        "acc": acc,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "n_params": n_params
    }


def main():
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    csv_path = os.path.join(project_dir, "http_requests_labeled.csv")
    
    print("[*] Loading dataset from CSV...")
    X, y = load_dataset_from_csv(csv_path)
    X = np.array(X, dtype=np.float32)
    y = np.array(y, dtype=np.int32)

    print(f"[+] Loaded {len(X)} samples")
    print(f"    Features: {X.shape[1]}")
    print(f"    Benign: {np.sum(y == 0)}, Malicious: {np.sum(y == 1)}")

    # Train/Val/Test split
    print("\n[*] Splitting dataset...")
    X_train, X_tmp, y_train, y_tmp = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y
    )
    X_val, X_test, y_val, y_test = train_test_split(
        X_tmp, y_tmp, test_size=0.5, random_state=42, stratify=y_tmp
    )

    print(f"    Train: {len(X_train)}, Val: {len(X_val)}, Test: {len(X_test)}")

    # Feature scaling
    print("\n[*] Scaling features...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_val_scaled = scaler.transform(X_val)
    X_test_scaled = scaler.transform(X_test)

    results = []

    # 1) Logistic Regression
    logreg = LogisticRegression(
        max_iter=1000,
        class_weight="balanced",
        solver="lbfgs",
        random_state=42
    )
    results.append(
        evaluate_model(
            "LogisticRegression",
            logreg,
            X_train_scaled, y_train,
            X_val_scaled, y_val
        )
    )

    # 2) Küçük MLP (8 nöron)
    mlp8 = MLPClassifier(
        hidden_layer_sizes=(8,),
        activation="relu",
        solver="adam",
        alpha=1e-4,
        batch_size=64,
        learning_rate_init=1e-3,
        max_iter=50,
        random_state=42
    )
    results.append(
        evaluate_model(
            "MLP(8)",
            mlp8,
            X_train_scaled, y_train,
            X_val_scaled, y_val
        )
    )

    # 3) Biraz daha büyük MLP (16 nöron)
    mlp16 = MLPClassifier(
        hidden_layer_sizes=(16,),
        activation="relu",
        solver="adam",
        alpha=1e-4,
        batch_size=64,
        learning_rate_init=1e-3,
        max_iter=50,
        random_state=42
    )
    results.append(
        evaluate_model(
            "MLP(16)",
            mlp16,
            X_train_scaled, y_train,
            X_val_scaled, y_val
        )
    )

    # 4) Küçük Decision Tree
    tree = DecisionTreeClassifier(
        max_depth=5,
        min_samples_leaf=10,
        random_state=42,
        class_weight="balanced"
    )
    results.append(
        evaluate_model(
            "DecisionTree(max_depth=5)",
            tree,
            X_train, y_train,  # tree için scaling şart değil
            X_val, y_val
        )
    )

    # En iyi modeli seç (F1'e göre)
    print("\n" + "="*60)
    print("MODEL COMPARISON (Validation F1)")
    print("="*60)
    for r in results:
        print(f"{r['name']:30s} | F1: {r['f1']:.4f} | Params: {r['n_params']}")

    best = max(results, key=lambda r: r["f1"])
    print("\n" + "="*60)
    print(f"BEST MODEL: {best['name']} (F1: {best['f1']:.4f})")
    print("="*60)

    # Test set üzerinde final değerlendirme
    print("\n[*] Evaluating best model on TEST set...")
    if isinstance(best["model"], DecisionTreeClassifier):
        X_test_used = X_test
    else:
        X_test_used = X_test_scaled

    y_test_pred = best["model"].predict(X_test_used)
    acc = accuracy_score(y_test, y_test_pred)
    precision, recall, f1, _ = precision_recall_fscore_support(
        y_test, y_test_pred, average="binary", zero_division=0
    )
    cm = confusion_matrix(y_test, y_test_pred)

    print(f"\nConfusion matrix (Test):")
    print(cm)
    print(f"\nTest Metrics:")
    print(f"  Accuracy:  {acc:.4f}")
    print(f"  Precision: {precision:.4f}")
    print(f"  Recall:    {recall:.4f}")
    print(f"  F1-score:  {f1:.4f}")

    # Model ve scaler'ı kaydet
    print("\n[*] Saving best model and scaler...")
    model_path = os.path.join(script_dir, "best_model.pkl")
    scaler_path = os.path.join(script_dir, "scaler.pkl")
    
    with open(model_path, "wb") as f:
        pickle.dump(best["model"], f)
    with open(scaler_path, "wb") as f:
        pickle.dump(scaler, f)
    
    print("[+] Saved:")
    print("    - best_model.pkl")
    print("    - scaler.pkl")
    print("\n[+] Training complete!")


if __name__ == "__main__":
    main()
