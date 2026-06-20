from typing import Dict, Any, Union
from src.api_clients.data_go_kr_client import BaseAPIClient
from config.settings import SMARTFARM_API_SERVICE_KEY

class SmartFarmClient(BaseAPIClient):
    """
    Client for '스마트팜코리아 (smartfarmkorea.net) 품목별 데이터셋 제공 서비스 API'.
    URL: http://www.smartfarmkorea.net/Agree_WS/webservices/DataMartItemRestService/
    """
    def __init__(self, service_key: str = SMARTFARM_API_SERVICE_KEY):
        # SmartFarm Korea uses path parameters instead of query strings.
        super().__init__(base_url="http://www.smartfarmkorea.net/Agree_WS/webservices/DataMartItemRestService", service_key=service_key)
        self.api_name = "smartfarm_korea"

    def get_crop_data(self, farm_id: str, crop_code: str, start_date: str, end_date: str,
                       crpsn_sn: str = "1", num_of_rows: int = 50) -> Union[str, Dict[str, Any]]:
        """
        Fetches crop environmental data from Smart Farm Korea Data Mart.
        Uses path parameters: .../getEnvInfoDataList/{serviceKey}/{fcltyId}/{crpsnSn}/{itemCode}/{fixPlntngDe}/{crpsnEndDe}
        
        :param farm_id: 농가 ID (fcltyId)
        :param crop_code: 작물 코드 (itemCode, '080300' for Tomato. If '114' is passed, it is mapped to '080300')
        :param start_date: 시작일 YYYYMMDD (fixPlntngDe)
        :param end_date: 종료일 YYYYMMDD (crpsnEndDe)
        :param crpsn_sn: 작기 일련번호 (crpsnSn)
        :param num_of_rows: (Not used in path param, kept for signature compatibility)
        :return: API response (JSON or str)
        """
        # Map crop_code
        if crop_code == "114":
            item_code = "080300"
        else:
            item_code = crop_code

        # Smart Farm Korea REST path: getEnvInfoDataList/{serviceKey}/{fcltyId}/{crpsnSn}/{itemCode}/{fixPlntngDe}/{crpsnEndDe}
        endpoint = f"getEnvInfoDataList/{self.service_key}/{farm_id}/{crpsn_sn}/{item_code}/{start_date}/{end_date}"

        # Make the request without query params since we pass parameters in path
        return self._make_request(
            endpoint=endpoint,
            params={},
            api_name=f"{self.api_name}_{farm_id}_{item_code}",
            is_json_response=True # Assume JSON response
        )