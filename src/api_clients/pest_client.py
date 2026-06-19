from typing import Dict, Any, Union 
from src.api_clients.data_go_kr_client import DataGoKrClient
from config.settings import PEST_API_SERVICE_KEY

class PestClient(DataGoKrClient):
    """
    Client for '농촌진흥청_작물 병해충 검색 서비스'.
    URL: https://www.data.go.kr/data/15058504/openapi.do
    Base URL: http://openapi.rda.go.kr/openapi/service/pest/getInsectList
    """
    def __init__(self, service_key: str = PEST_API_SERVICE_KEY):
        super().__init__(base_url="http://openapi.rda.go.kr/openapi/service/pest", service_key=service_key)
        self.api_name = "pest_search"
        # Override default_params for this XML-based API
        self.default_params = {
            "pageNo": "1",
            "numOfRows": "10",
            "_type": "xml", # This API returns XML by default, specify XML
        }

    def search_pest(self, pest_name: str = None, crop_name: str = None, 
                    page_no: int = 1, num_of_rows: int = 10) -> str:
        """
        Searches for crop pests.
        Can search by pest name or crop name.
        :param pest_name: 병해충 이름 (e.g., '잿빛곰팡이병')
        :param crop_name: 작물 이름 (e.g., '토마토')
        :param page_no: 페이지 번호
        :param num_of_rows: 한 페이지 결과 수
        :return: API response (XML string)
        """
        endpoint = "getPestDiseaseList" # Confirmed from data.go.kr documentation

        params = {
            "pageNo": str(page_no),
            "numOfRows": str(num_of_rows),
            "_type": "xml" # Explicitly request XML
        }
        
        if pest_name:
            params["diseaseNm"] = pest_name # Parameter for disease name
        if crop_name:
            params["cropName"] = crop_name # Parameter for crop name

        # Note: The serviceKey parameter name for this API is 'serviceKey' (lowercase k)
        # The base class DataGoKrClient will add it correctly if not present.

        return self.get_data(endpoint=endpoint, api_name=f"{self.api_name}_{pest_name or crop_name}", extra_params=params, is_json_response=False) # Expect XML response

    # TODO: Add methods for other specific Pest Search endpoints if needed
