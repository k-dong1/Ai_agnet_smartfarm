import pandas as pd
from config.thresholds import (
    HUMIDITY_CAUTION,
    HUMIDITY_SEVERE,
    LOW_TEMP_THRESHOLD,
    HUMIDITY_CHANGE_THRESHOLD,
    TEMP_CHANGE_THRESHOLD
)

def make_risk_label(row: pd.Series) -> int:
    """
    Computes a risk label (0 = Normal, 1 = Caution, 2 = Warning, 3 = Severe)
    based on environmental sensor features of a single observation row.
    """
    score = 0

    # Extract values safely with defaults
    humidity = row.get("humidity", 0.0)
    temperature = row.get("temperature", 20.0)
    humidity_duration = row.get("humidity_duration", 0)
    humidity_change = row.get("humidity_change", 0.0)
    temp_change = row.get("temp_change", 0.0)

    # 1. High humidity check
    if humidity >= HUMIDITY_CAUTION:
        score += 1
    if humidity >= HUMIDITY_SEVERE:
        score += 1

    # 2. Low temperature check (increases mold risk)
    if temperature <= LOW_TEMP_THRESHOLD:
        score += 1

    # 3. High humidity duration check (consecutive high humidity observations)
    if humidity_duration >= 3:
        score += 1

    # 4. Stress check (sudden shifts in humidity or temperature)
    if abs(humidity_change) >= HUMIDITY_CHANGE_THRESHOLD:
        score += 1
    if abs(temp_change) >= TEMP_CHANGE_THRESHOLD:
        score += 1

    # Classify final risk label based on cumulative score
    if score <= 1:
        return 0  # 정상 (Normal)
    elif score == 2:
        return 1  # 주의 (Caution)
    elif score <= 4:
        return 2  # 경고 (Warning)
    else:
        return 3  # 심각 (Severe)

def label_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Applies the risk labeling rule to the given DataFrame.
    Adds a 'risk_label' column.
    """
    if df.empty:
        return df
        
    df_labeled = df.copy()
    # Apply row-wise labeling
    df_labeled["risk_label"] = df_labeled.apply(make_risk_label, axis=1)
    return df_labeled
