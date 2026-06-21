import requests
import json

class OllamaClient:
    def __init__(self, base_url: str, model: str, timeout: int = 90):
        """
        Queries the local Ollama LLM to generate a user-friendly summary of the agent diagnostics.
        """
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    def generate_summary(self, sensor_data: dict, risk_level: str, reasons: list, actions: list) -> str:
        """
        Queries the local Ollama LLM to generate a user-friendly summary of the agent diagnostics.
        """
        # Format arrays to clean string representations
        reasons_text = "\n".join([f"- {r}" for r in reasons])
        actions_text = "\n".join([f"- {a}" for a in actions])
        
        prompt = f"""
        너는 스마트팜 AI Agent 결과를 설명하는 보조 LLM이다.
        위험도 판단을 새로 하지 말고, 아래 결과를 사용자가 이해하기 쉽게 요약하라.

        센서 데이터: {sensor_data}
        MLP 예측 위험도: {risk_level}
        Agent 분석 원인:
        {reasons_text}
        Agent 추천 행동:
        {actions_text}

        조건:
        - 한국어로 작성
        - 5문장 이내
        - 과장 금지
        - 의료/농약 전문 진단처럼 단정하지 말 것
        - 농장 관리자가 바로 이해할 수 있게 작성
        """

        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        
        # Requests POST to Ollama API
        response = requests.post(url, json=payload, timeout=self.timeout)
        response.raise_for_status()
        
        result_json = response.json()
        return result_json.get("response", "").strip()
