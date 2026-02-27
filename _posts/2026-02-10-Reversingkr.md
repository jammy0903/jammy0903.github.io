---
post_number: 17
layout: post
title: "Reversing.kr #"
date: 2026-02-10 08:49:11 +0900
categories: blog
original_url: "https://velog.io/@jammy0903/Reversing.kr"
tags: ['reversing', 'security']
---

  1. 이 함수가 수상했다. 계속 나오고, 뒤에 숫자가 일정하게 늘어나는걸 보니 시간 검사하는 함수가 아닐까?![](https://velog.velcdn.com/images/jammy0903/post/8cb6fd20-5989-46d2-84f8-158eb4886231/image.png) 각 명령어들을 파헤쳐보자. 각 주소값들의 차이를 16진수로 계산해보자. `call msvbvm60.7299CDIE` `je msvbvm60.7299CE6E` `jmp msvbvm60.7299CDE4` `jne msvbvm60.7299CE9A` 7299CD1E + **198** = 7299CDE4 +**138** = 7299CE6E + **44** = 7299CE9A 



전혀 .. 모르겠는 노 등차 수열이다.

  2. 두번째 더 그럴싸한 명령줄들을 발견했다. ![](https://velog.velcdn.com/images/jammy0903/post/a922d75e-1265-4b04-acbc-2c6e915d6344/image.png)

  3. 함수 추적 ![](https://velog.velcdn.com/images/jammy0903/post/b6a1c50e-8449-42ce-8c69-38a12496b8fe/image.png)
         
         push dword ptr ds:[72A4EF9C] ; 72A4EF9C 주소의 값을 스택에 push
         call dword ptr ds:[<TlsGetValue>]  ; TlsGetValue 함수 호출. 결과값은 eax에 저장
         test byte ptr ds:[eax+76], 2 ; eax+76 위치의 1바이트와 2(0010b)를 AND 연산
         ; AND 결과가 0이면 ZF=1, 아니면 ZF=0
         je msvbvm60.72A1A290 ; ZF=1이면(AND 결과가 0이면) 72A1A290로 점프
         




push 9C68 call msvbvm60.72A0E22C mov eax, dword ptr ss:[esp+4] test eax, eax jge msvbvm60.72A1A2B6 cmp eax, 800A9C68 jne msvbvm60.72A1A2A4 mov eax, 800A01B8 push dword ptr ss:[esp+10] push dword ptr ss:[esp+10] push dword ptr ss:[esp+10] push eax call msvbvm60.72A192E7 ret 10

```
