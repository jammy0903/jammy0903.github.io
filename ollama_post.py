#!/usr/bin/env python3
"""
Ollama + Jekyll 블로그 자동 글 생성 스크립트

사용법:
  python3 ollama_post.py "리눅스 파일 퍼미션 정리"
  python3 ollama_post.py "Docker 네트워크 이해하기" --auto-commit
  python3 ollama_post.py "Python 데코레이터" --model qwen2.5:1.5b
"""

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.request
from datetime import datetime

OLLAMA_API = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "qwen2.5:1.5b"
POSTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_posts")


def call_ollama(prompt, model):
    """Ollama API를 호출하고 스트리밍 응답을 합쳐서 반환한다."""
    payload = json.dumps({
        "model": model,
        "prompt": prompt,
        "stream": True,
    }).encode("utf-8")

    req = urllib.request.Request(
        OLLAMA_API,
        data=payload,
        headers={"Content-Type": "application/json"},
    )

    result_parts = []
    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            for line in resp:
                line = line.decode("utf-8").strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                    token = obj.get("response", "")
                    result_parts.append(token)
                    print(token, end="", flush=True)
                    if obj.get("done"):
                        break
                except json.JSONDecodeError:
                    continue
    except urllib.error.URLError as e:
        print(f"\n[오류] Ollama 서버에 연결할 수 없습니다: {e}", file=sys.stderr)
        print("ollama serve 가 실행 중인지 확인하세요.", file=sys.stderr)
        sys.exit(1)

    print()  # 줄바꿈
    return "".join(result_parts).strip()


def generate_post_content(topic, model):
    """주제를 받아 블로그 본문을 생성한다."""
    prompt = f"""당신은 기술 블로그 작성자입니다. 아래 주제에 대해 한국어로 블로그 글을 작성하세요.

주제: {topic}

작성 규칙:
- 한국어로 작성하되, 말투는 "음슴체"를 사용 (예: ~임, ~함, ~됨, ~있음, ~인 듯)
- 마크다운 문법을 적극적으로 활용:
  - ## / ### 헤더로 섹션 구분
  - `---` 수평선으로 섹션 사이를 시각적으로 구분
  - **굵게**, *기울임*, `인라인 코드` 적극 활용
  - > 인용 블록(콜아웃)으로 핵심 포인트나 주의사항 강조
  - 표(| 헤더 | 헤더 |)가 유용한 경우 표로 정리
  - 순서 있는 목록(1. 2. 3.)과 순서 없는 목록(- ) 혼합 사용
  - 코드 예시가 필요하면 코드블럭(```)에 언어 지정 포함
- 핵심 개념을 일상생활에 비유해서 쉽게 설명
- 제목(# 또는 title)은 포함하지 말 것 (frontmatter에서 처리)
- 글 분량은 적당히 (너무 짧지도, 너무 길지도 않게)

바로 본문 내용만 작성하세요:"""

    print(f"\n[글 생성 중] 모델: {model}")
    print("-" * 50)
    content = call_ollama(prompt, model)
    print("-" * 50)
    return content


def generate_tags(topic, content, model):
    """글 내용을 기반으로 태그를 자동 추출한다."""
    prompt = f"""아래 블로그 글의 주제와 내용을 보고 적절한 태그를 1~5개 추출하세요.

주제: {topic}
내용 일부: {content[:500]}

규칙:
- 태그는 영어 소문자, 하이픈(-) 사용
- 쉼표(,)로 구분
- 태그만 출력 (설명 없이)

예시 출력: linux, file-permission, security

태그:"""

    print("\n[태그 생성 중]")
    raw = call_ollama(prompt, model)
    # 태그 파싱: 쉼표로 분리, 정리
    tags = []
    for t in raw.replace("\n", ",").split(","):
        t = t.strip().strip("'\"").strip()
        t = re.sub(r"[^a-zA-Z0-9가-힣\-]", "", t)
        if t:
            tags.append(t)
    tags = tags[:5]  # 최대 5개
    if not tags:
        tags = ["blog"]
    print(f"  태그: {tags}")
    return tags


def generate_title(topic, model):
    """주제를 기반으로 블로그 제목을 생성한다."""
    prompt = f"""아래 주제로 한국어 블로그 글 제목을 하나만 만들어 주세요.

주제: {topic}

규칙:
- 한국어로 작성
- 간결하고 흥미를 끄는 제목
- 따옴표 없이 제목만 출력

제목:"""

    print("\n[제목 생성 중]")
    title = call_ollama(prompt, model)
    # 제목 정리: 앞뒤 공백, 따옴표 제거
    title = title.strip().strip('"').strip("'").strip()
    # 여러 줄이면 첫 줄만
    title = title.split("\n")[0].strip()
    if not title:
        title = topic
    print(f"  제목: {title}")
    return title


def get_next_post_number():
    """_posts/ 디렉토리에서 가장 큰 post_number를 찾아 다음 번호를 반환한다."""
    max_num = 0
    if not os.path.isdir(POSTS_DIR):
        os.makedirs(POSTS_DIR, exist_ok=True)
        return 1

    for fname in os.listdir(POSTS_DIR):
        if not fname.endswith(".md"):
            continue
        fpath = os.path.join(POSTS_DIR, fname)
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("post_number:"):
                        num = re.sub(r"[^0-9]", "", line)
                        if num:
                            max_num = max(max_num, int(num))
                        break
                    if line == "---" and max_num == 0:
                        continue
                    # frontmatter 영역을 벗어나면 중단
                    if not line.startswith("---") and ":" not in line:
                        break
        except (OSError, UnicodeDecodeError):
            continue

    return max_num + 1


def make_slug(title):
    """제목을 파일명용 슬러그로 변환한다 (new_post.sh와 동일한 방식)."""
    # 영문, 숫자, 한글, 공백, 하이픈만 남김
    slug = re.sub(r"[^a-zA-Z0-9가-힣 \-]", "", title)
    slug = slug.replace(" ", "-")
    slug = slug[:80]
    return slug


def save_post(title, content, tags, post_number):
    """포스트를 _posts/ 디렉토리에 저장한다."""
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    datetime_str = now.strftime("%Y-%m-%d %H:%M:%S")

    slug = make_slug(title)
    filename = f"{date_str}-{slug}.md"
    filepath = os.path.join(POSTS_DIR, filename)

    tag_list = "[" + ", ".join(f"'{t}'" for t in tags) + "]"

    frontmatter = f"""---
post_number: {post_number}
layout: post
title: "{title}"
date: {datetime_str} +0900
categories: blog
tags: {tag_list}
---"""

    full_content = frontmatter + "\n\n" + content + "\n"

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(full_content)

    return filepath, filename


def auto_commit(filepath, post_number, title):
    """git add + commit 을 자동으로 실행한다."""
    repo_dir = os.path.dirname(os.path.abspath(__file__))
    try:
        subprocess.run(
            ["git", "add", filepath],
            cwd=repo_dir, check=True,
        )
        msg = f"글 #{post_number}: {title}"
        subprocess.run(
            ["git", "commit", "-m", msg],
            cwd=repo_dir, check=True,
        )
        print(f"\n[커밋 완료] {msg}")
    except subprocess.CalledProcessError as e:
        print(f"\n[커밋 실패] {e}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        description="Ollama로 Jekyll 블로그 글 자동 생성"
    )
    parser.add_argument("topic", help="블로그 글 주제")
    parser.add_argument(
        "--model", default=DEFAULT_MODEL,
        help=f"Ollama 모델 (기본값: {DEFAULT_MODEL})"
    )
    parser.add_argument(
        "--auto-commit", action="store_true",
        help="생성 후 자동으로 git commit"
    )
    args = parser.parse_args()

    print(f"=== Ollama 블로그 글 생성기 ===")
    print(f"주제: {args.topic}")
    print(f"모델: {args.model}")

    # 1. 제목 생성
    title = generate_title(args.topic, args.model)

    # 2. 본문 생성
    content = generate_post_content(args.topic, args.model)

    # 3. 태그 생성
    tags = generate_tags(args.topic, content, args.model)

    # 4. post_number 계산
    post_number = get_next_post_number()
    print(f"\n[글 번호] #{post_number}")

    # 5. 미리보기
    print("\n" + "=" * 50)
    print("[미리보기]")
    print("=" * 50)
    print(f"제목: {title}")
    print(f"태그: {tags}")
    print(f"글 번호: #{post_number}")
    print("-" * 50)
    preview = content[:300]
    if len(content) > 300:
        preview += "\n..."
    print(preview)
    print("=" * 50)

    # 6. 파일 저장
    filepath, filename = save_post(title, content, tags, post_number)
    print(f"\n[저장 완료] {filepath}")

    # 7. 자동 커밋
    if args.auto_commit:
        auto_commit(filepath, post_number, title)
    else:
        print(f"\n배포하려면:")
        print(f'  git add "{filepath}"')
        print(f'  git commit -m "글 #{post_number}: {title}"')
        print(f"  git push")


if __name__ == "__main__":
    main()
