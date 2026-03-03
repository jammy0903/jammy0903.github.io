#!/bin/bash
# 사용법: ./new_post.sh "제목" "태그1,태그2" "본문 마크다운 내용"
# 예시:  ./new_post.sh "Python 데코레이터 정리" "python" "## 데코레이터란?..."
# 예시:  ./new_post.sh "Docker 입문" "docker,devops" "$(cat my_draft.md)"

TITLE="$1"
TAGS="$2"
BODY="$3"

if [ -z "$TITLE" ]; then
  echo "사용법: ./new_post.sh \"제목\" \"태그1,태그2\" \"본문 내용\""
  exit 1
fi

cd "$(dirname "$0")"

# 다음 글 번호 계산
LAST_NUM=$(grep -rh 'post_number:' _posts/ 2>/dev/null | sed 's/[^0-9]//g' | sort -n | tail -1)
NEXT_NUM=$((LAST_NUM + 1))

# 날짜
DATE=$(date +"%Y-%m-%d")
DATETIME=$(date +"%Y-%m-%d %H:%M:%S")

# 파일명용 슬러그
SLUG=$(echo "$TITLE" | sed 's/[^a-zA-Z0-9가-힣 -]//g' | sed 's/ /-/g' | cut -c1-80)
FILENAME="_posts/${DATE}-${SLUG}.md"

# 태그 포맷
TAG_LIST="[$(echo "$TAGS" | sed 's/,/, /g')]"

# 파일 생성
cat > "$FILENAME" << EOF
---
post_number: ${NEXT_NUM}
layout: post
title: "${TITLE}"
date: ${DATETIME} +0900
categories: blog
original_url: ""
tags: ${TAG_LIST}
---

${BODY}
EOF

echo "✅ 글 #${NEXT_NUM} 생성: ${FILENAME}"
echo ""
echo "배포하려면:"
echo "  cd $(pwd)"
echo "  git add -A && git commit -m \"글 #${NEXT_NUM}: ${TITLE}\" && git push"
