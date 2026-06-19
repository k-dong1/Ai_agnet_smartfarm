import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

# --- API Keys ---
SMARTFARM_API_SERVICE_KEY = os.getenv("SMARTFARM_API_SERVICE_KEY")
if not SMARTFARM_API_SERVICE_KEY:
    raise ValueError("SMARTFARM_API_SERVICE_KEY environment variable not set. Please create a .env file or set the environment variable.")

PEST_API_SERVICE_KEY = os.getenv("PEST_API_SERVICE_KEY")
if not PEST_API_SERVICE_KEY:
    raise ValueError("PEST_API_SERVICE_KEY environment variable not set. Please create a .env file or set the environment variable.")

DATA_GO_KR_SERVICE_KEY = os.getenv("DATA_GO_KR_SERVICE_KEY")
if not DATA_GO_KR_SERVICE_KEY:
    raise ValueError("DATA_GO_KR_SERVICE_KEY environment variable not set. Please create a .env file or set the environment variable.")

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "90")) # seconds

# --- Location & Period Configuration ---
WEATHER_DATA_DAYS = int(os.getenv("WEATHER_DATA_DAYS", "30"))
TARGET_STATION_CODE = os.getenv("TARGET_STATION_CODE", "")
TARGET_STATION_NAME = os.getenv("TARGET_STATION_NAME", "")
TARGET_FARM_ID = os.getenv("TARGET_FARM_ID", "M2103_001_001_01")

# --- Base Directories ---
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
CACHE_DIR = DATA_DIR / "cache"
MODELS_DIR = BASE_DIR / "models"
OUTPUT_DIR = BASE_DIR / "output"

# Ensure directories exist (they should already exist from the initial setup, but good to double check)
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# --- Public Data API Endpoints ---
# (URLs will be filled or refined as specific clients are implemented)
SMARTFARM_API_URL = "https://www.data.go.kr/data/15121325/openapi.do" # Placeholder - actual endpoint will be more specific
PEST_SEARCH_API_URL = "https://www.data.go.kr/data/15058504/openapi.do" # Placeholder
PEST_DICTIONARY_API_URL = "https://www.data.go.kr/data/15002034/openapi.do" # Placeholder
SMARTFARM_MODEL_API_URL = "https://www.data.go.kr/data/15125691/openapi.do" # Placeholder
WEATHER_OBSERVATION_BASIC_API_URL = "https://www.data.go.kr/data/15078057/openapi.do" # Placeholder
WEATHER_OBSERVATION_DETAIL_API_URL = "https://www.data.go.kr/data/15078194/openapi.do" # Placeholder

# --- Other Constants ---
# Add other constants here as needed