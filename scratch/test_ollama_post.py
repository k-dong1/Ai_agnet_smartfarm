import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

url = "http://localhost:11434/api/generate"
payload = {
    "model": "qwen2.5:3b",
    "prompt": "안녕? 반가워. 짧게 한 문장으로 답해줘.",
    "stream": False
}

print(f"Sending POST to: {url}")
print(f"Payload: {json.dumps(payload, ensure_ascii=False)}")

try:
    response = requests.post(url, json=payload, timeout=20)
    print(f"Status Code: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    print(f"Response Text: {response.text}")
except Exception as e:
    print(f"Exception occurred: {e}")
