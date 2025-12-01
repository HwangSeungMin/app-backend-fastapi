## 🚀 빠른 시작


```bash
# 1. 설치
cd d:/yakkobak_be

git clone <repository-url>

python --version # 3.9 이상 

python -m venv venv # 가상환경 생성

# 가상환경 접속 
venv\Scripts\activate #Windows 
source venv/bin/activate  #Linux/Mac 

python.exe -m pip install --upgrade pip

pip install -r requirements.txt

# 2. 환경 설정
cp .env.example .env
# .env 파일에서 API 키 설정

## 기본 요구 조건 : Docker Desktop 설치 및 실행 

# 3. Elasticsearch & Kibana 시작
docker-compose up -d

# 4. 데이터 색인
python scripts/setup_data.py --api-key YOUR_KEY --max-items 5000

# 5. 서버 시작
uvicorn api.app:app --reload --host 0.0.0.0 --port 8000
```
# 의약품 관리 앱 백엔드 (FastAPI)

> **계획 변경**: 데이터베이스를 사용하지 않습니다. 플러터 앱에서 로컬 DB로 알람 정보를 관리합니다.

팀 프로젝트로 개발하는 의약품 관리 모바일 앱의 백엔드 API 서버입니다.

## 📋 프로젝트 개요

약봉투 사진(OCR) 또는 음성(STT)을 통해 약 정보를 추출하여 플러터 앱으로 전달하는 Stateless API 서버입니다.

### 주요 기능

- **OCR (광학 문자 인식)**: 약봉투 사진에서 텍스트 추출 및 약 정보 파싱
- **STT (음성-텍스트 변환)**: 음성으로 약 정보 입력 가능
- **약 정보 파싱**: 복용 시간, 횟수, 약 종류 등 추출 및 반환

### 아키텍처

```
┌─────────────┐      HTTP Request     ┌──────────────────┐
│             │ ──────────────────────> │                  │
│  Flutter    │   (이미지/음성 파일)   │  FastAPI Server  │
│  App        │                         │                  │
│  (로컬 DB)  │ <────────────────────── │ (Stateless)      │
└─────────────┘   JSON Response (파싱된 약 정보) └──────────────────┘
                                                │
                                                │ API Call
                                                ▼
                                        ┌───────────────┐
                                        │ Azure         │
                                        │ - OCR         │
                                        │ - STT         │
                                        └───────────────┘
```

## 🛠️ 기술 스택

- **웹 프레임워크**: FastAPI
- **컨테이너**: Docker, Docker Compose
- **외부 서비스**: Azure Computer Vision (OCR), Azure Speech Service (STT)
- **배포**: Azure Container Registry, Azure App Service

## 📂 프로젝트 구조

```
app-backend-fastapi/
├── app/
│   ├── main.py              # FastAPI 애플리케이션 진입점
│   ├── requirements.txt     # Python 의존성
│   │
│   ├── api/                 # API 라우터
│   │   └── v1/              # API 버전 1
│   │       ├── ocr.py       # OCR 엔드포인트 (예정)
│   │       └── stt.py       # STT 엔드포인트 (예정)
│   │
│   ├── core/                # 핵심 설정
│   │   └── config.py        # 환경 변수 관리
│   │
│   └── services/            # 비즈니스 로직 (예정)
│       ├── ocr_service.py   # Azure OCR 연동
│       ├── stt_service.py   # Azure STT 연동
│       └── parser.py        # 텍스트 파싱 로직
│
├── .env                     # 환경 변수 (직접 생성 필요)
├── .env.example             # 환경 변수 예시
├── .gitignore
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## 🚀 시작하기

### 사전 요구사항

- **Docker Desktop** 설치 필요
  - [Windows용 Docker Desktop 다운로드](https://www.docker.com/products/docker-desktop/)
  - 설치 후 Docker Desktop을 실행해주세요
- **Git** (이미 설치되어 있을 것입니다)

### 1. 저장소 클론

```bash
git clone <repository-url>
cd app-backend-fastapi
```

### 2. 환경 변수 파일 생성

`.env.example` 파일을 복사하여 `.env` 파일을 만들어주세요.

**Windows (PowerShell)**:
```powershell
Copy-Item .env.example .env
```

**Windows (명령 프롬프트)**:
```cmd
copy .env.example .env
```

**Mac/Linux**:
```bash
cp .env.example .env
```

그 다음, `.env` 파일을 열어서 Azure 키를 설정해주세요:

```env
# 애플리케이션 환경 (개발 환경)
APP_ENV=dev

# Azure OCR/STT 키 (Azure Portal에서 생성 후 입력)
AZURE_OCR_KEY=YOUR_OCR_KEY_HERE
AZURE_OCR_ENDPOINT=YOUR_OCR_ENDPOINT_HERE
AZURE_TTS_KEY=YOUR_TTS_KEY_HERE
AZURE_TTS_ENDPOINT=YOUR_TTS_ENDPOINT_HERE
```

> **참고**: Azure 키는 나중에 OCR/STT 기능을 구현할 때 입력하면 됩니다.

### 3. Docker로 서버 실행

```bash
docker-compose up --build
```

**명령어 설명**:
- `docker-compose up`: 서비스를 시작합니다
- `--build`: Docker 이미지를 새로 빌드합니다

**실행 결과**:
```
✔ Container app-fastapi-server started
```

서버가 정상적으로 시작되면:
```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 4. API 문서 확인

브라우저에서 다음 URL로 접속하면 자동 생성된 API 문서를 볼 수 있습니다:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 5. 서버 종료

터미널에서 **Ctrl + C**를 누르면 서버가 종료됩니다.

컨테이너를 완전히 정리하려면:
```bash
docker-compose down
```

## 🔧 개발 모드

### 코드 수정 시 자동 리로드

`docker-compose.yml`에서 볼륨 마운트와 `--reload` 옵션이 설정되어 있어, 코드를 수정하면 자동으로 서버가 재시작됩니다.

### 로컬에서 Python으로 직접 실행 (선택사항)

Docker 없이 로컬 환경에서 실행하려면:

1. **가상환경 생성**:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # source .venv/bin/activate  # Mac/Linux
   ```

2. **패키지 설치**:
   ```bash
   pip install -r app/requirements.txt
   ```

3. **서버 실행**:
   ```bash
   cd app
   uvicorn main:app --reload
   ```

## 📝 API 사용 예시

### 헬스 체크

```bash
curl http://localhost:8000/
```

**응답**:
```json
{
  "message": "Medicine Management API",
  "status": "running"
}
```

### OCR API (예정)

```bash
curl -X POST "http://localhost:8000/api/v1/ocr/extract" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@medicine_image.jpg"
```

**예상 응답**:
```json
{
  "extracted_text": "하루 3회, 식후 30분",
  "parsed_info": {
    "frequency": 3,
    "timing": "식후",
    "timing_minutes": 30
  }
}
```

## 🤝 팀 협업 가이드

### Git 브랜치 전략

1. **새로운 기능 개발**:
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/기능명
   ```

2. **코드 작성 후 커밋**:
   ```bash
   git add .
   git commit -m "feat: 기능 설명"
   ```

3. **원격 저장소에 푸시**:
   ```bash
   git push origin feature/기능명
   ```

4. **Pull Request 생성**
   - GitHub에서 `feature/기능명` → `develop`으로 PR 생성
   - 팀원의 코드 리뷰 받기
   - 승인 후 merge

### 커밋 메시지 컨벤션

- `feat:` 새로운 기능 추가
- `fix:` 버그 수정
- `docs:` 문서 수정
- `refactor:` 코드 리팩토링
- `chore:` 빌드, 설정 파일 수정

## 🐛 트러블슈팅

### Docker가 실행되지 않을 때

1. Docker Desktop이 실행 중인지 확인
2. Windows의 경우 WSL2가 설치되어 있는지 확인

### 포트가 이미 사용 중일 때

다른 프로그램이 8000 포트를 사용 중일 수 있습니다.

**해결 방법**: `docker-compose.yml`에서 포트를 변경
```yaml
ports:
  - "8080:8000"  # 로컬 포트를 8080으로 변경
```

## 📚 다음 단계

### 구현 예정 기능

1. **OCR API 구현**
   - Azure Computer Vision 연동
   - 이미지 업로드 엔드포인트
   - 텍스트 추출 및 파싱

2. **STT API 구현**
   - Azure Speech Service 연동
   - 음성 파일 업로드 엔드포인트
   - 텍스트 변환 및 파싱

3. **Azure 배포**
   - Container Registry 설정
   - App Service 또는 Container Instances 배포
   - GitHub Actions CI/CD 설정

## 📧 문의

팀 내부 문서나 이슈 트래커를 참고해주세요.

---

**Happy Coding! 🚀**
