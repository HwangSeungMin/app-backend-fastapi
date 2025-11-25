# -*- coding: utf-8 -*-
"""
인코딩 테스트 스크립트
"""
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.encoding_fix import ensure_utf8, print_encoding_info

# UTF-8 인코딩 보장
ensure_utf8()

def test_korean_output():
    """한글 출력 테스트"""

    print("\n" + "=" * 80)
    print("한글 출력 테스트")
    print("=" * 80)

    test_strings = [
        "가나다라마바사아자차카타파하",
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
        "1234567890",
        "!@#$%^&*()_+-=",
        "건강기능식품 RAG 시스템",
        "✅ ✓ ✗ ⚠️ 🔍 💊 ⏰ 📊",
    ]

    for idx, text in enumerate(test_strings, 1):
        print(f"{idx}. {text}")

    print("=" * 80)


def test_file_encoding():
    """파일 인코딩 테스트"""

    print("\n" + "=" * 80)
    print("파일 인코딩 테스트")
    print("=" * 80)

    test_file = "test_encoding_output.txt"

    try:
        # UTF-8로 파일 쓰기
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("한글 테스트: 가나다라마바사아자차카타파하\n")
            f.write("English Test: ABCDEFGHIJKLMNOPQRSTUVWXYZ\n")
            f.write("건강기능식품 RAG 시스템\n")

        print(f"✓ 파일 생성 완료: {test_file}")

        # UTF-8로 파일 읽기
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()

        print("✓ 파일 읽기 완료:")
        print(content)

        # 파일 삭제
        os.remove(test_file)
        print(f"✓ 파일 삭제 완료: {test_file}")

    except Exception as e:
        print(f"✗ 파일 처리 오류: {e}")

    print("=" * 80)


def test_logger_output():
    """Logger 출력 테스트"""

    print("\n" + "=" * 80)
    print("Logger 출력 테스트")
    print("=" * 80)

    try:
        from utils.logger import get_logger

        logger = get_logger(__name__)

        logger.info("한글 INFO 메시지 테스트")
        logger.warning("한글 WARNING 메시지 테스트")
        logger.error("한글 ERROR 메시지 테스트")
        logger.debug("한글 DEBUG 메시지 테스트")

        print("✓ Logger 한글 출력 성공")

    except Exception as e:
        print(f"✗ Logger 테스트 오류: {e}")

    print("=" * 80)


def main():
    """메인 함수"""

    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "인코딩 종합 테스트" + " " * 40 + "║")
    print("╚" + "═" * 78 + "╝")

    # 인코딩 정보 출력
    print_encoding_info()

    # 한글 출력 테스트
    test_korean_output()

    # 파일 인코딩 테스트
    test_file_encoding()

    # Logger 출력 테스트
    test_logger_output()

    print("\n" + "=" * 80)
    print("모든 테스트 완료!")
    print("=" * 80)
    print("\n한글이 정상적으로 표시되면 인코딩 설정이 올바릅니다.")
    print("한글이 깨져 보이면 'scripts\\fix_encoding.bat'를 실행하세요.")
    print("=" * 80 + "\n")


if __name__ == '__main__':
    main()
