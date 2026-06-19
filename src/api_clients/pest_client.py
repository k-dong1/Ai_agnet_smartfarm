from typing import Dict, Any, Union
from src.api_clients.data_go_kr_client import BaseAPIClient
from config.settings import PEST_API_SERVICE_KEY

class PestClient(BaseAPIClient):
    """
    Client for '농촌진흥청 국가농작물병해충관리시스템 (NCPMS) Open API'.
    URL: http://ncpms.rda.go.kr/npmsAPI/service
    """
    def __init__(self, service_key: str = PEST_API_SERVICE_KEY):
        # NCPMS API does not use endpoints in the URL. It always requests the base URL directly.
        super().__init__(base_url="http://ncpms.rda.go.kr/npmsAPI/service", service_key=service_key)
        self.api_name = "pest_ncpms"

    def search_pest(self, crop_name: str = None, sick_name_kor: str = None, 
                    display_count: int = 10, start_point: int = 1) -> str:
        """
        SVC01: 병 검색 API
        crop_name or sick_name_kor must be provided.
        """
        if not crop_name and not sick_name_kor:
            raise ValueError("Either crop_name or sick_name_kor must be provided.")
        
        params = {
            "apiKey": self.service_key,
            "serviceCode": "SVC01",
            "serviceType": "AA001",  # XML
            "displayCount": str(display_count),
            "startPoint": str(start_point)
        }
        if crop_name:
            params["cropName"] = crop_name
        if sick_name_kor:
            params["sickNameKor"] = sick_name_kor

        api_suffix = f"search_pest_{crop_name or ''}_{sick_name_kor or ''}"
        return self._make_request(
            endpoint="", 
            params=params, 
            api_name=f"{self.api_name}_{api_suffix}", 
            is_json_response=False
        )

    def get_pest_detail(self, sick_key: str) -> str:
        """
        SVC05: 병 상세정보 API
        """
        if not sick_key:
            raise ValueError("sick_key is required.")
            
        params = {
            "apiKey": self.service_key,
            "serviceCode": "SVC05",
            "sickKey": str(sick_key)
        }
        
        return self._make_request(
            endpoint="",
            params=params,
            api_name=f"{self.api_name}_detail_pest_{sick_key}",
            is_json_response=False
        )

    def search_insect(self, crop_name: str = None, insect_kor_name: str = None,
                      display_count: int = 10, start_point: int = 1) -> str:
        """
        SVC03: 해충 검색 API
        crop_name or insect_kor_name must be provided.
        """
        if not crop_name and not insect_kor_name:
            raise ValueError("Either crop_name or insect_kor_name must be provided.")
            
        params = {
            "apiKey": self.service_key,
            "serviceCode": "SVC03",
            "serviceType": "AA001",  # XML
            "displayCount": str(display_count),
            "startPoint": str(start_point)
        }
        if crop_name:
            params["cropName"] = crop_name
        if insect_kor_name:
            params["insectKorName"] = insect_kor_name

        api_suffix = f"search_insect_{crop_name or ''}_{insect_kor_name or ''}"
        return self._make_request(
            endpoint="",
            params=params,
            api_name=f"{self.api_name}_{api_suffix}",
            is_json_response=False
        )

    def get_insect_detail(self, insect_key: str) -> str:
        """
        SVC07: 해충 상세정보 API
        """
        if not insect_key:
            raise ValueError("insect_key is required.")
            
        params = {
            "apiKey": self.service_key,
            "serviceCode": "SVC07",
            "insectKey": str(insect_key)
        }
        
        return self._make_request(
            endpoint="",
            params=params,
            api_name=f"{self.api_name}_detail_insect_{insect_key}",
            is_json_response=False
        )
