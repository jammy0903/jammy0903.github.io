---
layout: post
title: "input() vs sys.stdin.readin()"
date: 2026-02-17 10:41:06 +0900
categories: blog
original_url: "https://velog.io/@jammy0903/input-vs-sys.stdin.readin"
---

input() vs sys.stdin.readin() input은 내부적으로 처리가 느리다. 

> import sys input = sys.stdin.readline

사용은 위와같이함 input이랑 똑같이 작동하는데 더 빠른것임. 차이점 : 뒤에 줄바꿈 \n 이 포함되는데, 문제가 있다면 문자열 비교할 때 .strip()을 붙여서 해결한다 
