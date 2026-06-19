# --- Risk Labeling Thresholds ---
# These thresholds are used to generate risk labels (0-3) based on environmental data.
# They should reflect conditions that contribute to pest and disease risk.

# Humidity thresholds for Gray Mold and Whitefly
HUMIDITY_CAUTION = 70.0  # Humidity % at which caution is advised
HUMIDITY_WARNING = 80.0  # Humidity % at which warning is advised
HUMIDITY_SEVERE = 90.0   # Humidity % at which severe risk is present

# Temperature thresholds for general plant health and pest activity
LOW_TEMP_THRESHOLD = 15.0 # Temperature (Celsius) below which risk increases
HIGH_TEMP_THRESHOLD = 30.0 # Temperature (Celsius) above which risk increases

# Changes in environmental factors over a short period
HUMIDITY_CHANGE_THRESHOLD = 10.0 # Absolute change in humidity % over period indicating stress
TEMP_CHANGE_THRESHOLD = 5.0      # Absolute change in temperature C over period indicating stress

# Duration of adverse conditions
HUMIDITY_DURATION_THRESHOLD = 3  # Number of consecutive observations with high humidity to trigger risk

# CO2 thresholds (placeholders, adjust based on actual data/knowledge)
LOW_CO2_THRESHOLD = 300   # ppm
HIGH_CO2_THRESHOLD = 1000 # ppm

# Light intensity thresholds (placeholders)
LOW_LIGHT_THRESHOLD = 5000 # Lux or other unit
HIGH_LIGHT_THRESHOLD = 50000 # Lux or other unit

# Combine thresholds for different risk levels (example scoring, can be refined)
# This is a general guideline; specific rules will be in labeling.py
RISK_SCORE_NORMAL = 1
RISK_SCORE_CAUTION = 2
RISK_SCORE_WARNING = 4
RISK_SCORE_SEVERE = 5