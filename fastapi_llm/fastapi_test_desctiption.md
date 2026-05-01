
*   **`main`**: `main.py` 파일을 의미합니다.
*   **`app`**: `main.py` 안에서 정의한 `app = FastAPI()` 객체를 의미합니다.
*   **`--reload`**: 코드를 수정할 때마다 서버가 자동으로 재시작되는 옵션입니다.
*   **성공 시**: 터미널에 `Uvicorn running on http://127.0.0.1:800로컬에서 FastAPI와 Django가 연동된 시스템을 테스트하는 방법을 **어느 폴더에서 어떤 명령어를 입력해야 하는지**를 중심으로 아주 상세하게 설명해 드릴게요.

이미지 `image_58e6bf.png`를 기준으로, 모든 작업의 중심은 프로젝트의 최상위 폴더인 **`fastapi_llm`** (또는 `main.py`가 있는 루트 폴더)입니다.

---

### 1단계: 터미널 위치 이동 (가장 중요)
명령어를 입력할 터미널(또는 CMD/PowerShell)을 열고, `main.py` 파일이 바로 보이는 **프로젝트 루트 폴더**로 이동해야 합니다.

*   **경로 확인**: 터미널에 `ls` (Mac/Linux) 또는 `dir` (Windows)을 입력했을 때 `main.py`, `services/`, `visa_la_vista/`, `.env` 등이 한눈에 보여야 합니다.
*   **명령어**:
    ```bash
    # 예시 (실제 본인의 경로로 이동)
    cd /상위폴더경로/fastapi_llm
    ```

---

### 2단계: 가상환경 활성화 & 패키지 확인
Django와 FastAPI 패키지가 설치된 가상환경이 있다면 반드시 먼저 활성화해야 합니다.

*   **가상환경 활성화**:
    *   (Windows): `venv\Scripts\activate`
    *   (Mac/Linux): `source venv/bin/activate`
*   **필수 패키지 설치**: 혹시 모르니 아래 패키지들이 설치되어 있는지 확인하세요.
    ```bash
    pip install uvicorn fastapi python-dotenv django asgiref
    ```

---

### 3단계: FastAPI 서버 실행
루트 폴더(`fastapi_llm`)에서 다음 명령어를 입력합니다.
```bash
uvicorn main:app --reload





Step 1: 터미널 1 (Ollama 실행)
    먼저 LLM 엔진을 준비합니다.

    위치: 상관없음 (어느 폴더에서든 실행 가능)

    명령어: ollama run llama3.2:3b (모델이 잘 도나 확인용)

    확인이 끝났으면 Ctrl+D로 나오셔도 서버는 백그라운드에서 계속 돌고 있습니다.

Step 2: 터미널 2 (FastAPI 서버 실행)
    위치: fastapi_llm (루트 폴더)

    명령어: uvicorn main:app --reload --port 8001

    이때 main.py에 작성한 Django 초기화 코드 덕분에 visa_la_vista DB와 연결됩니다.

Step 3: 브라우저 (API 호출)
    주소: [http://127.0.0.1:8001/docs](http://127.0.0.1:8001/docs) 접속

    동작: POST /admission/chat/v2 실행

    흐름:

    chat.py가 요청을 받음.

    runner.py의 chat_v2_logic 실행.

    로컬 Ollama에 질문을 던져 답변을 가져옴.

    Django DB(ChatMessage 모델)에 질문과 답변을 저장함.

    사용자에게 최종 응답 반환.