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