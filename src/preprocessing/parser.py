import json
import xml.etree.ElementTree as ET
from typing import List, Dict, Any

def parse_smartfarm_data(json_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Parses raw JSON data from the SmartFarm Data Mart API.
    Expected structure: { "response": { "body": { "items": { "item": [...] } } } }
    """
    parsed_items = []
    try:
        items_wrapper = json_data.get("response", {}).get("body", {}).get("items", {})
        
        # 'item' can be a list if multiple items, or a dict if single item
        items = items_wrapper.get("item")
        if not items:
            return []

        if isinstance(items, dict):
            items = [items] # Wrap single item dict in a list

        for item in items:
            parsed_item = {}
            for key, value in item.items():
                # Attempt to convert numeric strings to float, otherwise keep as string
                try:
                    parsed_item[key] = float(value)
                except (ValueError, TypeError):
                    parsed_item[key] = value
            parsed_items.append(parsed_item)
            
    except Exception as e:
        print(f"Error parsing SmartFarm data: {e}")
        # Depending on requirements, could raise, log, or return partial data
        return []
    
    return parsed_items

def parse_pest_data(xml_data: str) -> List[Dict[str, Any]]:
    """
    Parses raw XML data from the Pest Search API.
    Expected structure: <response><body><items><item>...</item></items></body></response>
    """
    parsed_items = []
    try:
        root = ET.fromstring(xml_data)
        
        # Namespace handling for XML is crucial if present. 
        # For simplicity, assuming no namespace or using local-name() if necessary.
        # Example XPath might vary based on actual XML structure.
        
        items_node = root.find(".//items") # Find <items> anywhere in the tree
        if items_node is None:
            return []

        for item_node in items_node.findall(".//item"):
            parsed_item = {}
            for child in item_node:
                parsed_item[child.tag] = child.text
            parsed_items.append(parsed_item)

    except ET.ParseError as e:
        print(f"Error parsing Pest XML data: {e}")
        return []
    except Exception as e:
        print(f"Error processing parsed Pest XML data: {e}")
        return []

    return parsed_items

def parse_weather_data(json_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Parses raw JSON data from the Agricultural Weather Observation Data API.
    Expected structure: { "response": { "body": { "items": { "item": [...] } } } }
    Similar to SmartFarm data parsing.
    """
    parsed_items = []
    try:
        items_wrapper = json_data.get("response", {}).get("body", {}).get("items", {})
        items = items_wrapper.get("item")
        if not items:
            return []

        if isinstance(items, dict):
            items = [items] # Wrap single item dict in a list

        for item in items:
            parsed_item = {}
            for key, value in item.items():
                try:
                    parsed_item[key] = float(value)
                except (ValueError, TypeError):
                    parsed_item[key] = value
            parsed_items.append(parsed_item)
            
    except Exception as e:
        print(f"Error parsing Weather data: {e}")
        return []
    
    return parsed_items

# TODO: Add parsers for other potential APIs (e.g., Pest Dictionary, SmartFarm Model, if their structures differ)