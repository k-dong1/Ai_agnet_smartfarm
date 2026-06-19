from typing import Dict, Any, Union
from src.api_clients.data_go_kr_client import DataGoKrClient
from config.settings import SMARTFARM_API_SERVICE_KEY, SMARTFARM_API_URL

class SmartFarmClient(DataGoKrClient):
    """
    Client for '농림축산식품부_스마트팜 데이터 마트 품목별 데이터셋 제공 서비스'.
    URL: https://www.data.go.kr/data/15121325/openapi.do
    """
    def __init__(self, service_key: str = SMARTFARM_API_SERVICE_KEY):
        # The base_url for this specific service is identified as http://apis.data.go.kr/1543036/smartfarmDatamart
        # SMARTFARM_API_URL in settings might be more general, so using the specific one here.
        super().__init__(base_url="http://apis.data.go.kr/1543036/smartfarmDatamart", service_key=service_key)
        self.api_name = "smartfarm_datamart"

    def get_crop_data(self, farm_id: str, crop_code: str, start_date: str, end_date: str,
                      page_no: int = 1, num_of_rows: int = 100) -> Union[str, Dict[str, Any]]:
        """
        Fetches crop data from the SmartFarm Data Mart.
        :param farm_id: 농장 ID
        :param crop_code: 작물 코드 (e.g., '114' for Tomato)
        :param start_date: 시작일 (YYYYMMDD)
        :param end_date: 종료일 (YYYYMMDD)
        :param page_no: 페이지 번호
        :param num_of_rows: 한 페이지 결과 수
        :return: API response (JSON or XML string)
        """
        endpoint = "getDataItem" # Confirmed from data.go.kr documentation
        
        params = {
            "farmId": farm_id,
            "cropCode": crop_code,
            "sdate": start_date,
            "edate": end_date,
            "pageNo": str(page_no),
            "numOfRows": str(num_of_rows),
            "dataType": "json" # Request JSON response
        }
        
        # Override serviceKey parameter name if needed for this specific API, otherwise base handles it
        # Based on data.go.kr, 'serviceKey' (lowercase k) is correct for this API
        
        return self.get_data(endpoint=endpoint, api_name=f"{self.api_name}_{farm_id}_{crop_code}", 
                             extra_params=params, is_json_response=True)

    # TODO: Add methods for other specific SmartFarm Data Mart endpoints if needed