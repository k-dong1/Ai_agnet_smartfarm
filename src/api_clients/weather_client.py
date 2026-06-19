from typing import Dict, Any, Union
from src.api_clients.data_go_kr_client import DataGoKrClient
from config.settings import PEST_API_SERVICE_KEY

class WeatherClient(DataGoKrClient):
    """
    Client for '농촌진흥청 국립농업과학원_농업기상 관측데이터 조회' services.
    Includes basic and detailed observation data.
    Basic URL: https://www.data.go.kr/data/15078057/openapi.do
    Detailed URL: https://www.data.go.kr/data/15078194/openapi.do
    """
    def __init__(self, service_key: str = PEST_API_SERVICE_KEY):
        # Using a generic base_url for AgriWeather and specifying endpoints in methods
        super().__init__(base_url="http://apis.data.go.kr/1390804/AgriWeather", service_key=service_key)
        self.api_name_basic = "agri_weather_basic"
        self.api_name_detail = "agri_weather_detail"
        
        # Override default_params for this API to request JSON
        self.default_params = {
            "pageNo": "1",
            "numOfRows": "10",
            "dataType": "json", 
        }

    def get_basic_observation_data(self, obsr_div: str, obsr_div_cd: str, start_dt: str, end_dt: str,
                                   page_no: int = 1, num_of_rows: int = 10) -> Union[str, Dict[str, Any]]:
        """
        Fetches basic agricultural weather observation data.
        :param obsr_div: 관측구분 (ex: 'RDA_WEATHER')
        :param obsr_div_cd: 관측구분코드 (ex: '01' for '기본')
        :param start_dt: 시작일 (YYYYMMDD)
        :param end_dt: 종료일 (YYYYMMDD)
        :param page_no: 페이지 번호
        :param num_of_rows: 한 페이지 결과 수
        :return: API response (JSON or XML string)
        """
        endpoint = "AgriWeatherObsrv/getAgriWeatherObsrv" # Confirmed from data.go.kr documentation
        
        params = {
            "obsrDiv": obsr_div,
            "obsrDivCd": obsr_div_cd,
            "startDt": start_dt,
            "endDt": end_dt,
            "pageNo": str(page_no),
            "numOfRows": str(num_of_rows),
            "dataType": "json" 
        }
        
        return self.get_data(endpoint=endpoint, api_name=self.api_name_basic, 
                             extra_params=params, is_json_response=True)

    def get_detailed_observation_data(self, obsr_div: str, obsr_div_cd: str, start_dt: str, end_dt: str,
                                      page_no: int = 1, num_of_rows: int = 10) -> Union[str, Dict[str, Any]]:
        """
        Fetches detailed agricultural weather observation data.
        :param obsr_div: 관측구분 (ex: 'RDA_WEATHER')
        :param obsr_div_cd: 관측구분코드 (ex: '01' for '기본')
        :param start_dt: 시작일 (YYYYMMDD)
        :param end_dt: 종료일 (YYYYMMDD)
        :param page_no: 페이지 번호
        :param num_of_rows: 한 페이지 결과 수
        :return: API response (JSON or XML string)
        """
        endpoint = "AgriWeatherDetailObsrv/getAgriWeatherDetailObsrv" # Confirmed from data.go.kr documentation
        
        params = {
            "obsrDiv": obsr_div,
            "obsrDivCd": obsr_div_cd,
            "startDt": start_dt,
            "endDt": end_dt,
            "pageNo": str(page_no),
            "numOfRows": str(num_of_rows),
            "dataType": "json" 
        }
        
        return self.get_data(endpoint=endpoint, api_name=self.api_name_detail, 
                             extra_params=params, is_json_response=True)

    # TODO: Add methods for other specific weather data endpoints if needed
