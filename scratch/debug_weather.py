import requests
import os
from dotenv import load_dotenv

# Load .env variables
load_dotenv()
service_key = os.getenv("DATA_GO_KR_SERVICE_KEY")

print(f"Loaded serviceKey (first 10 chars): {service_key[:10] if service_key else 'None'}")

test_cases = [
    # 1. V3 GnrlWeather with getWeatherMonDayList3 (Capital ServiceKey, search_Year, search_Month)
    {
        "url": "https://apis.data.go.kr/1390802/AgriWeather/WeatherObsrInfo/V3/GnrlWeather/getWeatherMonDayList3",
        "params": {
            "search_Year": "2026",
            "search_Month": "06",
            "Page_No": "1",
            "Page_Size": "10",
            "ServiceKey": service_key
        }
    },
    # 2. V4 InsttWeather with getWeatherTimeList4 (Capital ServiceKey, date_Time)
    {
        "url": "https://apis.data.go.kr/1390802/AgriWeather/WeatherObsrInfo/V4/InsttWeather/getWeatherTimeList4",
        "params": {
            "date_Time": "2026-06-18",
            "Page_No": "1",
            "Page_Size": "10",
            "ServiceKey": service_key
        }
    }
]

for i, case in enumerate(test_cases, 1):
    url = case["url"]
    params = case["params"]
    print(f"\n--- TEST CASE {i} ---")
    print(f"URL: {url}")
    print(f"Params (excluding key): {{k: v for k, v in params.items() if k.lower() != 'servicekey'}}")
    
    try:
        response = requests.get(url, params=params, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        if response.status_code == 200:
            print(f"Snippet (first 300 chars): {response.text[:300]}")
        else:
            print(f"Error Content: {response.text[:200]}")
    except Exception as e:
        print(f"Exception occurred: {e}")
