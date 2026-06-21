import requests
import os
import xml.etree.ElementTree as ET
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

from dotenv import load_dotenv
load_dotenv()
service_key = os.getenv("DATA_GO_KR_SERVICE_KEY")

def get_and_print_first_item(url, params, label):
    print(f"\n=== {label} ===")
    response = requests.get(url, params=params)
    if response.status_code == 200:
        try:
            root = ET.fromstring(response.text)
            items = root.findall('.//item')
            if items:
                first_item = items[0]
                print("First Item XML Tags and Values:")
                for child in first_item:
                    print(f"  <{child.tag}>: {child.text}")
            else:
                print("No items found.")
        except Exception as e:
            print("Error parsing XML:", e)
            print("Response:", response.text[:500])
    else:
        print(f"Failed: {response.status_code}")

# 1. V3 GnrlWeather
get_and_print_first_item(
    "https://apis.data.go.kr/1390802/AgriWeather/WeatherObsrInfo/V3/GnrlWeather/getWeatherMonDayList3",
    {
        "search_Year": "2026",
        "search_Month": "06",
        "Page_No": "1",
        "Page_Size": "1",
        "ServiceKey": service_key
    },
    "V3 GnrlWeather (getWeatherMonDayList3)"
)

# 2. V4 InsttWeather
get_and_print_first_item(
    "https://apis.data.go.kr/1390802/AgriWeather/WeatherObsrInfo/V4/InsttWeather/getWeatherTimeList4",
    {
        "date_Time": "2026-06-18",
        "Page_No": "1",
        "Page_Size": "1",
        "ServiceKey": service_key
    },
    "V4 InsttWeather (getWeatherTimeList4)"
)
