import requests
import json
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Union
from config.settings import REQUEST_TIMEOUT, RAW_DATA_DIR

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
        url = f"{self.base_url}/{endpoint}"
        
        # Add service key if provided for the client
        if self.service_key:
            params_with_key = params.copy()
            # Note: Public Data APIs can have varying service key parameter names (serviceKey, ServiceKey, etc.)
            # This needs to be handled in the inheriting client classes or specified by the API itself.
            # For data.go.kr, 'serviceKey' is common, but will be overridden if a specific client sets it.
            params_with_key.setdefault("serviceKey", self.service_key) 
        else:
            params_with_key = params

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

        except requests.exceptions.Timeout:
            print(f"API Request to {url} timed out after {self.timeout} seconds.")
            raise
        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error for {url}: {e.response.status_code} - {e.response.text}")
            raise
        except requests.exceptions.RequestException as e:
            print(f"An error occurred during the request to {url}: {e}")
            raise
        except json.JSONDecodeError:
            print(f"Failed to decode JSON from response for {url}. Raw content: {response_content[:500]}...")
            raise
        
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
        if "serviceKey" in params and params["serviceKey"] != self.service_key:
            # If a custom serviceKey is passed, use it, otherwise use the default client one
            pass 
        elif "ServiceKey" in params and params["ServiceKey"] != self.service_key:
             # Handle cases where ServiceKey (capital S) is used
            pass
        else:
            # Ensure the service key from settings is used if not explicitly provided in params
            params["serviceKey"] = self.service_key 

        return self._make_request(endpoint, params, api_name, is_json_response=is_json_response)