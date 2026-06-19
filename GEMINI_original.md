# GEMINI.md

## 0. 이 문서의 목적

이 문서는 Gemini CLI가 VSCode 프로젝트 루트에서 읽고, **토마토 스마트팜 병충해 위험도 판단 AI Agent**를 구현하기 위한 작업 지시서다.

이 프로젝트는 수업 과제용 프로토타입이며, 핵심은 UI가 아니라 **Python 기반 AI Agent**다.
UI는 Agent가 처리한 결과와 로그를 확인하는 정적 HTML 리포트 정도로 구현한다.

---

## 1. 프로젝트 요약

### 프로젝트명

**Tomato SmartFarm Pest Risk AI Agent**

### 도메인

농업 / 스마트팜 / 제조형 농업 데이터 분석

### 대상 작물

토마토

### 대상 병충해

1. 잿빛곰팡이병
2. 담배가루이

### 최종 목표

공공데이터 API에서 가져온 스마트팜 환경 데이터와 병해충 기준 정보를 기반으로, MLP 모델이 현재 환경의 병충해 위험도를 분류하고, AI Agent가 원인 분석과 대응 행동을 제안한다.

```text
공공데이터 API
→ 원본 응답 저장
→ 파싱/전처리
→ MLP 입력 feature 생성
→ 라벨 생성
→ MLP 학습/예측
→ Agent 원인 분석
→ 대응 행동 추천
→ Ollama 로컬 LLM 설명문 생성
→ HTML 리포트 생성
```

---

## 2. 절대 지켜야 할 핵심 제약사항

### 2.1 더미데이터 금지

다음은 금지한다.

```text
랜덤 더미데이터 생성 금지
가짜 센서 데이터 생성 금지
API 실패 시 임의 데이터로 대체 금지
임의 CSV를 만들어 실제 데이터처럼 사용 금지
```

반드시 공공데이터 API 또는 공공데이터 파일에서 얻은 실제 데이터를 사용한다.

단, 위험도 라벨은 공공데이터에 없을 수 있으므로, 실제 공공데이터 환경값에 대해 규칙 기반으로 생성할 수 있다.
이때 라벨링 규칙은 코드와 README에 명확히 설명해야 한다.

### 2.2 서비스키 보안

공공데이터 서비스키는 코드에 직접 작성하지 않는다.

허용 방식:

```text
.env 파일
환경변수
config.local.json, 단 .gitignore 처리 필수
```

필수 환경변수 예시:

```text
DATA_GO_KR_SERVICE_KEY=공공데이터포털_인증키
OLLAMA_MODEL=qwen2.5:3b
OLLAMA_BASE_URL=http://localhost:11434
```

`.env`는 Git에 올리지 않는다.
`.env.example`만 제공한다.

### 2.3 웹 프레임워크 금지 또는 최소화

이 프로젝트에서는 Flask, FastAPI, Streamlit을 기본적으로 사용하지 않는다.

이유:

```text
과제 핵심은 AI Agent 구현이다.
UI는 가산점 또는 결과 확인용이다.
웹 서버 실행 오류를 줄이기 위해 정적 HTML 리포트로 구현한다.
```

출력 방식:

```text
python main.py
→ output/report.html 생성
→ 브라우저에서 output/report.html 확인
```

### 2.4 로컬 LLM 역할 제한

Ollama 로컬 LLM은 위험도를 직접 판단하지 않는다.

로컬 LLM 역할:

```text
MLP 예측 결과와 Agent 분석 결과를 자연어 설명문으로 바꾸는 보조 역할
```

핵심 판단은 반드시 다음이 담당한다.

```text
MLP 모델 + Agent 규칙 기반 원인 분석 로직
```

### 2.5 실행 가능성 우선

복잡한 기능보다 다음을 우선한다.

```text
공공데이터 API 호출 성공
원본 응답 저장
파싱 성공
MLP 학습/예측 성공
Agent 분석 결과 출력
HTML 리포트 생성 성공
```

---

## 3. 사용할 공공데이터

### 필수 데이터 1: 스마트팜 환경/생육 데이터

**농림축산식품부_스마트팜 데이터 마트 품목별 데이터셋 제공 서비스**

- URL: https://www.data.go.kr/data/15121325/openapi.do
- 역할: MLP 입력 데이터의 핵심 원천
- 기대 필드:
  - 온도
  - 습도
  - CO2
  - 광량/일사량
  - 작기 정보
  - 생육 정보
  - 제어 정보

이 데이터에서 숫자형 환경값을 추출하여 MLP 입력 feature를 만든다.

### 필수 데이터 2: 병해충 기준 정보

**농촌진흥청_작물 병해충 검색 서비스**

- URL: https://www.data.go.kr/data/15058504/openapi.do
- 역할: 잿빛곰팡이병/담배가루이 위험 조건과 대응 행동 근거
- 검색 대상:
  - 토마토
  - 잿빛곰팡이병
  - 담배가루이

### 보조 데이터 1: 병해충도감정보

**농촌진흥청_국가농작물병해충도감정보**

- URL: https://www.data.go.kr/data/15002034/openapi.do
- 역할: 병해충 설명, 발생 환경, 방제 방법 보완

### 보조 데이터 2: 스마트팜 생산성 향상 모델

**농촌진흥청_스마트팜 생산성 향상 모델 오픈 API 조회 서비스**

- URL: https://www.data.go.kr/data/15125691/openapi.do
- 역할: 토마토 생육 적정 조건 또는 기준값 참고

### 보조 데이터 3: 농업기상 관측 데이터

**농촌진흥청 국립농업과학원_농업기상 기본 관측데이터 조회**

- URL: https://www.data.go.kr/data/15078057/openapi.do
- 역할: 외부 기상 보조 정보

**농촌진흥청 국립농업과학원_농업기상 상세 관측데이터 조회**

- URL: https://www.data.go.kr/data/15078194/openapi.do
- 역할: 시간 단위 기상 보조 정보

---

## 4. 구현 기술 스택

### 필수

```text
Python 3.10 이상
PyTorch
pandas
numpy
scikit-learn
requests
python-dotenv
jinja2
```

### 선택

```text
matplotlib
ollama Python SDK 또는 requests 기반 Ollama REST API 호출
```

### requirements.txt 예시

```text
torch
pandas
numpy
scikit-learn
requests
python-dotenv
jinja2
matplotlib
```

Ollama는 Python 패키지가 아니라 별도 프로그램으로 설치되어 있어야 한다.
Ollama 호출은 `requests`로 구현해도 충분하다.

---

## 5. 권장 폴더 구조

다음 구조로 프로젝트를 생성한다.

```text
smartfarm_ai_agent/
├─ GEMINI.md
├─ README.md
├─ requirements.txt
├─ .env.example
├─ .gitignore
├─ main.py
├─ config/
│  ├─ settings.py
│  └─ thresholds.py
├─ data/
│  ├─ raw/
│  │  └─ .gitkeep
│  ├─ processed/
│  │  └─ .gitkeep
│  └─ cache/
│     └─ .gitkeep
├─ src/
│  ├─ __init__.py
│  ├─ api_clients/
│  │  ├─ __init__.py
│  │  ├─ data_go_kr_client.py
│  │  ├─ smartfarm_client.py
│  │  ├─ pest_client.py
│  │  └─ weather_client.py
│  ├─ preprocessing/
│  │  ├─ __init__.py
│  │  ├─ parser.py
│  │  ├─ feature_engineering.py
│  │  └─ labeling.py
│  ├─ ml/
│  │  ├─ __init__.py
│  │  ├─ model.py
│  │  ├─ train.py
│  │  ├─ predict.py
│  │  └─ dataset.py
│  ├─ agent/
│  │  ├─ __init__.py
│  │  ├─ smartfarm_agent.py
│  │  ├─ action_recommender.py
│  │  └─ risk_analyzer.py
│  ├─ llm/
│  │  ├─ __init__.py
│  │  └─ ollama_client.py
│  └─ report/
│     ├─ __init__.py
│     ├─ report_generator.py
│     └─ templates/
│        └─ report_template.html
├─ output/
│  ├─ .gitkeep
│  └─ report.html
└─ models/
   └─ .gitkeep
```

---

## 6. 단계별 구현 지시

### 6.1 1단계: 환경변수와 설정

구현 파일:

```text
.env.example
config/settings.py
config/thresholds.py
```

`.env.example` 예시:

```text
DATA_GO_KR_SERVICE_KEY=YOUR_SERVICE_KEY_HERE
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:3b
REQUEST_TIMEOUT=20
```

`settings.py` 요구사항:

- `.env`를 읽는다.
- 서비스키가 없으면 명확한 오류 메시지를 출력한다.
- API URL과 파일 저장 경로를 상수로 관리한다.

`thresholds.py` 요구사항:

- 위험도 라벨링 임계값을 한 곳에서 관리한다.
- 코드 내부에 마법 숫자를 흩뿌리지 않는다.

예시:

```python
HUMIDITY_CAUTION = 80.0
HUMIDITY_WARNING = 85.0
HUMIDITY_SEVERE = 90.0
LOW_TEMP_THRESHOLD = 20.0
HUMIDITY_CHANGE_THRESHOLD = 10.0
TEMP_CHANGE_THRESHOLD = 5.0
```

---

### 6.2 2단계: 공공데이터 API Client

구현 파일:

```text
src/api_clients/data_go_kr_client.py
src/api_clients/smartfarm_client.py
src/api_clients/pest_client.py
src/api_clients/weather_client.py
```

공통 요구사항:

- `requests.get()` 사용
- `timeout` 설정 필수
- 응답 status code 검사
- JSON/XML 응답 모두 대비
- 원본 응답을 `data/raw/`에 저장
- 실패 시 랜덤 데이터 생성 금지
- 실패 시 오류 메시지를 명확히 출력

공통 client 예시 구조:

```python
class DataGoKrClient:
    def __init__(self, service_key: str, timeout: int = 20):
        self.service_key = service_key
        self.timeout = timeout

    def get(self, url: str, params: dict) -> dict | str:
        params = dict(params)
        params["serviceKey"] = self.service_key
        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        return response.text
```

주의:

- 공공데이터 API마다 `serviceKey`, `ServiceKey`, `_type`, `type`, `returnType` 등 파라미터명이 다를 수 있다.
- 각 API 상세 페이지의 요청 변수를 확인해서 별도 client에서 맞춰야 한다.
- Gemini CLI는 URL과 파라미터명을 임의로 확정하지 말고, TODO 주석으로 API 상세 페이지 확인 필요 지점을 남겨야 한다.

---

### 6.3 3단계: 원본 데이터 저장

구현 파일:

```text
src/api_clients/*.py
```

모든 API 응답은 다음 규칙으로 저장한다.

```text
data/raw/{api_name}_{yyyyMMdd_HHmmss}.json
data/raw/{api_name}_{yyyyMMdd_HHmmss}.xml
```

예시:

```text
data/raw/smartfarm_dataset_20260613_153000.json
data/raw/pest_search_gray_mold_20260613_153030.xml
```

캐시 규칙:

- API 호출 성공 시 원본 저장
- 같은 실행에서 같은 API를 다시 호출하지 않아도 되도록 cache 사용 가능
- 캐시는 실제 API 응답만 허용
- 임의 생성 캐시는 금지

---

### 6.4 4단계: 파싱/전처리

구현 파일:

```text
src/preprocessing/parser.py
src/preprocessing/feature_engineering.py
```

목표 feature:

```text
temperature
humidity
light
co2
humidity_duration
temp_change
humidity_change
```

공공데이터에 CO2가 없으면 다음 중 하나를 선택한다.

```text
1. co2 feature 제외 후 input_dim을 6으로 변경
2. co2를 결측치로 두고 중앙값/평균값 대체
```

임의 랜덤값으로 채우는 것은 금지한다.

전처리 규칙:

- 문자열 숫자는 float로 변환
- 결측치는 NaN으로 처리
- 학습 전 결측 처리 방식을 명확히 적용
- 날짜/시간 기준 정렬
- 이전 시점 대비 변화량 계산
- 고습 지속 시간 또는 고습 연속 관측 횟수 계산

`humidity_duration` 계산 예시:

```text
습도 >= 85%인 관측이 연속되면 카운트 증가
습도 < 85%가 나오면 0으로 초기화
```

---

### 6.5 5단계: 위험도 라벨링

구현 파일:

```text
src/preprocessing/labeling.py
```

라벨:

```text
0 = 정상
1 = 주의
2 = 경고
3 = 심각
```

라벨링 규칙은 실제 공공데이터 feature에 적용한다.
더미데이터 라벨링이 아니다.

예시 구조:

```python
def make_risk_label(row: dict) -> int:
    score = 0

    if row["humidity"] >= HUMIDITY_CAUTION:
        score += 1
    if row["humidity"] >= HUMIDITY_SEVERE:
        score += 1
    if row["temperature"] <= LOW_TEMP_THRESHOLD:
        score += 1
    if row["humidity_duration"] >= 3:
        score += 1
    if abs(row["humidity_change"]) >= HUMIDITY_CHANGE_THRESHOLD:
        score += 1
    if abs(row["temp_change"]) >= TEMP_CHANGE_THRESHOLD:
        score += 1

    if score <= 1:
        return 0
    elif score == 2:
        return 1
    elif score <= 4:
        return 2
    else:
        return 3
```

반드시 README에 다음 내용을 적는다.

```text
공공데이터에는 병충해 위험도 정답 라벨이 없으므로,
본 프로젝트에서는 병해충 발생 조건과 스마트팜 환경 기준을 바탕으로
규칙 기반 라벨을 생성하여 MLP 학습에 사용했다.
```

---

### 6.6 6단계: MLP 모델 구현

구현 파일:

```text
src/ml/model.py
src/ml/train.py
src/ml/predict.py
src/ml/dataset.py
```

모델 요구사항:

- PyTorch 사용
- MLP 직접 구현
- 활성화 함수: ReLU 사용
- Optimizer: Adam 사용
- Loss: CrossEntropyLoss 사용
- 출력 클래스: 4개

모델 예시:

```python
import torch
import torch.nn as nn

class SmartFarmMLP(nn.Module):
    def __init__(self, input_dim: int, hidden1: int = 16, hidden2: int = 8, output_dim: int = 4):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(input_dim, hidden1),
            nn.ReLU(),
            nn.Linear(hidden1, hidden2),
            nn.ReLU(),
            nn.Linear(hidden2, output_dim)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.network(x)
```

학습 요구사항:

- train/test split 수행
- StandardScaler 또는 MinMaxScaler 사용
- scaler 저장
- model 저장
- epoch별 loss 출력
- accuracy 계산
- 데이터 개수가 너무 적으면 경고 출력

파일 저장:

```text
models/smartfarm_mlp.pt
models/scaler.pkl
output/training_metrics.json
```

---

### 6.7 7단계: AI Agent 구현

구현 파일:

```text
src/agent/smartfarm_agent.py
src/agent/risk_analyzer.py
src/agent/action_recommender.py
```

Agent 역할:

```text
1. 전처리된 최신 환경 데이터를 입력받는다.
2. MLP 모델로 위험도를 예측한다.
3. 입력 feature를 다시 분석하여 위험 원인을 찾는다.
4. 위험도별 대응 행동을 추천한다.
5. 처리 로그를 생성한다.
6. Ollama 로컬 LLM에 설명문 생성을 요청한다.
7. 최종 결과를 dict로 반환한다.
```

Agent 출력 형식:

```python
{
    "sensor_data": {...},
    "risk_level": "경고",
    "risk_label": 2,
    "risk_probability": {
        "정상": 0.05,
        "주의": 0.15,
        "경고": 0.70,
        "심각": 0.10
    },
    "reasons": [
        "습도가 높아 잿빛곰팡이병 위험이 증가할 수 있습니다."
    ],
    "actions": [
        "환기 장치를 가동하세요.",
        "습도 조절을 진행하세요."
    ],
    "llm_summary": "...",
    "logs": [
        "[STEP 1] 공공데이터 기반 입력 데이터 로드 완료",
        "[STEP 2] MLP 위험도 예측 완료",
        "[STEP 3] Agent 대응 행동 추천 완료"
    ]
}
```

---

### 6.8 8단계: Ollama 로컬 LLM 연동

구현 파일:

```text
src/llm/ollama_client.py
```

요구사항:

- `requests.post()`로 Ollama REST API 호출
- 기본 주소: `http://localhost:11434`
- endpoint: `/api/generate`
- `stream: false` 사용
- Ollama 실행 실패 시 전체 프로그램이 죽지 않도록 fallback 문장 생성
- LLM이 판단을 바꾸지 못하게 prompt에 명시

예시:

```python
class OllamaClient:
    def __init__(self, base_url: str, model: str, timeout: int = 60):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    def generate_summary(self, sensor_data, risk_level, reasons, actions) -> str:
        prompt = f"""
        너는 스마트팜 AI Agent 결과를 설명하는 보조 LLM이다.
        위험도 판단을 새로 하지 말고, 아래 결과를 사용자가 이해하기 쉽게 요약하라.

        센서 데이터: {sensor_data}
        MLP 예측 위험도: {risk_level}
        Agent 분석 원인: {reasons}
        Agent 추천 행동: {actions}

        조건:
        - 한국어로 작성
        - 5문장 이내
        - 과장 금지
        - 의료/농약 전문 진단처럼 단정하지 말 것
        - 농장 관리자가 바로 이해할 수 있게 작성
        """

        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False
            },
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json().get("response", "")
```

Fallback:

```text
Ollama 연결 실패 시:
"로컬 LLM 설명 생성에는 실패했지만, MLP Agent 분석 결과는 정상 생성되었습니다."
```

---

### 6.9 9단계: HTML 리포트 생성

구현 파일:

```text
src/report/report_generator.py
src/report/templates/report_template.html
```

출력 파일:

```text
output/report.html
```

HTML에 포함할 내용:

```text
프로젝트 제목
사용한 공공데이터 목록
최신 센서/환경 데이터
MLP 예측 위험도
위험도 확률
위험 원인
추천 행동
Ollama LLM 설명문
Agent 처리 로그
학습 지표
```

UI는 정적 HTML/CSS로만 구현한다.
JS는 필수 아님.

위험도 색상:

```text
정상: 초록 계열
주의: 노랑 계열
경고: 주황 계열
심각: 빨강 계열
```

---

### 6.10 10단계: main.py 실행 흐름

`main.py`는 다음 순서로 동작한다.

```text
1. 환경변수 로드
2. 공공데이터 API 호출
3. raw 데이터 저장
4. raw 데이터 파싱
5. feature 생성
6. 라벨 생성
7. processed 데이터 저장
8. MLP 학습
9. 최신 데이터 1건에 대해 Agent 분석
10. Ollama 설명문 생성
11. HTML 리포트 생성
12. 실행 결과 경로 출력
```

실행 명령:

```bash
python main.py
```

성공 메시지:

```text
[완료] AI Agent 분석이 끝났습니다.
[완료] HTML 리포트: output/report.html
```

---

## 7. 코딩 규칙

### 7.1 코드 스타일

- 함수와 클래스는 역할별로 분리한다.
- 한 함수는 한 가지 일만 한다.
- 매직 넘버는 `config/thresholds.py`로 분리한다.
- type hint를 가능한 한 작성한다.
- 예외 처리를 반드시 넣는다.
- print 남발 금지, 필요한 경우 logging 사용.
- 긴 함수 금지. 80줄을 넘기지 않도록 분리한다.

### 7.2 주석 규칙

주석은 다음 위치에 반드시 작성한다.

```text
API 파라미터가 불확실한 부분
공공데이터 필드명을 내부 feature명으로 매핑하는 부분
위험도 라벨링 기준
Ollama prompt 설계 부분
```

### 7.3 데이터 규칙

- `data/raw/`: API 원본만 저장
- `data/processed/`: 전처리된 CSV 저장
- `data/cache/`: 실제 API 응답 캐시만 저장
- 임의 생성 데이터 저장 금지

### 7.4 모델 규칙

- MLP 직접 구현
- ReLU 사용
- Adam 사용
- CrossEntropyLoss 사용
- Softmax는 예측 확률 출력 시에만 사용
- 학습 시 CrossEntropyLoss 앞에 Softmax를 넣지 않는다.

### 7.5 Git 규칙

`.gitignore`에 다음을 포함한다.

```text
.env
__pycache__/
*.pyc
models/*.pt
models/*.pkl
data/raw/*
data/processed/*
data/cache/*
output/*.html
```

단, 폴더 유지를 위해 `.gitkeep`은 허용한다.

---

## 8. 금지사항

다음은 절대 하지 않는다.

```text
더미데이터 생성
랜덤 센서 데이터 생성
공공데이터 API 실패 시 가짜 데이터로 대체
서비스키 코드 하드코딩
LLM이 위험도를 임의 재판단하게 만들기
Flask/FastAPI/Streamlit을 기본 구조로 추가
복잡한 DB 연동
로그인 기능 구현
이미지 기반 병해충 탐지 구현
```

---

## 9. README에 반드시 적을 내용

README.md에는 다음을 포함한다.

```text
1. 프로젝트 개요
2. 사용한 공공데이터 목록
3. 실행 환경
4. 설치 방법
5. .env 설정 방법
6. Ollama 실행 방법
7. 실행 명령
8. MLP 구조
9. Adam/ReLU 선택 이유
10. 라벨링 기준
11. Agent 역할
12. HTML 리포트 확인 방법
13. 한계점
```

Adam/ReLU 설명 예시:

```text
MLP의 은닉층 활성화 함수로 ReLU를 사용했다.
ReLU는 양수 입력은 그대로 통과시키고 음수 입력은 0으로 처리하여 비선형성을 부여하며,
센서 기반 분류 문제에서 학습이 비교적 안정적이다.
Optimizer는 Adam을 사용했다.
Adam은 학습률을 적응적으로 조절하여 MLP 학습에서 안정적인 수렴을 돕기 때문에 선택했다.
```

한계점 예시:

```text
본 프로젝트는 실제 병충해 진단 시스템이 아니라 공공데이터 기반 위험도 판단 프로토타입이다.
공공데이터에 병충해 위험도 정답 라벨이 직접 포함되어 있지 않기 때문에,
병해충 발생 조건을 참고한 규칙 기반 라벨링을 적용했다.
```

---

## 10. 최종 검증 체크리스트

Gemini CLI는 구현 완료 후 다음을 확인한다.

```text
[ ] 더미데이터 생성 코드가 없는가?
[ ] 공공데이터 API 호출 코드가 있는가?
[ ] API 원본 응답이 data/raw에 저장되는가?
[ ] 파싱된 processed CSV가 생성되는가?
[ ] MLP 모델이 PyTorch로 직접 구현되었는가?
[ ] ReLU를 사용했는가?
[ ] Adam optimizer를 사용했는가?
[ ] CrossEntropyLoss를 사용했는가?
[ ] 라벨링 규칙이 별도 파일/함수로 분리되었는가?
[ ] Agent가 위험도뿐 아니라 원인과 행동을 추천하는가?
[ ] Ollama 연결 실패 시 fallback이 있는가?
[ ] HTML 리포트가 생성되는가?
[ ] README에 실행 방법이 있는가?
```

---

## 11. 발표 시연 기준

시연은 다음 흐름으로 가능해야 한다.

```text
1. VSCode 터미널 열기
2. python main.py 실행
3. 공공데이터 API 호출 로그 확인
4. MLP 학습 로그 확인
5. Agent 분석 로그 확인
6. output/report.html 열기
7. 위험도, 원인, 추천 행동, LLM 설명 확인
```

발표 멘트 예시:

```text
본 프로젝트는 더미데이터가 아니라 공공데이터 API에서 가져온 스마트팜 환경 데이터를 사용했습니다.
수집한 데이터는 전처리 과정을 거쳐 MLP 입력 feature로 변환했고,
병해충 발생 조건을 기준으로 위험도 라벨을 생성했습니다.
MLP는 ReLU 활성화 함수와 Adam optimizer를 사용하여 정상, 주의, 경고, 심각 네 단계로 위험도를 분류합니다.
이후 Agent는 예측 결과와 입력 데이터를 함께 분석하여 위험 원인과 대응 행동을 추천하고,
Ollama 로컬 LLM은 그 결과를 사용자에게 보여줄 설명문으로 변환합니다.
```

---

## 12. 구현 우선순위

시간이 부족하면 다음 순서만 반드시 완성한다.

```text
1순위: 공공데이터 API 호출 및 raw 저장
2순위: 파싱/feature 생성
3순위: 라벨링
4순위: MLP 학습/예측
5순위: Agent 원인 분석/행동 추천
6순위: HTML 리포트
7순위: Ollama 설명문 생성
```

Ollama 연동은 중요하지만, 핵심 AI 판단은 MLP Agent이므로 API/MLP/Agent가 먼저다.
