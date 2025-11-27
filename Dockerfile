# Dockerfile
# 이 파일은 FastAPI 백엔드 서버를 Docker 컨테이너로 실행하기 위한 설정입니다.

# 1. 베이스 이미지: Python 3.11을 사용합니다
#    - slim 버전은 불필요한 패키지가 제거된 경량 버전입니다
FROM python:3.11-slim

# 2. 작업 디렉토리를 /app으로 설정합니다
#    - 컨테이너 내부에서 모든 명령어는 이 디렉토리에서 실행됩니다
WORKDIR /app

# 3. Python이 .pyc 파일을 생성하지 않도록 설정
#    - 컨테이너 환경에서는 불필요한 캐시 파일입니다
ENV PYTHONDONTWRITEBYTECODE=1

# 4. Python 출력을 버퍼링하지 않도록 설정
#    - 로그가 즉시 출력되도록 하여 디버깅이 쉬워집니다
ENV PYTHONUNBUFFERED=1

# 5. requirements.txt를 먼저 복사하고 의존성을 설치합니다
#    - 이렇게 하면 코드 변경 시 의존성을 다시 설치하지 않아도 됩니다 (Docker 캐시 활용)
COPY app/requirements.txt /app/requirements.txt

# 6. pip를 최신 버전으로 업그레이드하고 패키지를 설치합니다
#    - --no-cache-dir: pip 캐시를 저장하지 않아 이미지 크기를 줄입니다
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 7. 애플리케이션 코드를 컨테이너로 복사합니다
COPY ./app /app

# 8. 컨테이너가 8000번 포트를 사용한다는 것을 명시합니다
#    - 실제 포트 매핑은 docker-compose.yml이나 docker run 명령어에서 설정합니다
EXPOSE 8000

# 9. 컨테이너가 시작될 때 실행할 명령어
#    - uvicorn: FastAPI를 실행하는 ASGI 서버
#    - main:app: main.py 파일의 app 객체를 실행
#    - --host 0.0.0.0: 모든 네트워크 인터페이스에서 접속 허용
#    - --port 8000: 8000번 포트에서 실행
#    - --reload: 코드 변경 시 자동으로 서버 재시작 (개발 모드용, 프로덕션에서는 제거)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
