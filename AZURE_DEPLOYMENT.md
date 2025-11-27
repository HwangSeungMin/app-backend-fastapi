# Azure 배포 설정 가이드

## 📋 이 문서의 목적

Azure 배포를 위해 필요한 리소스 생성 및 설정을 단계별로 안내합니다.

## 🔧 Phase 1: Azure 리소스 생성 (Azure Portal에서 수동 작업)

### 1. Azure Container Registry 생성

1. https://portal.azure.com 접속
2. "리소스 만들기" → "Container Registry" 검색
3. 다음과 같이 설정:
   ```
   리소스 그룹: rg-medicine-app (새로 만들기)
   레지스트리 이름: medicineappregistry (고유 이름 필요)
   위치: Korea Central
   SKU: Basic
   ```
4. "검토 + 만들기" → "만들기"
5. 생성 완료 후 "리소스로 이동"
6. **왼쪽 메뉴 → 액세스 키**:
   - "관리 사용자" 활성화
   - **로그인 서버**: `medicineappregistry.azurecr.io` 복사
   - **사용자 이름**: 복사
   - **암호**: 복사 (password 또는 password2)

### 2. Azure App Service 생성

#### 옵션 A: App Service (권장)

1. "리소스 만들기" → "Web App" 검색
2. 다음과 같이 설정:
   ```
   리소스 그룹: rg-medicine-app (위에서 만든 것 선택)
   이름: medicine-api (고유 이름 필요)
   게시: Docker 컨테이너
   운영 체제: Linux
   지역: Korea Central
   App Service 플랜: B1 Basic (또는 F1 Free)
   ```
3. "Docker" 탭으로 이동:
   ```
   옵션: 단일 컨테이너
   이미지 원본: Azure Container Registry
   레지스트리: medicineappregistry
   이미지: app-backend
   태그: latest
   ```
4. "검토 + 만들기" → "만들기"
5. 생성 완료 후 "리소스로 이동"
6. **왼쪽 메뉴 → 배포 센터**:
   - 스크롤 다운하여 "게시 프로필 다운로드" 클릭
   - 다운로드된 XML 파일 내용을 복사 (나중에 GitHub Secrets에 사용)

### 3. App Service 환경 변수 설정

1. Azure Portal → App Service (medicine-api) → "구성"
2. "애플리케이션 설정" 탭에서 다음 변수들 추가:
   ```
   APP_ENV = prod
   WEBSITES_PORT = 8000
   ```
3. "저장" 클릭

## 🔑 Phase 2: GitHub Secrets 설정

GitHub 저장소 → Settings → Secrets and variables → Actions → "New repository secret"

다음 Secrets를 추가:

| Secret 이름 | 값 | 설명 |
|-------------|---|------|
| `ACR_LOGIN_SERVER` | `medicineappregistry.azurecr.io` | ACR 로그인 서버 |
| `ACR_USERNAME` | ACR 사용자 이름 | ACR 액세스 키에서 복사 |
| `ACR_PASSWORD` | ACR 암호 | ACR 액세스 키에서 복사 |
| `AZURE_WEBAPP_NAME` | `medicine-api` | App Service 이름 |
| `AZURE_WEBAPP_PUBLISH_PROFILE` | 게시 프로필 XML 내용 | App Service 배포 센터에서 다운로드한 파일 |

## ✅ Phase 3: 배포 테스트

### 로컬에서 수동 배포 (선택사항)

```bash
# 1. Azure CLI 설치 확인
az --version

# 2. Azure 로그인
az login

# 3. ACR 로그인
az acr login --name medicineappregistry

# 4. Docker 이미지 빌드
docker build -t medicineappregistry.azurecr.io/app-backend:latest .

# 5. 이미지 푸시
docker push medicineappregistry.azurecr.io/app-backend:latest

# 6. App Service 재시작
az webapp restart --name medicine-api --resource-group rg-medicine-app
```

### GitHub Actions 자동 배포

1. `.github/workflows/deploy.yml` 파일을 `develop` 브랜치에 커밋
2. GitHub Actions 탭에서 워크플로우 실행 확인
3. 성공 시 공개 URL 접속:
   - https://medicine-api.azurewebsites.net/
   - https://medicine-api.azurewebsites.net/docs

## 🐛 문제 해결

### Docker 이미지 푸시 실패
```bash
az acr login --name medicineappregistry
```

### App Service 시작 실패
- Azure Portal → App Service → "로그 스트림"에서 로그 확인
- "구성"에서 환경 변수 확인

### GitHub Actions 실패
- GitHub Actions 탭에서 실패 로그 확인
- Secrets 값이 올바른지 확인

## 📝 체크리스트

배포 전:
- [ ] Azure Container Registry 생성 완료
- [ ] ACR 관리자 계정 활성화 및 자격 증명 복사
- [ ] Azure App Service 생성 완료
- [ ] 게시 프로필 다운로드 완료
- [ ] App Service 환경 변수 설정 완료
- [ ] GitHub Secrets 5개 모두 설정 완료
- [ ] `.github/workflows/deploy.yml` 파일 작성 완료

배포 후:
- [ ] GitHub Actions 워크플로우 실행 성공
- [ ] Azure App Service URL 접속 확인
- [ ] Swagger UI 정상 표시 확인

## 🎯 예상 비용

- **Container Registry (Basic)**: 약 $5/월
- **App Service (B1 Basic)**: 약 $13/월
- **App Service (F1 Free)**: 무료 (제한적)

총 예상 비용: 약 $18/월 (또는 F1 사용 시 $5/월)
