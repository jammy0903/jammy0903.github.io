#!/bin/bash
# Ollama 블로그 글 자동 생성 래퍼
# 사용법: ./ai_post.sh "주제"
#         ./ai_post.sh "주제" --auto-commit
#         ./ai_post.sh "주제" --model qwen2.5:1.5b --auto-commit

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHON_SCRIPT="${SCRIPT_DIR}/ollama_post.py"

# 사용법 안내
if [ -z "$1" ] || [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
  echo "=== Ollama 블로그 글 자동 생성기 ==="
  echo ""
  echo "사용법:"
  echo "  ./ai_post.sh \"주제\"                        # 글 생성만"
  echo "  ./ai_post.sh \"주제\" --auto-commit           # 글 생성 + 자동 커밋"
  echo "  ./ai_post.sh \"주제\" --model gemma2:2b       # 다른 모델 사용"
  echo ""
  echo "예시:"
  echo "  ./ai_post.sh \"리눅스 파일 퍼미션 정리\""
  echo "  ./ai_post.sh \"Docker 네트워크 이해하기\" --auto-commit"
  echo "  ./ai_post.sh \"Python 데코레이터\" --model qwen2.5:1.5b"
  exit 0
fi

# Python3 확인
if ! command -v python3 &> /dev/null; then
  echo "[오류] python3가 설치되어 있지 않습니다."
  exit 1
fi

# Ollama 실행 여부 확인
if ! curl -s --connect-timeout 3 http://localhost:11434/api/tags > /dev/null 2>&1; then
  echo "[오류] Ollama 서버가 실행 중이지 않습니다."
  echo ""
  echo "아래 명령어로 Ollama를 시작하세요:"
  echo "  ollama serve"
  echo ""
  echo "모델이 없다면 먼저 다운로드하세요:"
  echo "  ollama pull qwen2.5:1.5b"
  exit 1
fi

echo "[확인] Ollama 서버 연결 성공"

# Python 스크립트 실행 (모든 인자 전달)
python3 "$PYTHON_SCRIPT" "$@"
