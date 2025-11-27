# 의약품 관리 앱 백엔드 (FastAPI)

팀 프로젝트로 개발하는 의약품 관리 모바일 앱의 백엔드 서버입니다.

## 📋 프로젝트 개요

약봉투 사진(OCR) 또는 음성(STT)을 통해 약 정보를 입력받아 분석하고, 복용 시간에 맞춰 알람을 제공하는 서비스의 백엔드 API입니다.

### 주요 기능

- **OCR (광학 문자 인식)**: 약봉투 사진에서 텍스트 추출 및 약 정보 파싱
- **STT (음성-텍스트 변환)**: 음성으로 약 정보 입력 가능
- **약 정보 관리**: 복용 시간, 횟수, 약 종류 등 관리
- **알람 시스템**: 정해진 시간에 알람 전송
- **리포트 기능** (추후): 복용 기록 및 통계

## 🛠️ 기술 스택

- **웹 프레임워크**: FastAPI
- **데이터베이스**: PostgreSQL
- **ORM**: SQLAlchemy
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
│   │   └── v1/
│   │       └── ocr.py       # OCR 엔드포인트
│   │
│   ├── core/                # 핵심 설정
│   │   ├── config.py        # 환경 변수 관리
│   │   └── database.py      # DB 연결 설정
│   │
│   ├── models/              # SQLAlchemy ORM 모델
│   │   └── user_text.py
│   │
│   └── schemas/             # Pydantic 스키마
│       └── user_text.py
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

그 다음, `.env` 파일을 열어서 필요한 값들을 설정해주세요:

```env
# 데이터베이스 URL (기본값 사용 - 수정 불필요)
DATABASE_URL=postgresql+psycopg2://postgres:postgres@db:5432/app_db

# 애플리케이션 환경 (개발 환경)
APP_ENV=dev

# Azure OCR/STT 키 (나중에 Azure 서비스 생성 후 입력)
AZURE_OCR_KEY=YOUR_OCR_KEY_HERE
AZURE_OCR_ENDPOINT=YOUR_OCR_ENDPOINT_HERE
AZURE_TTS_KEY=YOUR_TTS_KEY_HERE
AZURE_TTS_ENDPOINT=YOUR_TTS_ENDPOINT_HERE
```

> **참고**: Azure 키는 나중에 OCR/STT 기능을 구현할 때 입력하면 됩니다.

### 3. Docker로 서버 실행

Docker Compose를 사용하여 FastAPI 서버와 PostgreSQL 데이터베이스를 한 번에 실행합니다.

```bash
docker-compose up --build
```

**명령어 설명**:
- `docker-compose up`: 서비스를 시작합니다
- `--build`: Docker 이미지를 새로 빌드합니다 (처음 실행할 때 또는 코드가 변경되었을 때)

**실행 결과**:
```
✔ Container app-postgres-db started
✔ Container app-fastapi-server started
```

서버가 정상적으로 시작되면 다음 메시지를 볼 수 있습니다:
```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 4. API 문서 확인

브라우저에서 다음 URL로 접속하면 자동 생성된 API 문서를 볼 수 있습니다:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 5. 서버 종료

서버를 종료하려면 터미널에서 **Ctrl + C**를 누르면 됩니다.

컨테이너를 완전히 정리하려면:
```bash
docker-compose down
```

데이터베이스 볼륨까지 삭제하려면 (주의: 모든 데이터가 삭제됩니다):
```bash
docker-compose down -v
```

## 🔧 개발 모드

### 코드 수정 시 자동 리로드

`docker-compose.yml`에서 볼륨 마운트와 `--reload` 옵션이 설정되어 있어, 코드를 수정하면 자동으로 서버가 재시작됩니다.

```yaml
volumes:
  - ./app:/app  # 로컬 코드를 컨테이너에 마운트
```

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

3. **PostgreSQL 설정** (별도로 설치 필요):
   - `.env` 파일에서 `DATABASE_URL`을 로컬 PostgreSQL로 변경

4. **서버 실행**:
   ```bash
   cd app
   uvicorn main:app --reload
   ```

## 📝 API 사용 예시

### 예시 엔드포인트: 텍스트 저장

```bash
curl -X POST "http://localhost:8000/api/v1/ocr/texts" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "테스트 약 정보",
    "content": "하루 3회, 식후 30분"
  }'
```

**응답**:
```json
{
  "id": 1,
  "title": "테스트 약 정보",
  "content": "하루 3회, 식후 30분"
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
- `test:` 테스트 코드 추가
- `chore:` 빌드, 설정 파일 수정

## 🐛 트러블슈팅

### Docker가 실행되지 않을 때

1. Docker Desktop이 실행 중인지 확인
2. Windows의 경우 WSL2가 설치되어 있는지 확인

### 포트가 이미 사용 중일 때

다른 프로그램이 8000 또는 5432 포트를 사용 중일 수 있습니다.

**해결 방법**: `docker-compose.yml`에서 포트를 변경
```yaml
ports:
  - "8080:8000"  # 로컬 포트를 8080으로 변경
```

### 데이터베이스 연결 오류

1. PostgreSQL 컨테이너가 정상적으로 시작되었는지 확인:
   ```bash
   docker-compose ps
   ```

2. 로그 확인:
   ```bash
   docker-compose logs db
   ```

## 📚 추가 문서

- [구현 계획서](C:\Users\UserK\.gemini\antigravity\brain\60ac66ff-5363-42ac-bd17-bf688896b3b0\implementation_plan.md)
- [작업 목록](C:\Users\UserK\.gemini\antigravity\brain\60ac66ff-5363-42ac-bd17-bf688896b3b0\task.md)
- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [Docker 공식 문서](https://docs.docker.com/)

## 📧 문의

팀 내부 문서나 이슈 트래커를 참고해주세요.

---

**Happy Coding! 🚀**