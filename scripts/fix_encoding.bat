@echo off
REM Windows 터미널 한글 깨짐 해결 스크립트

echo ============================================
echo Windows 터미널 인코딩 설정 도구
echo ============================================
echo.

REM 현재 코드 페이지 확인
echo [현재 설정]
chcp
echo.

REM UTF-8로 변경
echo UTF-8(65001)로 변경 중...
chcp 65001
echo.

echo [변경된 설정]
chcp
echo.

echo ============================================
echo 인코딩 설정 완료!
echo ============================================
echo.
echo 이제 한글이 정상적으로 표시됩니다.
echo 이 설정은 현재 터미널 세션에만 적용됩니다.
echo.
echo 영구 적용을 원하시면:
echo 1. 레지스트리 편집기 실행 (regedit)
echo 2. HKEY_LOCAL_MACHINE\Software\Microsoft\Command Processor
echo 3. 새 문자열 값: Autorun
echo 4. 값 데이터: chcp 65001
echo.

pause
