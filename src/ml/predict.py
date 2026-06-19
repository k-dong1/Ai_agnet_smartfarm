import os
import pickle
import torch
import torch.nn.functional as F
import numpy as np
from src.ml.model import SmartFarmMLP
from config.settings import MODELS_DIR

def predict_risk(feature_dict: dict) -> tuple:
    """
    Predicts the pest risk level and class probabilities for a single environmental sensor observation.
    
    Args:
        feature_dict: A dictionary containing keys:
            ['temperature', 'humidity', 'light', 'co2', 'humidity_duration', 'temp_change', 'humidity_change']
            
    Returns:
        tuple: (pred_label: int, probabilities: dict)
    """
    model_path = os.path.join(MODELS_DIR, "smartfarm_mlp.pt")
    scaler_path = os.path.join(MODELS_DIR, "scaler.pkl")
    
    if not os.path.exists(model_path) or not os.path.exists(scaler_path):
        raise FileNotFoundError("Model or scaler file not found. Please train the model first.")

    # Load scaler
    with open(scaler_path, "rb") as f:
        scaler = pickle.load(f)

    # Prepare inputs in correct order
    feature_keys = ['temperature', 'humidity', 'light', 'co2', 'humidity_duration', 'temp_change', 'humidity_change']
    input_values = [feature_dict.get(key, 0.0) for key in feature_keys]
    
    # Scale inputs
    input_array = np.array(input_values).reshape(1, -1)
    scaled_input = scaler.transform(input_array)
    
    # Initialize and load model
    model = SmartFarmMLP(input_dim=len(feature_keys), output_dim=4)
    model.load_state_dict(torch.load(model_path))
    model.eval()
    
    # Run prediction
    with torch.no_grad():
        input_tensor = torch.tensor(scaled_input, dtype=torch.float32)
        outputs = model(input_tensor)
        probabilities_tensor = F.softmax(outputs, dim=1)
        
        probabilities = probabilities_tensor.squeeze().tolist()
        pred_label = torch.argmax(outputs, dim=1).item()
        
    labels_map = ["정상", "주의", "경고", "심각"]
    prob_dict = {labels_map[i]: probabilities[i] for i in range(4)}
    
    return pred_label, prob_dict
