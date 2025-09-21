#!/usr/bin/env python3
"""
텔레그램 메시지 스케줄러
MVVM 아키텍처를 사용한 텔레그램 봇 메시지 스케줄링 애플리케이션
"""

import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from views.telegram_view import TelegramView


def main():
    """메인 함수"""
    try:
        app = TelegramView()
        app.run()
    except Exception as e:
        print(f"애플리케이션 실행 중 오류 발생: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
