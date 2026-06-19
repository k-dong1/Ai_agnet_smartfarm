import os
import json
import pickle
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from src.ml.model import SmartFarmMLP
from src.ml.dataset import SmartFarmDataset
from config.settings import MODELS_DIR, OUTPUT_DIR

def train_model(data_path: str, epochs: int = 50, batch_size: int = 16, lr: float = 0.01):
    print("\n--- Starting MLP Model Training ---")
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Processed data file not found: {data_path}")

    # Load labeled dataset
    df = pd.read_csv(data_path)
    if df.empty:
        raise ValueError("Processed dataset is empty. Cannot train model.")

    feature_cols = ['temperature', 'humidity', 'light', 'co2', 'humidity_duration', 'temp_change', 'humidity_change']
    
    # Ensure all required features exist
    for col in feature_cols:
        if col not in df.columns:
            df[col] = 0.0

    X = df[feature_cols].values
    y = df['risk_label'].values

    num_samples = len(df)
    print(f"Loaded {num_samples} samples for training.")

    # Robust handling for small datasets
    if num_samples < 5:
        print("Warning: The dataset is extremely small (< 5). Training might not be accurate.")
        X_train, X_test, y_train, y_test = X, X, y, y
    elif num_samples < 20:
        print("Warning: Dataset is small (< 20). Splitting with a small test size.")
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=42, stratify=None)
    else:
        # Standard split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=None)

    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Create PyTorch datasets and dataloaders
    train_dataset = SmartFarmDataset(X_train_scaled, y_train)
    test_dataset = SmartFarmDataset(X_test_scaled, y_test)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

    # Initialize model
    input_dim = len(feature_cols)
    model = SmartFarmMLP(input_dim=input_dim, output_dim=4)
    
    # Loss and Optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)

    # Training loop
    model.train()
    history = []
    for epoch in range(1, epochs + 1):
        epoch_loss = 0.0
        for batch_X, batch_y in train_loader:
            optimizer.zero_grad()
            outputs = model(batch_X)
            loss = criterion(outputs, batch_y)
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item() * len(batch_X)
        
        epoch_loss /= len(train_dataset)
        history.append(epoch_loss)
        if epoch % 10 == 0 or epoch == 1:
            print(f"Epoch [{epoch}/{epochs}] - Loss: {epoch_loss:.4f}")

    # Evaluate on test set
    model.eval()
    with torch.no_grad():
        test_inputs = torch.tensor(X_test_scaled, dtype=torch.float32)
        test_targets = torch.tensor(y_test, dtype=torch.long)
        
        if len(test_targets) > 0:
            test_outputs = model(test_inputs)
            _, predicted = torch.max(test_outputs, 1)
            correct = (predicted == test_targets).sum().item()
            accuracy = correct / len(test_targets)
        else:
            accuracy = 0.0
        print(f"Test Accuracy: {accuracy * 100:.2f}%")

    # Ensure output directories exist
    os.makedirs(MODELS_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    model_path = os.path.join(MODELS_DIR, "smartfarm_mlp.pt")
    scaler_path = os.path.join(MODELS_DIR, "scaler.pkl")
    metrics_path = os.path.join(OUTPUT_DIR, "training_metrics.json")

    # Save model weights
    torch.save(model.state_dict(), model_path)
    
    # Save standardizer
    with open(scaler_path, "wb") as f:
        pickle.dump(scaler, f)

    # Calculate Feature Importances (XAI)
    try:
        # network[0] is the first nn.Linear(input_dim, hidden1)
        first_layer_weights = model.network[0].weight.data.abs().cpu().numpy() # Shape [16, 7]
        mean_weights = np.mean(first_layer_weights, axis=0) # Shape [7]
        normalized_importance = (mean_weights / np.sum(mean_weights)) * 100.0
        
        importance_dict = {
            feature_cols[i]: float(normalized_importance[i])
            for i in range(len(feature_cols))
        }
    except Exception as e:
        print(f"Warning: Failed to compute feature importances from weights: {e}")
        importance_dict = {f: 14.28 for f in feature_cols} # Even split fallback

    # Save training metrics
    metrics = {
        "final_train_loss": history[-1],
        "test_accuracy": accuracy,
        "num_samples": num_samples,
        "epochs": epochs,
        "loss_history": history,
        "feature_importance": importance_dict
    }
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=4)

    print(f"Model saved to: {model_path}")
    print(f"Scaler saved to: {scaler_path}")
    print(f"Metrics saved to: {metrics_path}")

    return metrics
