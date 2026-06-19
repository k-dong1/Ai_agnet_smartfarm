import sys
from datetime import datetime, timedelta
from src.api_clients.smartfarm_client import SmartFarmClient
from src.api_clients.pest_client import PestClient
from src.api_clients.weather_client import WeatherClient
from src.preprocessing.parser import parse_smartfarm_data, parse_pest_data, parse_weather_data
from src.preprocessing.feature_engineering import create_smartfarm_features
from config.settings import SMARTFARM_API_SERVICE_KEY, PEST_API_SERVICE_KEY

def main():
    print("[STEP 0] Initializing and testing API Clients and Preprocessing...")
    
    # --- Date setup for API calls ---
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    date_str_today = today.strftime("%Y%m%d")
    date_str_yesterday = yesterday.strftime("%Y%m%d")

    try:
        # --- Test SmartFarmClient ---
        print("\n--- Testing SmartFarmClient ---")
        smartfarm_client = SmartFarmClient(service_key=SMARTFARM_API_SERVICE_KEY)
        # Using example parameters for tomato data
        smartfarm_data_raw = smartfarm_client.get_crop_data(
            farm_id="M2103_001_001_01", # Example Farm ID
            crop_code="114",            # Tomato crop code
            # start_date=date_str_yesterday,
            # end_date=date_str_yesterday,
            start_date = "20230101",
            end_date = "20230131",
            num_of_rows=50
        )
        print(f"SmartFarm API Call Successful. Raw response saved. Data type: {type(smartfarm_data_raw)}")
        
        # Parse SmartFarm data
        smartfarm_data_parsed = parse_smartfarm_data(smartfarm_data_raw)
        print(f"SmartFarm Data Parsed. Number of items: {len(smartfarm_data_parsed)}")
        if smartfarm_data_parsed:
            print("First parsed SmartFarm item:", smartfarm_data_parsed[0])
            # Create features for SmartFarm data
            smartfarm_features_df = create_smartfarm_features(smartfarm_data_parsed)
            print("SmartFarm Features DataFrame head:\n", smartfarm_features_df.head())
        else:
            print("No SmartFarm data to parse or create features from.")


        # --- Test PestClient ---
        print("\n--- Testing PestClient ---")
        pest_client = PestClient(service_key=PEST_API_SERVICE_KEY)
        # Search for Grey Mold (잿빛곰팡이병) and Whitefly (담배가루이)
        pest_gray_mold_raw = pest_client.search_pest(pest_name="잿빛곰팡이병", crop_name="토마토")
        print(f"Pest (Grey Mold) API Call Successful. Raw response saved. Data type: {type(pest_gray_mold_raw)}")
        pest_gray_mold_parsed = parse_pest_data(pest_gray_mold_raw)
        print(f"Pest (Grey Mold) Data Parsed. Number of items: {len(pest_gray_mold_parsed)}")
        if pest_gray_mold_parsed:
            print("First parsed Pest (Grey Mold) item:", pest_gray_mold_parsed[0])


        pest_whitefly_raw = pest_client.search_pest(pest_name="담배가루이", crop_name="토마토")
        print(f"Pest (Whitefly) API Call Successful. Raw response saved. Data type: {type(pest_whitefly_raw)}")
        pest_whitefly_parsed = parse_pest_data(pest_whitefly_raw)
        print(f"Pest (Whitefly) Data Parsed. Number of items: {len(pest_whitefly_parsed)}")
        if pest_whitefly_parsed:
            print("First parsed Pest (Whitefly) item:", pest_whitefly_parsed[0])


        # --- Test WeatherClient ---
        print("\n--- Testing WeatherClient ---")
        weather_client = WeatherClient(service_key=PEST_API_SERVICE_KEY)
        # Fetch basic observation data (example: RDA_WEATHER, '01' for basic)
        weather_basic_data_raw = weather_client.get_basic_observation_data(
            obsr_div="RDA_WEATHER", 
            obsr_div_cd="01", # Basic observation
            start_dt=date_str_yesterday, 
            end_dt=date_str_yesterday
        )
        print(f"Weather Basic API Call Successful. Raw response saved. Data type: {type(weather_basic_data_raw)}")
        weather_basic_data_parsed = parse_weather_data(weather_basic_data_raw)
        print(f"Weather Basic Data Parsed. Number of items: {len(weather_basic_data_parsed)}")
        if weather_basic_data_parsed:
            print("First parsed Weather Basic item:", weather_basic_data_parsed[0])


        weather_detailed_data_raw = weather_client.get_detailed_observation_data(
            obsr_div="RDA_WEATHER", 
            obsr_div_cd="01", # Basic observation (might need different code for detailed)
            start_dt=date_str_yesterday, 
            end_dt=date_str_yesterday
        )
        print(f"Weather Detailed API Call Successful. Raw response saved. Data type: {type(weather_detailed_data_raw)}")
        weather_detailed_data_parsed = parse_weather_data(weather_detailed_data_raw)
        print(f"Weather Detailed Data Parsed. Number of items: {len(weather_detailed_data_parsed)}")
        if weather_detailed_data_parsed:
            print("First parsed Weather Detailed item:", weather_detailed_data_parsed[0])


    except ValueError as ve:
        print(f"Configuration Error: {ve}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred during API call or preprocessing test: {e}", file=sys.stderr)
        sys.exit(1)

    print("\n[STEP 2] Day 2 tasks verification (API calls, parsing, initial feature engineering) complete.")

if __name__ == "__main__":
    main()