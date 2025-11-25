# Windows 터미널 한글 깨짐 해결 가이드

Windows 환경에서 Python 및 배치 스크립트 실행 시 한글이 깨지는 문제를 해결하는 방법입니다.

## 목차

1. [빠른 해결 방법](#빠른-해결-방법)
2. [영구 해결 방법](#영구-해결-방법)
3. [Python 스크립트 한글 깨짐](#python-스크립트-한글-깨짐)
4. [PowerShell 한글 깨짐](#powershell-한글-깨짐)
5. [VSCode 터미널 설정](#vscode-터미널-설정)

---

## 빠른 해결 방법

### 방법 1: 자동 스크립트 실행

프로젝트 루트에서 실행:
```cmd
scripts\fix_encoding.bat
```

### 방법 2: 수동으로 인코딩 변경

터미널에서 다음 명령어 실행:
```cmd
chcp 65001
```

이 명령어는 코드 페이지를 UTF-8(65001)로 변경합니다.

**코드 페이지 종류:**
- `936` - 중국어 간체 (GBK)
- `949` - 한국어 (EUC-KR)
- `65001` - UTF-8 ✅ 권장

---

## 영구 해결 방법

### 방법 1: 레지스트리 설정 (권장)

1. **레지스트리 편집기 실행**
   ```cmd
   regedit
   ```

2. **다음 경로로 이동**
   ```
   HKEY_LOCAL_MACHINE\Software\Microsoft\Command Processor
   ```

3. **새 문자열 값 만들기**
   - 우클릭 → 새로 만들기 → 문자열 값
   - 이름: `Autorun`
   - 값 데이터: `chcp 65001 >nul`

4. **레지스트리 편집기 종료 및 터미널 재시작**

### 방법 2: Windows Terminal 설정

**Windows Terminal 사용 시:**

1. `Ctrl + ,` 눌러 설정 열기
2. 설정 → 프로필 → 기본값 또는 특정 프로필 선택
3. "추가 설정" → "고급" 탭
4. "텍스트 인코딩" → `UTF-8` 선택
5. 저장 후 터미널 재시작

### 방법 3: 환경 변수 설정

1. **시스템 환경 변수 열기**
   - `Win + Pause` → 고급 시스템 설정 → 환경 변수

2. **시스템 변수에 추가**
   - 변수 이름: `PYTHONIOENCODING`
   - 변수 값: `utf-8`

3. **적용 후 터미널 재시작**

---

## Python 스크립트 한글 깨짐

### 방법 1: 파일 상단에 인코딩 선언

```python
# -*- coding: utf-8 -*-
"""
스크립트 설명
"""
```

### 방법 2: print() 함수 인코딩 설정

```python
import sys
import io

# stdout 인코딩을 UTF-8로 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
```

### 방법 3: 환경 변수 사용

터미널에서 실행 전:
```cmd
set PYTHONIOENCODING=utf-8
python your_script.py
```

또는 스크립트 내부에서:
```python
import os
os.environ['PYTHONIOENCODING'] = 'utf-8'
```

### 방법 4: logger 설정

```python
import logging

# UTF-8 인코딩으로 로거 설정
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(message)s'))
handler.stream.reconfigure(encoding='utf-8')
logger.addHandler(handler)
```

---

## PowerShell 한글 깨짐

### 방법 1: 프로필 설정

1. **PowerShell 프로필 열기**
   ```powershell
   notepad $PROFILE
   ```

2. **다음 내용 추가**
   ```powershell
   # UTF-8 인코딩 설정
   [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
   $OutputEncoding = [System.Text.Encoding]::UTF8

   # chcp 65001 실행
   chcp 65001 | Out-Null
   ```

3. **저장 후 PowerShell 재시작**

### 방법 2: 실행 시마다 설정

```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
chcp 65001
```

---

## VSCode 터미널 설정

### 통합 터미널 인코딩 설정

1. **설정 열기** (`Ctrl + ,`)

2. **settings.json 편집**
   ```json
   {
     "terminal.integrated.defaultProfile.windows": "Command Prompt",
     "terminal.integrated.profiles.windows": {
       "Command Prompt": {
         "path": "C:\\Windows\\System32\\cmd.exe",
         "args": ["/K", "chcp 65001 >nul"]
       },
       "PowerShell": {
         "source": "PowerShell",
         "args": ["-NoExit", "-Command", "chcp 65001"]
       }
     },
     "files.encoding": "utf8",
     "files.autoGuessEncoding": true
   }
   ```

3. **VSCode 재시작**

### Git Bash 사용 시

```json
{
  "terminal.integrated.defaultProfile.windows": "Git Bash",
  "terminal.integrated.env.windows": {
    "LANG": "ko_KR.UTF-8"
  }
}
```

---

## 프로젝트별 자동 설정

### .vscode/settings.json 생성

프로젝트 루트에 `.vscode/settings.json` 파일 생성:

```json
{
  "terminal.integrated.defaultProfile.windows": "Command Prompt",
  "terminal.integrated.profiles.windows": {
    "Command Prompt": {
      "path": "C:\\Windows\\System32\\cmd.exe",
      "args": ["/K", "chcp 65001 >nul && echo 한글 인코딩 설정 완료"]
    }
  },
  "files.encoding": "utf8",
  "python.terminal.executeInFileDir": true,
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter"
  }
}
```

---

## 배치 스크립트 템플릿

새로운 `.bat` 파일 생성 시 다음 템플릿 사용:

```batch
@echo off
chcp 65001 >nul
REM UTF-8 인코딩 설정

echo 한글이 정상적으로 출력됩니다.
echo ====================================

REM 여기에 스크립트 내용 작성

pause
```

---

## 문제 해결

### 여전히 한글이 깨질 때

#### 1. 폰트 확인
- Windows Terminal: Cascadia Code, D2Coding, 나눔고딕코딩 등 한글 지원 폰트 사용
- CMD: 래스터 글꼴 대신 TrueType 글꼴 사용

#### 2. 파일 인코딩 확인
```cmd
# 파일 인코딩 확인
file your_script.py
```

VSCode에서:
- 우측 하단에 인코딩 표시 확인
- 클릭하여 "UTF-8로 다시 열기" 또는 "UTF-8로 저장" 선택

#### 3. Python 환경 확인
```python
import sys
print(sys.stdout.encoding)  # UTF-8이어야 함
print(sys.getdefaultencoding())  # UTF-8이어야 함
```

#### 4. Windows 지역 설정 확인
- 설정 → 시간 및 언어 → 언어 → 관리 언어 설정
- "유니코드를 지원하지 않는 프로그램의 언어" → 한국어 확인
- "베타: 전 세계 언어 지원을 위해 Unicode UTF-8 사용" 체크

---

## 테스트

### 한글 출력 테스트 스크립트

**test_encoding.bat:**
```batch
@echo off
chcp 65001 >nul
echo 한글 테스트: 가나다라마바사아자차카타파하
echo English Test: ABCDEFGHIJKLMNOPQRSTUVWXYZ
echo 숫자 테스트: 1234567890
echo 특수문자 테스트: !@#$%^&*()_+-=
pause
```

**test_encoding.py:**
```python
# -*- coding: utf-8 -*-
import sys

print(f"시스템 인코딩: {sys.stdout.encoding}")
print(f"기본 인코딩: {sys.getdefaultencoding()}")
print("-" * 50)
print("한글 테스트: 가나다라마바사아자차카타파하")
print("English Test: ABCDEFGHIJKLMNOPQRSTUVWXYZ")
print("숫자 테스트: 1234567890")
print("특수문자 테스트: !@#$%^&*()_+-=")
```

실행:
```cmd
scripts\fix_encoding.bat
python test_encoding.py
```

---

## 자주 묻는 질문 (FAQ)

### Q1: chcp 65001 실행 후에도 한글이 깨져요
**A:** 폰트가 한글을 지원하지 않을 수 있습니다. D2Coding이나 나눔고딕코딩 폰트로 변경하세요.

### Q2: Python 스크립트는 정상인데 터미널에서만 깨져요
**A:** 터미널의 출력 인코딩 문제입니다. `chcp 65001`을 실행하세요.

### Q3: 레지스트리 수정이 두려워요
**A:** Windows Terminal 설정이나 배치 스크립트에 `chcp 65001`을 추가하는 방법을 사용하세요.

### Q4: VSCode에서만 한글이 깨져요
**A:** VSCode 설정에서 터미널 인코딩을 UTF-8로 설정하세요.

### Q5: Docker 로그에서 한글이 깨져요
**A:** Docker 컨테이너 내부의 locale 설정을 확인하세요:
```bash
docker exec -it container_name locale
docker exec -it container_name bash -c "export LANG=C.UTF-8"
```

---

## 참고 자료

- [Microsoft Docs - Code Pages](https://docs.microsoft.com/en-us/windows/win32/intl/code-pages)
- [Python 공식 문서 - Unicode HOWTO](https://docs.python.org/3/howto/unicode.html)
- [Windows Terminal 설정 가이드](https://docs.microsoft.com/en-us/windows/terminal/)

---

**프로젝트에서 권장하는 설정:**
1. 모든 `.bat` 파일 시작에 `chcp 65001 >nul` 추가 ✅
2. Python 파일 상단에 `# -*- coding: utf-8 -*-` 추가 ✅
3. VSCode settings.json에 UTF-8 설정 추가 ✅
4. 한글 지원 폰트 사용 (D2Coding, Cascadia Code 등) ✅
