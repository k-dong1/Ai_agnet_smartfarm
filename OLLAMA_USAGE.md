# Ollama 사용 가이드

## 1. Ollama가 뭔지

Ollama는 로컬 PC에서 LLM을 실행할 수 있게 해주는 도구다.
ChatGPT처럼 외부 서버에 요청하는 방식이 아니라, 설치한 모델을 내 컴퓨터에서 실행한다.

이 프로젝트에서 Ollama의 역할은 다음과 같다.

```text
MLP Agent가 위험도 판단
→ Agent가 원인과 대응 행동 생성
→ Ollama 로컬 LLM이 이를 자연어 설명문으로 정리
→ HTML 리포트에 표시
```

중요:

```text
Ollama가 위험도를 직접 판단하는 것이 아니다.
위험도 판단은 MLP 모델과 Agent 로직이 한다.
Ollama는 결과 설명을 자연스럽게 바꿔주는 보조 역할이다.
```

---

## 2. 설치 확인

이미 설치되어 있다면 PowerShell 또는 VSCode 터미널에서 다음 명령어를 실행한다.

```bash
ollama --version
```

정상이라면 버전 정보가 나온다.

설치되어 있는데 명령어가 안 먹으면:

1. Ollama 앱이 실행 중인지 확인한다.
2. Windows 작업 표시줄 오른쪽 아래 트레이에 Ollama 아이콘이 있는지 확인한다.
3. PowerShell을 새로 열어 다시 실행한다.
4. 그래도 안 되면 PC 재부팅 후 다시 확인한다.

---

## 3. Ollama 서버 실행 확인

Ollama가 실행 중이면 로컬 API가 자동으로 열린다.
기본 주소는 다음과 같다.

```text
http://localhost:11434
```

브라우저에서 아래 주소를 열어본다.

```text
http://localhost:11434
```

정상 실행 중이면 Ollama가 실행 중이라는 문구가 나온다.

또는 PowerShell에서 확인한다.

```bash
curl http://localhost:11434/api/tags
```

설치된 모델 목록이 JSON 형태로 나오면 정상이다.

만약 연결이 안 되면 다음 명령어를 실행한다.

```bash
ollama serve
```

이미 Ollama가 백그라운드에서 실행 중이면 `address already in use` 같은 메시지가 나올 수 있다.
이 경우는 이미 서버가 켜져 있다는 뜻일 수 있다.

---

## 4. 추천 모델

노트북/데스크톱 성능을 고려해서 작은 모델부터 사용한다.

### 1순위 추천

```bash
ollama pull qwen2.5:3b
```

사용 이유:

```text
한국어 설명도 어느 정도 가능
3B라서 비교적 가벼움
발표용 요약문 생성에 충분함
```

### 더 가벼운 모델이 필요할 때

```bash
ollama pull gemma2:2b
```

또는 설치 가능한 최신 소형 모델을 사용한다.

### 모델 실행 테스트

```bash
ollama run qwen2.5:3b
```

프롬프트가 뜨면 다음처럼 입력해본다.

```text
토마토 스마트팜에서 습도가 높을 때 주의해야 할 점을 3문장으로 설명해줘.
```

답변이 나오면 정상이다.

종료는 다음 중 하나를 사용한다.

```text
/bye
Ctrl + D
Ctrl + C
```

---

## 5. Python 프로젝트에서 Ollama 쓰는 방식

이 프로젝트에서는 터미널에서 직접 대화하는 것이 아니라, Python 코드가 Ollama API를 호출한다.

Ollama는 기본적으로 다음 API를 제공한다.

```text
POST http://localhost:11434/api/generate
```

Python 예시:

```python
import requests

response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "qwen2.5:3b",
        "prompt": "토마토 스마트팜 위험도 분석 결과를 3문장으로 요약해줘.",
        "stream": False
    },
    timeout=60
)

response.raise_for_status()
print(response.json()["response"])
```

`stream: False`를 넣는 이유:

```text
기본 스트리밍 응답은 여러 줄로 쪼개져서 오기 때문에 파싱이 귀찮다.
stream: false를 주면 한 번에 JSON 응답을 받을 수 있다.
```

---

## 6. 이 프로젝트용 Ollama Client 예시

`src/llm/ollama_client.py` 파일에 다음 구조로 구현한다.

```python
import requests


class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "qwen2.5:3b", timeout: int = 60):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    def generate_summary(self, sensor_data: dict, risk_level: str, reasons: list[str], actions: list[str]) -> str:
        prompt = self._build_prompt(sensor_data, risk_level, reasons, actions)

        try:
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
            return response.json().get("response", "").strip()

        except Exception as e:
            return (
                "로컬 LLM 설명 생성에는 실패했지만, "
                "MLP Agent의 위험도 분석 결과와 추천 행동은 정상 생성되었습니다. "
                f"오류: {e}"
            )

    def _build_prompt(self, sensor_data: dict, risk_level: str, reasons: list[str], actions: list[str]) -> str:
        return f"""
너는 스마트팜 AI Agent의 분석 결과를 사용자에게 설명하는 보조 LLM이다.
위험도를 새로 판단하지 말고, 반드시 아래 MLP Agent 결과만 바탕으로 설명하라.

[센서/환경 데이터]
{sensor_data}

[MLP 예측 위험도]
{risk_level}

[Agent 분석 원인]
{reasons}

[Agent 추천 행동]
{actions}

작성 조건:
- 한국어로 작성
- 5문장 이내
- 너무 과장하지 말 것
- 실제 진단처럼 단정하지 말 것
- 농장 관리자가 바로 이해할 수 있게 설명할 것
"""
```

---

## 7. `.env` 설정

프로젝트 루트에 `.env` 파일을 만든다.

```text
DATA_GO_KR_SERVICE_KEY=공공데이터포털_서비스키
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:3b
```

주의:

```text
.env 파일은 Git에 올리지 않는다.
.env.example 파일만 제출한다.
```

---

## 8. 연결 테스트 코드

`test_ollama.py`를 임시로 만들어서 테스트할 수 있다.

```python
import os
import requests
from dotenv import load_dotenv

load_dotenv()

base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
model = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")

response = requests.post(
    f"{base_url}/api/generate",
    json={
        "model": model,
        "prompt": "Ollama 연결 테스트입니다. 한국어로 한 문장만 답하세요.",
        "stream": False
    },
    timeout=60
)

response.raise_for_status()
print(response.json()["response"])
```

실행:

```bash
python test_ollama.py
```

정상 출력 예시:

```text
Ollama 연결이 정상적으로 작동하고 있습니다.
```

---

## 9. 자주 나는 오류와 해결

### 오류 1: `ollama` 명령어를 찾을 수 없음

해결:

```text
PowerShell을 새로 열기
Ollama 설치 확인
PC 재부팅
Ollama 재설치
```

---

### 오류 2: `connection refused`

의미:

```text
Ollama 서버가 실행 중이 아님
```

해결:

```bash
ollama serve
```

또는 Ollama 앱을 직접 실행한다.

---

### 오류 3: `model not found`

의미:

```text
지정한 모델이 아직 다운로드되지 않음
```

해결:

```bash
ollama pull qwen2.5:3b
```

또는 `.env`의 `OLLAMA_MODEL` 값을 실제 설치된 모델명으로 바꾼다.

설치된 모델 확인:

```bash
ollama list
```

---

### 오류 4: 응답이 너무 느림

원인:

```text
모델이 너무 큼
CPU로만 실행 중
RAM 부족
```

해결:

```text
더 작은 모델 사용
qwen2.5:3b 또는 gemma2:2b 사용
프롬프트 짧게 만들기
max token 제한 옵션 추가 고려
```

---

### 오류 5: 이상한 설명을 함

원인:

```text
LLM이 위험도를 새로 추론하려고 함
```

해결:

프롬프트에 다음 문장을 반드시 넣는다.

```text
위험도를 새로 판단하지 말고, 반드시 MLP Agent 결과만 바탕으로 설명하라.
```

---

## 10. 발표에서 Ollama 설명하는 법

발표에서는 길게 설명할 필요 없다.

```text
본 프로젝트에서는 로컬 LLM인 Ollama를 사용했습니다.
단, Ollama가 병충해 위험도를 직접 판단하는 것은 아니고,
MLP Agent가 예측한 위험도와 추천 행동을 사용자가 이해하기 쉬운 자연어 설명으로 변환하는 보조 역할을 담당합니다.
핵심 판단은 PyTorch 기반 MLP 모델과 Agent 로직에서 수행됩니다.
```

---

## 11. 최종 확인 체크리스트

```text
[ ] ollama --version이 정상 출력되는가?
[ ] ollama list로 모델 목록이 보이는가?
[ ] qwen2.5:3b 또는 선택한 모델이 설치되어 있는가?
[ ] http://localhost:11434/api/tags 호출이 되는가?
[ ] Python requests로 /api/generate 호출이 되는가?
[ ] stream: false를 넣었는가?
[ ] Ollama 실패 시 fallback 문장이 있는가?
[ ] LLM이 위험도를 직접 판단하지 않도록 prompt를 제한했는가?
```

---

## 12. 참고 출처

- Ollama API Introduction: https://docs.ollama.com/api/introduction
- Ollama Generate API: https://docs.ollama.com/api/generate
- Ollama Streaming: https://docs.ollama.com/api/streaming
- Ollama Authentication: https://docs.ollama.com/api/authentication
- Ollama Windows Guide: https://docs.ollama.com/windows
