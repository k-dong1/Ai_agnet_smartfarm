import pandas as pd
import numpy as np
from typing import List, Dict, Any
from config.thresholds import HUMIDITY_WARNING, HUMIDITY_DURATION_THRESHOLD

def create_smartfarm_features(data: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Creates MLP input features from parsed SmartFarm data.
    Assumes 'data' is a list of dictionaries with keys like 'collectDate', 'outTemp', 'outHum', 'inCo2', etc.
    Missing values will be handled (e.g., imputed or dropped).
    """
    if not data:
        return pd.DataFrame()

    df = pd.DataFrame(data)

    # Convert relevant columns to numeric, coercing errors to NaN
    numeric_cols = ['outTemp', 'outHum', 'inCo2', 'inLight', 'inTemp', 'inHum'] # Example sensor data
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Convert collection date to datetime and set as index
    if 'collectDate' in df.columns:
        df['collectDate'] = pd.to_datetime(df['collectDate'])
        df = df.sort_values('collectDate').set_index('collectDate')
    else:
        print("Warning: 'collectDate' column not found for sorting.")
        # If no datetime index, some feature engineering might not make sense, e.g., 'change' features.

    # Handle missing CO2: Option 1: exclude, Option 2: impute with median/mean
    # For now, we will impute with median, but this should be configurable.
    if 'inCo2' in df.columns and df['inCo2'].isnull().all():
        print("Warning: 'inCo2' column is entirely missing. It might be excluded or imputed differently.")
        # Option 1: Drop 'inCo2' if entirely missing
        # df = df.drop(columns=['inCo2']) 
        # Or just let it be NaN for now and handle in ML part
    elif 'inCo2' in df.columns:
        df['inCo2'] = df['inCo2'].fillna(df['inCo2'].median())

    # Fill other missing numeric values with median (or mean, or more sophisticated methods)
    for col in numeric_cols:
        if col in df.columns and df[col].isnull().any():
            df[col] = df[col].fillna(df[col].median())


    # --- Feature Engineering ---
    # 1. Temperature Change (assuming 'inTemp' is the primary temperature sensor)
    if 'inTemp' in df.columns:
        df['temp_change'] = df['inTemp'].diff().fillna(0) # Change from previous observation
    else:
        df['temp_change'] = 0 # Default if column not present

    # 2. Humidity Change (assuming 'inHum' is the primary humidity sensor)
    if 'inHum' in df.columns:
        df['humidity_change'] = df['inHum'].diff().fillna(0) # Change from previous observation
    else:
        df['humidity_change'] = 0 # Default if column not present

    # 3. Humidity Duration (consecutive high humidity)
    if 'inHum' in df.columns:
        # Identify periods of high humidity
        high_humidity = df['inHum'] >= HUMIDITY_WARNING
        # Group consecutive True values and count them
        df['humidity_duration'] = high_humidity.astype(int).groupby(high_humidity.ne(high_humidity.shift()).cumsum()).cumsum()
        df.loc[~high_humidity, 'humidity_duration'] = 0 # Reset count when humidity drops below threshold
    else:
        df['humidity_duration'] = 0 # Default if column not present


    # Rename columns to standardized feature names
    # This mapping is an assumption and needs to be verified with actual API response keys
    feature_mapping = {
        'inTemp': 'temperature',
        'inHum': 'humidity',
        'inLight': 'light',
        'inCo2': 'co2',
    }
    df = df.rename(columns=feature_mapping)

    # Select final MLP input features
    # Ensure all target features are present, fill with 0 or a reasonable default if not
    target_features = ['temperature', 'humidity', 'light', 'co2', 'humidity_duration', 'temp_change', 'humidity_change']
    for feature in target_features:
        if feature not in df.columns:
            df[feature] = 0.0 # Default value if feature is completely missing

    # Keep only the target features
    df = df[target_features]
    
    return df

def create_pest_features(data: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Creates features from parsed Pest data.
    Pest data is likely descriptive and might not directly generate numeric MLP features.
    This function primarily processes and cleans descriptive text.
    """
    if not data:
        return pd.DataFrame()
    df = pd.DataFrame(data)
    # TODO: Further process pest description text (e.g., TF-IDF, embeddings) if needed for advanced agent
    return df

def create_weather_features(data: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Creates MLP input features from parsed weather data.
    Similar to SmartFarm data, but with weather-specific keys.
    """
    if not data:
        return pd.DataFrame()
    df = pd.DataFrame(data)

    # Convert relevant columns to numeric, coercing errors to NaN
    # Example: 'avgTa' (Avg Temperature), 'avgWs' (Avg Wind Speed), 'sumRn' (Total Rainfall)
    numeric_cols = ['avgTa', 'avgWs', 'sumRn'] 
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    if 'ymd' in df.columns: # Assuming 'ymd' for basic weather data date
        df['ymd'] = pd.to_datetime(df['ymd'])
        df = df.sort_values('ymd').set_index('ymd')
    elif 'date' in df.columns: # Assuming 'date' for detailed weather data date/time
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date').set_index('date')

    # Fill missing numeric values with median
    for col in numeric_cols:
        if col in df.columns and df[col].isnull().any():
            df[col] = df[col].fillna(df[col].median())

    # Example: Temperature change from weather data
    if 'avgTa' in df.columns:
        df['weather_temp_change'] = df['avgTa'].diff().fillna(0)
    else:
        df['weather_temp_change'] = 0

    return df

# TODO: Refine feature names and logic based on actual API response keys and domain knowledge.
