import os
import sys
import xml.etree.ElementTree as ET
import requests
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

load_dotenv()
api_key = os.getenv("PEST_API_SERVICE_KEY") or os.getenv("DATA_GO_KR_SERVICE_KEY")
print(f"API Key found: {bool(api_key)}")

def get_detail(service_code, key_name, key_value):
    url = "http://ncpms.rda.go.kr/npmsAPI/service"
    params = {
        "apiKey": api_key,
        "serviceCode": service_code,
        "serviceType": "AA001",
        key_name: key_value
    }
    response = requests.get(url, params=params)
    print(f"\n=== {service_code} ({key_value}) ===")
    if response.status_code == 200:
        try:
            root = ET.fromstring(response.text.encode('utf-8'))
            print("Root Tag:", root.tag)
            
            # Print elements recursively
            def print_tree(node, depth=0):
                indent = "  " * depth
                children = list(node)
                if len(children) == 0:
                    text_preview = (node.text[:80] + "...") if node.text and len(node.text) > 80 else node.text
                    print(f"{indent}<{node.tag}>: {text_preview}")
                else:
                    print(f"{indent}<{node.tag}>")
                    for child in children:
                        print_tree(child, depth + 1)
            
            print_tree(root)
        except Exception as e:
            print("Error parsing XML:", e)
            print("Response preview:", response.text[:1000])
    else:
        print("Failed with status:", response.status_code)

if __name__ == "__main__":
    # Test Gray Mold (sickKey=D00001545)
    get_detail("SVC05", "sickKey", "D00001545")
    # Test Whitefly (insectKey=H00000304)
    get_detail("SVC07", "insectKey", "H00000304")
