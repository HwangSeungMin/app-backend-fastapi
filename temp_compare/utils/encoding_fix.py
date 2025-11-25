# -*- coding: utf-8 -*-
"""
Windows 환경에서 한글 출력 인코딩 문제를 해결하는 유틸리티
"""
import sys
import io
import os
import platform


def fix_windows_encoding():
    """Windows 환경에서 stdout/stderr 인코딩을 UTF-8로 설정"""

    if platform.system() != 'Windows':
        return

    # Python 3.7 이상에서 reconfigure 지원
    if hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8')
            sys.stderr.reconfigure(encoding='utf-8')
            return
        except Exception:
            pass

    # 이전 버전 Python을 위한 fallback
    try:
        sys.stdout = io.TextIOWrapper(
            sys.stdout.buffer,
            encoding='utf-8',
            errors='replace',
            line_buffering=True
        )
        sys.stderr = io.TextIOWrapper(
            sys.stderr.buffer,
            encoding='utf-8',
            errors='replace',
            line_buffering=True
        )
    except Exception as e:
        print(f"Warning: Could not set UTF-8 encoding: {e}")


def set_console_utf8():
    """Windows 콘솔 코드 페이지를 UTF-8로 설정"""

    if platform.system() != 'Windows':
        return

    try:
        # chcp 65001 실행
        os.system('chcp 65001 >nul 2>&1')
    except Exception:
        pass


def ensure_utf8():
    """UTF-8 인코딩 환경 보장"""

    # 환경 변수 설정
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['PYTHONUTF8'] = '1'

    # Windows 콘솔 설정
    set_console_utf8()

    # stdout/stderr 인코딩 설정
    fix_windows_encoding()


def print_encoding_info():
    """현재 인코딩 설정 정보 출력"""

    print("=" * 60)
    print("인코딩 설정 정보")
    print("=" * 60)
    print(f"플랫폼: {platform.system()}")
    print(f"Python 버전: {sys.version}")
    print(f"기본 인코딩: {sys.getdefaultencoding()}")
    print(f"파일시스템 인코딩: {sys.getfilesystemencoding()}")
    print(f"stdout 인코딩: {sys.stdout.encoding}")
    print(f"stderr 인코딩: {sys.stderr.encoding}")
    print(f"PYTHONIOENCODING: {os.environ.get('PYTHONIOENCODING', 'not set')}")
    print(f"PYTHONUTF8: {os.environ.get('PYTHONUTF8', 'not set')}")
    print("=" * 60)
    print("\n한글 테스트: 가나다라마바사아자차카타파하")
    print("English Test: ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    print("=" * 60)


# 자동 실행
if __name__ == '__main__':
    ensure_utf8()
    print_encoding_info()
