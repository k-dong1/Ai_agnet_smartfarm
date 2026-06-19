import json
import xml.etree.ElementTree as ET
from typing import List, Dict, Any

def parse_smartfarm_data(json_data: Any) -> List[Dict[str, Any]]:
    """
    Parses raw JSON data from the SmartFarm Korea API (DataMartItemRestService).
    Expected structure: List of dicts or dict containing 'statusCode' and a list of items.
    Since SmartFarm Korea returns a long format (each sensor reading as a separate row),
    this parser groups/pivots the data by 'measDate' and maps 'fatrCode' to wide format keys.
    """
    if not json_data:
        return []
        
    raw_items = []
    if isinstance(json_data, list):
        raw_items = json_data
    elif isinstance(json_data, dict):
        if "data" in json_data and isinstance(json_data["data"], list):
            raw_items = json_data["data"]
        else:
            status_code = json_data.get("statusCode")
            if status_code and status_code not in ["00", "NORMAL_SERVICE"]:
                status_msg = json_data.get("statusMessage", "Unknown status")
                print(f"SmartFarm Korea API returned error: {status_code} - {status_msg}")
                return []
            # Check if it contains general key-values directly
            if "measDate" in json_data:
                raw_items = [json_data]

    # Map fatrCode to standardized keys
    fatr_map = {
        "TI": "inTemp",
        "HI": "inHum",
        "CI": "inCo2",
        "CO": "inCo2",
        "LI": "inLight",
        "TE": "outTemp",
        "HE": "outHum"
    }

    # Group by measDate to pivot
    # Format of measDate is yyyy-mm-dd hh:mm:ss
    grouped: Dict[str, Dict[str, Any]] = {}
    for item in raw_items:
        meas_date = item.get("measDate")
        if not meas_date:
            continue
            
        fatr_code = item.get("fatrCode")
        sen_val_str = item.get("senVal")
        if not fatr_code or sen_val_str is None:
            continue
            
        standard_key = fatr_map.get(fatr_code)
        if not standard_key:
            continue
            
        try:
            sen_val = float(sen_val_str)
        except (ValueError, TypeError):
            sen_val = sen_val_str
            
        if meas_date not in grouped:
            grouped[meas_date] = {
                "collectDate": meas_date,
                "fcltyId": item.get("fcltyId"),
                "cropCode": item.get("itemCode")
            }
        grouped[meas_date][standard_key] = sen_val

    # Convert back to a list of dicts sorted by collectDate
    parsed_items = list(grouped.values())
    parsed_items.sort(key=lambda x: x["collectDate"])
    return parsed_items

def parse_pest_data(xml_data: str) -> List[Dict[str, Any]]:
    """
    Parses raw XML data from the NCPMS Pest API.
    Expected structure: <service><list><item>...</item></list></service>
    Uses findall(".//item") to locate all item elements flexibly.
    """
    parsed_items = []
    try:
        root = ET.fromstring(xml_data)
        
        # Check if error response
        error_code_node = root.find("errorCode")
        if error_code_node is not None:
            error_msg = root.find("errorMsg")
            msg = error_msg.text if error_msg is not None else "Unknown error"
            print(f"API returned error: {error_code_node.text} - {msg}")
            return []

        # Find all <item> elements anywhere in the tree
        item_nodes = root.findall(".//item")
        
        for item_node in item_nodes:
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

def parse_weather_data(raw_data: Any) -> List[Dict[str, Any]]:
    """
    Parses raw data from the Agricultural Weather Observation Data API.
    Can handle both JSON (dict/str) and XML (str) formats.
    """
    if not raw_data:
        return []
        
    parsed_items = []
    
    # Check if JSON dict
    if isinstance(raw_data, dict):
        try:
            items_wrapper = raw_data.get("response", {}).get("body", {}).get("items", {})
            items = items_wrapper.get("item")
            if not items:
                items = raw_data.get("items", {}).get("item")
                if not items:
                    return []
            if isinstance(items, dict):
                items = [items]
            for item in items:
                parsed_item = {}
                for key, value in item.items():
                    try:
                        parsed_item[key] = float(value)
                    except (ValueError, TypeError):
                        parsed_item[key] = value
                parsed_items.append(parsed_item)
            return parsed_items
        except Exception as e:
            print(f"Error parsing Weather JSON data: {e}")
            return []
            
    # Check if XML string
    elif isinstance(raw_data, str):
        try:
            # Handle potential encoding declarations in XML string
            xml_bytes = raw_data.encode('utf-8')
            root = ET.fromstring(xml_bytes)
            
            # Check for error
            error_code_node = root.find("errorCode")
            if error_code_node is not None:
                error_msg = root.find("errorMsg")
                msg = error_msg.text if error_msg is not None else "Unknown error"
                print(f"Weather API returned error: {error_code_node.text} - {msg}")
                return []
                
            item_nodes = root.findall(".//item")
            for item_node in item_nodes:
                parsed_item = {}
                for child in item_node:
                    try:
                        parsed_item[child.tag] = float(child.text) if child.text else None
                    except (ValueError, TypeError):
                        parsed_item[child.tag] = child.text
                parsed_items.append(parsed_item)
        except ET.ParseError as e:
            # If it's not valid XML, maybe it was a JSON string?
            try:
                import json
                json_dict = json.loads(raw_data)
                return parse_weather_data(json_dict)
            except json.JSONDecodeError:
                print(f"Error parsing Weather XML/JSON data: {e}")
                return []
        except Exception as e:
            print(f"Error processing parsed Weather XML data: {e}")
            return []
            
    return parsed_items

# TODO: Add parsers for other potential APIs (e.g., Pest Dictionary, SmartFarm Model, if their structures differ)

def parse_pest_detail(xml_data: str) -> Dict[str, Any]:
    """
    Parses detailed information for a crop disease (SVC05).
    Extracts prevention methods, symptoms, development environment, and image URLs.
    """
    result = {
        "prevent_method": "",
        "symptoms": "",
        "development_env": "",
        "images": []
    }
    if not xml_data:
        return result
    try:
        xml_bytes = xml_data.encode('utf-8')
        root = ET.fromstring(xml_bytes)
        
        prevent_node = root.find(".//preventMethod")
        if prevent_node is not None and prevent_node.text:
            result["prevent_method"] = prevent_node.text.strip()
            
        symptoms_node = root.find(".//symptoms")
        if symptoms_node is not None and symptoms_node.text:
            result["symptoms"] = symptoms_node.text.strip()
            
        env_node = root.find(".//developmentEnv")
        if env_node is not None and env_node.text:
            result["development_env"] = env_node.text.strip()
            
        # Get images from imageList/item
        image_nodes = root.findall(".//imageList/item")
        for img_node in image_nodes:
            img_url_node = img_node.find("image")
            if img_url_node is not None and img_url_node.text:
                photo_sj = img_node.find("photoSj")
                title = photo_sj.text.strip() if photo_sj is not None and photo_sj.text else "병해 사진"
                result["images"].append({
                    "url": img_url_node.text.strip(),
                    "title": title
                })
                
        # If imageList is empty, look for general image list
        if not result["images"]:
            general_img_nodes = root.findall(".//image")
            for idx, img_node in enumerate(general_img_nodes):
                if img_node.text and img_node.text.startswith("http"):
                    result["images"].append({
                        "url": img_node.text.strip(),
                        "title": f"병해 사진 {idx+1}"
                    })
    except Exception as e:
        print(f"Error parsing disease detail XML: {e}")
    return result

def parse_insect_detail(xml_data: str) -> Dict[str, Any]:
    """
    Parses detailed information for a crop insect pest (SVC07).
    Extracts prevention methods, ecology, style/morphology, and image URLs.
    """
    result = {
        "prevent_method": "",
        "ecology": "",
        "morphology": "",
        "images": []
    }
    if not xml_data:
        return result
    try:
        xml_bytes = xml_data.encode('utf-8')
        root = ET.fromstring(xml_bytes)
        
        prevent_node = root.find(".//preventMethod")
        if prevent_node is not None and prevent_node.text and prevent_node.text.strip().lower() != "none":
            result["prevent_method"] = prevent_node.text.strip()
        else:
            chem_node = root.find(".//chemicalPrvnbeMth")
            bio_node = root.find(".//biologyPrvnbeMth")
            prevent_desc = []
            if chem_node is not None and chem_node.text and chem_node.text.strip().lower() != "none":
                prevent_desc.append(f"화학적 방제: {chem_node.text.strip()}")
            if bio_node is not None and bio_node.text and bio_node.text.strip().lower() != "none":
                prevent_desc.append(f"생물적 방제: {bio_node.text.strip()}")
            if prevent_desc:
                result["prevent_method"] = "\n".join(prevent_desc)
            
        ecology_node = root.find(".//ecologyInfo")
        if ecology_node is not None and ecology_node.text:
            result["ecology"] = ecology_node.text.strip()
            
        morph_node = root.find(".//stleInfo")
        if morph_node is not None and morph_node.text:
            result["morphology"] = morph_node.text.strip()
            
        # Get images from imageList/item
        image_nodes = root.findall(".//imageList/item")
        for img_node in image_nodes:
            img_url_node = img_node.find("image")
            if img_url_node is not None and img_url_node.text:
                photo_sj = img_node.find("photoSj")
                title = photo_sj.text.strip() if photo_sj is not None and photo_sj.text else "해충 사진"
                result["images"].append({
                    "url": img_url_node.text.strip(),
                    "title": title
                })
                
        # If imageList is empty, look for general image list
        if not result["images"]:
            general_img_nodes = root.findall(".//image")
            for idx, img_node in enumerate(general_img_nodes):
                if img_node.text and img_node.text.startswith("http"):
                    result["images"].append({
                        "url": img_node.text.strip(),
                        "title": f"해충 사진 {idx+1}"
                    })
    except Exception as e:
        print(f"Error parsing insect detail XML: {e}")
    return result