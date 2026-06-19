from typing import Dict, Any, Union
from src.api_clients.data_go_kr_client import DataGoKrClient
from config.settings import DATA_GO_KR_SERVICE_KEY

class WeatherClient(DataGoKrClient):
    """
    Client for '농촌진흥청 국립농업과학원_농업기상 관측데이터 조회' V3 (GnrlWeather) and V4 (InsttWeather).
    Uses the correct endpoints and parameter specifications:
    - V3: GnrlWeather/getWeatherMonDayList3 (Monthly observation by day)
    - V4: InsttWeather/getWeatherTimeList4 (Daily observation by hour)
    """
    def __init__(self, service_key: str = DATA_GO_KR_SERVICE_KEY):
        # Use HTTPS to avoid portal issues
        super().__init__(base_url="https://apis.data.go.kr/1390802/AgriWeather/WeatherObsrInfo", service_key=service_key)
        self.api_name_basic = "agri_weather_basic"
        self.api_name_detail = "agri_weather_detail"

    def get_basic_observation_data(self, obsr_div: str = "RDA_WEATHER", obsr_div_cd: str = "01", 
                                   start_dt: str = "", end_dt: str = "",
                                   page_no: int = 1, num_of_rows: int = 20) -> Union[str, Dict[str, Any]]:
        """
        Fetches basic observation data (V3) for a given month.
        Endpoint: V3/GnrlWeather/getWeatherMonDayList3
        Required parameters: search_Year (YYYY), search_Month (MM)
        `start_dt` format should be YYYYMMDD.
        """
        endpoint = "V3/GnrlWeather/getWeatherMonDayList3"
        
        # Ensure we have a valid start date
        if not start_dt or len(start_dt) < 6:
            raise ValueError(f"Invalid start_dt format: {start_dt}. Expected YYYYMMDD.")
            
        search_year = start_dt[:4]
        search_month = start_dt[4:6]
        
        params = {
            "search_Year": search_year,
            "search_Month": search_month,
            "Page_No": str(page_no),
            "Page_Size": str(num_of_rows),
            "ServiceKey": self.service_key  # Portal Gateway requires capital ServiceKey
        }
        
        # obsr_Spot_Cd or obsr_Spot_Nm can be optionally passed if provided.
        # Here we fetch generally and can filter or keep generic.
        
        return self.get_data(endpoint=endpoint, api_name=self.api_name_basic, 
                             extra_params=params, is_json_response=False)

    def get_detailed_observation_data(self, obsr_div: str = "RDA_WEATHER", obsr_div_cd: str = "01", 
                                      start_dt: str = "", end_dt: str = "",
                                      page_no: int = 1, num_of_rows: int = 20) -> Union[str, Dict[str, Any]]:
        """
        Fetches detailed hourly observation data (V4) for a given date.
        Endpoint: V4/InsttWeather/getWeatherTimeList4
        Required parameters: date_Time (YYYY-MM-DD)
        `start_dt` format should be YYYYMMDD.
        """
        endpoint = "V4/InsttWeather/getWeatherTimeList4"
        
        if not start_dt or len(start_dt) < 8:
            raise ValueError(f"Invalid start_dt format: {start_dt}. Expected YYYYMMDD.")
            
        search_year = start_dt[:4]
        search_month = start_dt[4:6]
        search_day = start_dt[6:8]
        date_time_param = f"{search_year}-{search_month}-{search_day}"
        
        params = {
            "date_Time": date_time_param,
            "Page_No": str(page_no),
            "Page_Size": str(num_of_rows),
            "ServiceKey": self.service_key  # Portal Gateway requires capital ServiceKey
        }
        
        return self.get_data(endpoint=endpoint, api_name=self.api_name_detail, 
                             extra_params=params, is_json_response=False)
