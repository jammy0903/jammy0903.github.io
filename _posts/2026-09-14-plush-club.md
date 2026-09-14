---
layout: post
title: "무제한으로 즐기는 실제같은 인형뽑기게임"
subtitle: "인형을 모으고, 탐험을 보내고, 나만의 책상까지 꾸미는 PLUSH CLUB"
date: 2026-09-14 15:00:00 +0900
categories: blog
description: "무료로 무제한 도전하는 3D 인형뽑기 게임 PLUSH CLUB. 인형 탐험과 책상 꾸미기, PNG 저장까지 브라우저에서 즐길 수 있다."
thumbnail-img: /assets/img/plush-club/claw.png
share-img: /assets/img/plush-club/claw.png
tags: [개인프로젝트, 게임개발, 인형뽑기, PLUSH CLUB]
---

인형뽑기를 돈 걱정 없이 계속 할 수 있으면 어떨까 싶어서 직접 만들었다.

이름은 **PLUSH CLUB — 두근두근 인형 탐험대**. 브라우저에서 바로 플레이하는 무료 인형뽑기 게임이다. 횟수 제한 없이 도전할 수 있고, 따로 설치할 필요도 없다.

**[→ 두근두근 인형 탐험대 플레이하기](https://plush-club.fly.dev/?lang=ko)**

## 어떤 게임인지 영상부터

<div style="position:relative;width:100%;padding-top:56.25%;margin:1.5rem 0;">
  <iframe src="https://www.youtube-nocookie.com/embed/9ZkPQ4TshBc" title="PLUSH CLUB 인형뽑기와 책상 꾸미기 소개 영상" style="position:absolute;inset:0;width:100%;height:100%;border:0;" loading="lazy" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>
</div>

[유튜브에서 영상 보기](https://youtu.be/9ZkPQ4TshBc)

실제 플레이 장면을 배속해서 담은 영상이다. 배경 음악도 함께 넣었다.

## 일단 마음껏 뽑으면 된다

![PLUSH CLUB의 3D 인형뽑기 화면]({{ '/assets/img/plush-club/claw.png' | relative_url }})

3D 공간에서 집게를 움직여 인형을 잡는 방식이다. 물리 연산을 적용해서 인형이 집게에 걸리고, 흔들리고, 떨어지는 움직임을 구현했다.

실패해도 다시 하면 된다. 한 판 할 때마다 돈을 넣을 필요 없이, 원하는 인형을 얻을 때까지 계속 도전할 수 있다.

참고로 뽑은 인형은 **게임 안에서 모으는 가상 수집품**이다. 실제 인형을 배송해 주는 서비스는 아니다.

## 뽑은 인형들이 탐험도 다녀온다

인형을 모으는 데서 끝내기는 아쉬워서 탐험 기능을 넣었다. 모은 인형들을 탐험에 보내면 책상을 꾸밀 작은 물건들을 가져온다.

스탠드, 화분, 책, 텀블러, 연필, 컴퓨터, 선반, 과자통, 의자 같은 소품들이다. 소품 그림은 따뜻한 색감의 아기자기한 일러스트 느낌으로 다듬었다.

## 가져온 소품으로 내 책상 꾸미기

![소품으로 꾸민 나만의 책상]({{ '/assets/img/plush-club/desk.png' | relative_url }})

탐험에서 얻은 소품들을 배치해서 나만의 책상을 만들 수 있다. 조명과 화분을 놓고, 책이나 작은 물건들을 더하면서 원하는 분위기로 꾸미면 된다.

완성한 책상은 **전체화면으로 크게 보기**도 되고, **PNG 이미지로 저장**할 수도 있다. 마음에 드는 배치를 만들면 사진처럼 남겨두면 된다.

다른 플레이어들과 이야기할 수 있는 공용 채팅도 있다. 채팅은 서버 DB에 최근 50개까지 보관하도록 만들었다.

## 한국어·영어·일본어·중국어 지원

여러 나라에서도 플레이할 수 있도록 네 가지 언어를 지원한다.

- [한국어로 플레이](https://plush-club.fly.dev/?lang=ko)
- [Play in English](https://plush-club.fly.dev/?lang=en)
- [日本語で遊ぶ](https://plush-club.fly.dev/?lang=ja)
- [用中文游玩](https://plush-club.fly.dev/?lang=zh-CN)

제작 과정에서는 AI 도구의 도움을 받았다. 코딩 보조와 일부 소품 일러스트 제작에 생성형 AI를 활용했고, 직접 플레이해 보면서 조작과 화면 구성을 다듬었다.

잠깐 쉬면서 인형 몇 개 뽑거나 책상 꾸미고 싶을 때 가볍게 해보면 좋겠다. 집게 조작이 불편한 부분이나 추가됐으면 하는 소품이 있다면 댓글로 알려주세요!

**[→ 무료로 플레이하기](https://plush-club.fly.dev/?lang=ko)**
