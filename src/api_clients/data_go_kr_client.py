import requests
import json
import xml.etree.ElementTree as ET
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Union
from config.settings import REQUEST_TIMEOUT, RAW_DATA_DIR

def mask_service_key(text: str) -> str:
    if not text:
        return text
    # 1. Query parameter masking (e.g. serviceKey=..., apiKey=...)
    pattern_query = r"([sS]erviceKey|[aA]piKey)=[^&'\"\s\)]+"
    text = re.sub(pattern_query, r"\1=***", text)
    
    # 2. REST Path parameter masking (e.g. getEnvInfoDataList/service_key/...)
    pattern_path = r"(getEnvInfoDataList)/[^/]+"
    text = re.sub(pattern_path, r"\1/***", text)
    return text

class BaseAPIClient:
    """
    Base class for public data API clients.
    Handles common logic like request execution, status checking, and raw data saving.
    """
    def __init__(self, base_url: str, service_key: str = None, timeout: int = REQUEST_TIMEOUT):
        self.base_url = base_url
        self.service_key = service_key
        self.timeout = timeout

    def _save_raw_response(self, api_name: str, response_content: str, is_json: bool = True):
        """Saves the raw API response to the data/raw directory."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        extension = "json" if is_json else "xml"
        file_path = RAW_DATA_DIR / f"{api_name}_{timestamp}.{extension}"
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(response_content)
            print(f"Raw response saved to {file_path}")
        except IOError as e:
            print(f"Error saving raw response to {file_path}: {e}")

    def _make_request(self, endpoint: str, params: Dict[str, Any], api_name: str, 
                      method: str = "GET", headers: Dict[str, str] = None, is_json_response: bool = True) -> Union[str, Dict[str, Any]]:
        """
        Makes an HTTP request to the API endpoint.
        Automatically handles service key injection and raw response saving.
        """
        if endpoint:
            url = f"{self.base_url.rstrip('/')}/{endpoint}"
        else:
            url = self.base_url
        
        # Add service key if provided for the client and not already specified under other names
        params_with_key = params.copy()
        if self.service_key:
            if not any(k in params_with_key for k in ["serviceKey", "ServiceKey", "apiKey"]):
                params_with_key["serviceKey"] = self.service_key
        else:
            pass

        try:
            if method.upper() == "GET":
                response = requests.get(url, params=params_with_key, timeout=self.timeout, headers=headers)
            elif method.upper() == "POST":
                response = requests.post(url, json=params_with_key, timeout=self.timeout, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

            response_content = response.text
            self._save_raw_response(api_name, response_content, is_json=is_json_response)
            
            if is_json_response:
                return response.json()
            else:
                return response_content # Return raw text for XML parsing in specific client

        except requests.exceptions.Timeout as e:
            masked_url = mask_service_key(url)
            print(f"API Request to {masked_url} timed out after {self.timeout} seconds.")
            raise RuntimeError(f"API Request timed out: {mask_service_key(str(e))}") from None
        except requests.exceptions.HTTPError as e:
            masked_url = mask_service_key(url)
            masked_err_msg = mask_service_key(str(e))
            masked_response_text = mask_service_key(e.response.text) if e.response is not None else ""
            print(f"HTTP Error for {masked_url}: {e.response.status_code if e.response is not None else 'Unknown'} - {masked_response_text}")
            raise RuntimeError(f"HTTP Error: {masked_err_msg}") from None
        except requests.exceptions.RequestException as e:
            masked_url = mask_service_key(url)
            masked_err_msg = mask_service_key(str(e))
            print(f"An error occurred during the request to {masked_url}: {masked_err_msg}")
            raise RuntimeError(f"Request Exception: {masked_err_msg}") from None
        except json.JSONDecodeError as e:
            masked_url = mask_service_key(url)
            print(f"Failed to decode JSON from response for {masked_url}. Raw content: {mask_service_key(response_content[:500])}...")
            raise RuntimeError(f"JSON Decode Error for {masked_url}: {str(e)}") from None
        
class DataGoKrClient(BaseAPIClient):
    """
    Client for data.go.kr APIs, handling common parameter adjustments.
    """
    def __init__(self, base_url: str, service_key: str, timeout: int = REQUEST_TIMEOUT):
        super().__init__(base_url, service_key, timeout)
        # Specific parameters that might differ for data.go.kr APIs
        # These will be set by individual API clients inheriting from DataGoKrClient
        self.default_params = {
            "pageNo": "1",
            "numOfRows": "100",
            "dataType": "json", # Default to JSON, can be overridden
        }

    def get_data(self, endpoint: str, api_name: str, extra_params: Dict[str, Any] = None, is_json_response: bool = True) -> Union[str, Dict[str, Any]]:
        """
        Generic method to fetch data from data.go.kr APIs.
        Handles merging default parameters with specific ones, and setting the service key param name.
        """
        params = self.default_params.copy()
        if extra_params:
            params.update(extra_params)
        
        # Override serviceKey parameter name if specified in extra_params
        # Public Data APIs often use 'serviceKey' but sometimes 'ServiceKey' (capital S)
        # This will be handled explicitly by the child clients, e.g., smartfarm_client
        # Ensure the service key from settings is used if not explicitly provided in params
        if not any(k in params for k in ["serviceKey", "ServiceKey", "apiKey"]):
            params["serviceKey"] = self.service_key 

        return self._make_request(endpoint, params, api_name, is_json_response=is_json_response)