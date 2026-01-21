"""
Tacit 서비스 실행 스크립트

사용법:
    python run.py

또는:
    streamlit run app/main.py
"""

import subprocess
import sys
import os


def main():
    # 현재 디렉토리를 tacit 폴더로 설정
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Streamlit 앱 실행
    subprocess.run([
        sys.executable, "-m", "streamlit", "run",
        "app/main.py",
        "--server.port=8501",
        "--browser.gatherUsageStats=false"
    ])


if __name__ == "__main__":
    main()
