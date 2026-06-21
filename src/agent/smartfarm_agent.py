from datetime import datetime
from src.ml.predict import predict_risk
from src.agent.risk_analyzer import analyze_risk_reasons
from src.agent.action_recommender import recommend_actions
from src.llm.ollama_client import OllamaClient
from config.settings import OLLAMA_BASE_URL, OLLAMA_MODEL

class SmartFarmAgent:
    def __init__(self, ollama_client: OllamaClient = None):
        self.logs = []
        if ollama_client is None:
            self.ollama_client = OllamaClient(base_url=OLLAMA_BASE_URL, model=OLLAMA_MODEL)
        else:
            self.ollama_client = ollama_client

    def log(self, message: str):
        timestamp = datetime.now().strftime("[%H:%M:%S]")
        self.logs.append(f"{timestamp} {message}")
        print(f"[SmartFarmAgent] {message}")

    def run_agent_analysis(self, sensor_data: dict) -> dict:
        """
        Executes the full agent diagnostics pipeline.
        
        Args:
            sensor_data: Dict with keys: ['temperature', 'humidity', 'light', 'co2', 'humidity_duration', 'temp_change', 'humidity_change']
            
        Returns:
            dict: The output result structure containing agent decisions, probabilities, logs, and LLM text.
        """
        self.logs = []
        self.log("[STEP 1] 최신 환경 센서 데이터를 수령하여 검사를 시작합니다.")
        self.log(f"수령 센서값: {sensor_data}")

        # 1. MLP Predict
        self.log("[STEP 2] MLP 분류 모델을 활용하여 위험 예측을 가동합니다.")
        try:
            pred_label, probabilities, local_attribution = predict_risk(sensor_data)
            risk_levels = ["정상", "주의", "경고", "심각"]
            risk_level = risk_levels[pred_label]
            self.log(f"MLP 모델 예측 완료 -> 위험 등급: {risk_level} (라벨: {pred_label})")
        except Exception as e:
            self.log(f"WARNING: MLP 모델 예측 실패 ({e}). 규칙 기반 임계치 기준으로 폴백 작동합니다.")
            # Simple rule fallback if model fails (e.g. not trained yet)
            from src.preprocessing.labeling import make_risk_label
            import pandas as pd
            pred_label = make_risk_label(pd.Series(sensor_data))
            risk_levels = ["정상", "주의", "경고", "심각"]
            risk_level = risk_levels[pred_label]
            probabilities = {lvl: (1.0 if lvl == risk_level else 0.0) for lvl in risk_levels}
            local_attribution = {
                'temperature': 14.28, 'humidity': 14.28, 'light': 14.28, 'co2': 14.28, 
                'humidity_duration': 14.28, 'temp_change': 14.28, 'humidity_change': 14.28
            }

        # 2. Risk Reason Analysis
        self.log("[STEP 3] 규칙 분석기를 활용하여 세부 위험 요인 및 원인을 식별합니다.")
        reasons = analyze_risk_reasons(sensor_data)
        for r in reasons:
            self.log(f"원인 감지: {r}")

        # 3. Action Recommendation
        self.log("[STEP 4] 원인 및 위험 등급에 대응하는 관리자 조치 사항을 수립합니다.")
        actions = recommend_actions(pred_label, reasons)
        for a in actions:
            self.log(f"행동 추천: {a}")

        # 4. Local LLM Summary Generation
        self.log("[STEP 5] Ollama 로컬 LLM을 통한 자연어 요약본 생성을 시도합니다.")
        try:
            llm_summary = self.ollama_client.generate_summary(
                sensor_data=sensor_data,
                risk_level=risk_level,
                reasons=reasons,
                actions=actions
            )
            self.log("로컬 LLM 요약본 작성 성공.")
        except Exception as e:
            self.log(f"WARNING: 로컬 LLM 연동 실패 또는 제한시간 만료 ({e}). 로컬 폴백 메시지로 대체합니다.")
            llm_summary = "로컬 LLM 설명 생성에는 실패했지만, MLP Agent 분석 결과는 정상 생성되었습니다."

        self.log("[STEP 6] 분석 프로세스가 완수되었습니다.")
        
        result = {
            "sensor_data": sensor_data,
            "risk_level": risk_level,
            "risk_label": pred_label,
            "risk_probability": probabilities,
            "local_attribution": local_attribution,
            "reasons": reasons,
            "actions": actions,
            "llm_summary": llm_summary,
            "logs": self.logs
        }
        
        return result
