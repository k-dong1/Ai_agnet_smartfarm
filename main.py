import os
import sys

# Set stdout/stderr encoding to UTF-8 to prevent CP949 encoding errors on Windows console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass
if sys.stderr.encoding != 'utf-8':
    try:
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

import pandas as pd
from datetime import datetime, timedelta
from src.api_clients.smartfarm_client import SmartFarmClient
from src.api_clients.pest_client import PestClient
from src.api_clients.weather_client import WeatherClient
from src.preprocessing.parser import (
    parse_smartfarm_data, 
    parse_pest_data, 
    parse_weather_data,
    parse_pest_detail,
    parse_insect_detail
)
from src.preprocessing.feature_engineering import create_smartfarm_features
from src.preprocessing.labeling import label_data
from src.ml.train import train_model
from src.agent.smartfarm_agent import SmartFarmAgent
from src.report.report_generator import generate_report
from config.settings import (
    SMARTFARM_API_SERVICE_KEY, 
    PEST_API_SERVICE_KEY, 
    DATA_GO_KR_SERVICE_KEY,
    PROCESSED_DATA_DIR,
    WEATHER_DATA_DAYS,
    TARGET_STATION_CODE,
    TARGET_STATION_NAME,
    TARGET_FARM_ID
)

def main():
    print("======================================================================")
    print("      Tomato SmartFarm Pest Risk AI Agent Pipeline Initialization")
    print("======================================================================")
    
    # 1. Date setup for API calls
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    date_str_yesterday = yesterday.strftime("%Y%m%d")

    # Final data storage path
    processed_csv_path = os.path.join(PROCESSED_DATA_DIR, "processed_data.csv")

    try:
        # 2. Call Public APIs & Save Raw Responses
        # --- SmartFarm Korea ---
        print(f"\n[STEP 1] Calling SmartFarm Korea API for Farm {TARGET_FARM_ID}...")
        smartfarm_data_parsed = []
        try:
            smartfarm_client = SmartFarmClient(service_key=SMARTFARM_API_SERVICE_KEY)
            smartfarm_data_raw = smartfarm_client.get_crop_data(
                farm_id=TARGET_FARM_ID,
                crop_code="114",            # Tomato crop code
                start_date="20230101",
                end_date="20230131",
                num_of_rows=50
            )
            smartfarm_data_parsed = parse_smartfarm_data(smartfarm_data_raw)
        except Exception as sfe:
            print(f"Warning: SmartFarm Korea API call failed or timed out ({sfe}). Proceeding with Weather data fallback.")
            smartfarm_data_parsed = []
            
        print(f"-> SmartFarm Korea: Fetched and parsed {len(smartfarm_data_parsed)} items.")

        # --- NCPMS Pest Search ---
        print("\n[STEP 2] Calling NCPMS Pest XML API...")
        pest_client = PestClient(service_key=PEST_API_SERVICE_KEY)
        pest_gray_mold_raw = pest_client.search_pest(sick_name_kor="잿빛곰팡이병", crop_name="토마토")
        pest_whitefly_raw = pest_client.search_insect(insect_kor_name="담배가루이", crop_name="토마토")
        
        pest_gray_mold_parsed = parse_pest_data(pest_gray_mold_raw)
        pest_whitefly_parsed = parse_pest_data(pest_whitefly_raw)
        print(f"-> NCPMS Grey Mold: Fetched and parsed {len(pest_gray_mold_parsed)} items.")
        print(f"-> NCPMS Whitefly: Fetched and parsed {len(pest_whitefly_parsed)} items.")

        # --- NCPMS Pest Details (SVC05 & SVC07) ---
        gray_mold_detail = {}
        whitefly_detail = {}
        
        if pest_gray_mold_parsed and len(pest_gray_mold_parsed) > 0:
            sick_key = pest_gray_mold_parsed[0].get("sickKey")
            if sick_key:
                print(f"Fetching gray mold detail for sickKey: {sick_key}...")
                try:
                    detail_raw = pest_client.get_pest_detail(sick_key=sick_key)
                    gray_mold_detail = parse_pest_detail(detail_raw)
                    # Fallback image from search list
                    if not gray_mold_detail.get("images") and pest_gray_mold_parsed[0].get("oriImg"):
                        gray_mold_detail["images"] = [{
                            "url": pest_gray_mold_parsed[0].get("oriImg"),
                            "title": "잿빛곰팡이병 도감 이미지"
                        }]
                except Exception as e:
                    print(f"Warning: Failed to fetch disease detail: {e}")
                    
        if pest_whitefly_parsed and len(pest_whitefly_parsed) > 0:
            insect_key = pest_whitefly_parsed[0].get("insectKey")
            if insect_key:
                print(f"Fetching whitefly detail for insectKey: {insect_key}...")
                try:
                    detail_raw = pest_client.get_insect_detail(insect_key=insect_key)
                    whitefly_detail = parse_insect_detail(detail_raw)
                    # Fallback image from search list
                    if not whitefly_detail.get("images") and pest_whitefly_parsed[0].get("oriImg"):
                        whitefly_detail["images"] = [{
                            "url": pest_whitefly_parsed[0].get("oriImg"),
                            "title": "담배가루이 도감 이미지"
                        }]
                except Exception as e:
                    print(f"Warning: Failed to fetch insect detail: {e}")

        # --- AgriWeather Basic & Detailed (Dynamic Days Collection) ---
        print(f"\n[STEP 3] Calling Agricultural Weather Observation APIs for the last {WEATHER_DATA_DAYS} days...")
        weather_client = WeatherClient(service_key=DATA_GO_KR_SERVICE_KEY)
        weather_basic_data_parsed = []
        weather_detailed_data_parsed = []
        
        for i in range(1, WEATHER_DATA_DAYS + 1):
            target_date = today - timedelta(days=i)
            date_str = target_date.strftime("%Y%m%d")
            
            # Fetch basic
            try:
                w_basic_raw = weather_client.get_basic_observation_data(start_dt=date_str)
                w_basic_parsed = parse_weather_data(w_basic_raw)
                weather_basic_data_parsed.extend(w_basic_parsed)
            except Exception as e:
                print(f"Warning: Failed to fetch/parse weather basic for {date_str}: {e}")
                
            # Fetch detailed
            try:
                w_detail_raw = weather_client.get_detailed_observation_data(start_dt=date_str)
                w_detail_parsed = parse_weather_data(w_detail_raw)
                weather_detailed_data_parsed.extend(w_detail_parsed)
            except Exception as e:
                print(f"Warning: Failed to fetch/parse weather detailed for {date_str}: {e}")
                
        print(f"-> Weather Basic: Total fetched and parsed {len(weather_basic_data_parsed)} items.")
        print(f"-> Weather Detailed: Total fetched and parsed {len(weather_detailed_data_parsed)} items.")

        # 3. Create Features and Labels
        print("\n[STEP 4] Preprocessing and Feature Engineering...")
        combined_items = []
        
        # Add actual SmartFarm parsed items if they exist
        if smartfarm_data_parsed:
            combined_items.extend(smartfarm_data_parsed)
            
        # Map Weather Detailed items to SmartFarm feature structure with station filtering
        if weather_detailed_data_parsed:
            print("Mapping Weather Detailed (V4) records to SmartFarm sensor features...")
            
            filtered_weather = []
            if TARGET_STATION_CODE or TARGET_STATION_NAME:
                for w_item in weather_detailed_data_parsed:
                    spot_cd = str(w_item.get("obsr_Spot_Cd", ""))
                    spot_nm = str(w_item.get("obsr_Spot_Nm", ""))
                    if (TARGET_STATION_CODE and TARGET_STATION_CODE in spot_cd) or \
                       (TARGET_STATION_NAME and TARGET_STATION_NAME in spot_nm):
                        filtered_weather.append(w_item)
                
                if filtered_weather:
                    print(f"-> Filtered weather data to station (Code: {TARGET_STATION_CODE}, Name: {TARGET_STATION_NAME}). Count: {len(filtered_weather)}")
                else:
                    print(f"-> Target station (Code: {TARGET_STATION_CODE}, Name: {TARGET_STATION_NAME}) not found. Using all stations as fallback.")
                    filtered_weather = weather_detailed_data_parsed
            else:
                filtered_weather = weather_detailed_data_parsed

            for w_item in filtered_weather:
                mapped_item = {
                    "collectDate": w_item.get("date_Time"),
                    "inTemp": w_item.get("tmprt_150"),
                    "inHum": w_item.get("hd_150"),
                    "inCo2": 450.0, # Ambient default CO2
                    "inLight": 0.0, # Night / default Lux
                    "fcltyId": w_item.get("obsr_Spot_Cd"),
                    "itemCode": "080300"
                }
                combined_items.append(mapped_item)

        if not combined_items:
            raise ValueError("No actual sensor data collected from SmartFarm or Weather APIs. Cannot continue.")

        # Process features DataFrame
        features_df = create_smartfarm_features(combined_items)
        print(f"Feature matrix shape: {features_df.shape}")

        # 4. Generate Risk Labels based on thresholds
        print("\n[STEP 5] Applying Thresholds and Generating Risk Labels...")
        labeled_df = label_data(features_df)
        print("Label distribution:")
        print(labeled_df['risk_label'].value_counts())

        # Save processed dataset
        os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
        labeled_df.to_csv(processed_csv_path, index=True)
        print(f"Processed dataset saved to: {processed_csv_path}")

        # 5. Train PyTorch MLP Classifier
        print("\n[STEP 6] Running PyTorch MLP Training...")
        training_metrics = train_model(processed_csv_path, epochs=100, batch_size=8, lr=0.01)

        # 6. Run AI Agent Diagnosis on the Latest Record
        print("\n[STEP 7] Executing AI Agent Diagnostics on the latest record...")
        latest_record = labeled_df.iloc[-1].to_dict()
        
        agent = SmartFarmAgent()
        agent_result = agent.run_agent_analysis(latest_record)

        # 7. Generate Static HTML Report
        print("\n[STEP 8] Rendering Static HTML Dashboard Report...")
        
        # Determine display location name
        display_station_name = "전국 (전체)"
        if TARGET_STATION_NAME:
            display_station_name = TARGET_STATION_NAME
        elif latest_record.get("fcltyId"):
            display_station_name = f"스마트팜 농가 ({latest_record.get('fcltyId')})"
            
        report_path = generate_report(
            agent_result=agent_result, 
            metrics=training_metrics, 
            df=labeled_df, 
            output_filename="report.html",
            station_name=display_station_name,
            gray_mold_detail=gray_mold_detail,
            whitefly_detail=whitefly_detail
        )

        print("\n======================================================================")
        print("[완료] AI Agent 분석이 성공적으로 끝났습니다.")
        print(f"HTML 리포트 경로: {report_path}")
        print("======================================================================")

    except ValueError as ve:
        print(f"Configuration Error: {ve}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()