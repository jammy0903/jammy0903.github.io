---
post_number: 9
layout: post
title: "죽고싶다. Alma Linux 깔다가 D드라이브 덮어썼다"
date: 2025-03-07 00:49:20 +0900
categories: blog
original_url: "https://velog.io/@jammy0903/%EC%A3%BD%EA%B3%A0%EC%8B%B6%EB%8B%A4.-Alma-Linux-%EA%B9%94%EB%8B%A4%EA%B0%80-D%EB%93%9C%EB%9D%BC%EC%9D%B4%EB%B8%8C-%EB%8D%AE%EC%96%B4%EC%8D%BC%EB%8B%A4"
tags: ['linux']
---

이 일을 해결해보자 PWSH를 관리자모드로 켜자 그다음에 Get-Volumn 명령어로 파티션 변화나 용량이 바뀌었나 한번 보자🤔 응 그냥 덮어씌운것이다

![](https://velog.velcdn.com/images/jammy0903/post/8702f1f8-d016-4391-82e3-610b32278c9f/image.png)

> 내가 잃어버린 D드라이브를 구체적으로 찾아보자.
>     
>     
>     Get-Childitem D:W

``` 날라간 내 메모리 위에 씌워진 것들을 눈으로 확인했다. ㅂㄷㅂㄷ ![](https://velog.velcdn.com/images/jammy0903/post/b3de2693-53b1-40b4-9748-08a90cb85098/image.png) diskpart

> select disk 1 # D: 드라이브가 있는 디스크 번호 list partition ![](https://velog.velcdn.com/images/jammy0903/post/06ecb32a-07bd-4d3e-a4c9-8a61ece68995/image.png)

## diskpart 에서 사용 가능한 명령어

### 1\. 기본 정보 확인

> list disk # 모든 디스크 목록 select disk 1 # 분석하려는 디스크 선택 detail disk # 선택한 디스크의 자세한 정보 ![](https://velog.velcdn.com/images/jammy0903/post/caba87d4-29d6-410f-b608-0df0864cba6a/image.png)

### 2\. 파티션 분석

> list partition # 모든 파티션 표시 select partition 1 # 특정 파티션 선택 detail partition # 선택된 파티션의 상세 정보

### 3\. 볼륨 정보

> list volume # 모든 볼륨 표시 select volume 2 # 특정 볼륨 선택 detail volume # 선택된 볼륨의 상세 정보

### 4\. 파일시스템 정보

> filesystem # 현재 선택된 볼륨의 파일시스템 정보

### 5\. 삭제된 파티션 관련

> recover # 삭제된 파티션 복구 시도

이것인가? 하고 찾아보았다. 

**recover <명령어의 기능>

  * 선택된 디스크의 잘못된 파티션 테이블을 복구 시도
  * 기본 파티션 구조를 재구성
  * 읽을 수 없는 디스크를 읽을 수 있게 만들려고 시도** `파일 삭제나 포맷으로 인한 데이터 손실에는 효과 없으므로 파티션 테이블이 손상된 경우에만 사용하시오^^`



# 그냥 도구를 사용하는것이 가장 빠르다.

# 첫 시도 TestDisk( with튜토리얼)

TestDisk는 손실된 파티션을 복구하고 손상된 파일시스템을 복구할 수 있는 개꿀 오픈소스"지만 내꺼는 복구 못했다는 사실🫠"입니다. 

## 1\. TestDisk 시작하기

  1. `testdisk_win.exe` 파일을 관리자 권한으로 실행하세요.
  2. 시작 화면에서 로그 파일 생성 여부를 묻습니다. [Create]를 선택하여 로그 파일을 생성하는 것이 좋습니다.



## 2\. 디스크 선택

  1. 컴퓨터에 연결된 모든 디스크 목록이, 표시됩니다.
  2. 방향키(↑↓)를 사용하여 검사하려는 디스크를 선택하세요 (D: 드라이브가 있는 디스크를 선택).
  3. [Proceed] 버튼을 선택하고 Enter를 누릅니다.



## 3\. 파티션 테이블 유형 선택

  1. 디스크의 파티션 테이블 유형을 선택하는 화면이 나타납니다.
  2. 대부분의 윈도우 시스템은 [Intel/PC]를 사용합니다.
  3. [Proceed] 버튼을 선택하고 Enter를 누릅니다.



## 4\. 작업 선택

다음 중 원하는 작업을 선택하세요:

  * **[Analyse]** : 현재 파티션 구조를 분석하고 손실된 파티션을 찾습니다 (일반적으로 이 옵션부터 시작).
  * **[Advanced]** : 파일시스템 속성과 같은 고급 옵션에 접근합니다.
  * **[Geometry]** : 디스크 기하학적 설정을 수정합니다.
  * **[Options]** : 특정 작업 옵션을 설정합니다.
  * **[MBR Code]** : 마스터 부트 레코드를 수정합니다.



## 5\. 파티션 분석 및 복구

**[Analyse] 선택 후:**

  1. TestDisk가 현재 파티션 테이블을 스캔하고 결과를 표시합니다.
  2. 기존 파티션이 녹색으로 표시되고, 잠재적 손실 파티션은 다른 색상으로 표시됩니다.
  3. [Quick Search] 버튼을 선택하여 빠른 검색을 시작하세요.
  4. 검색이 완료되면 발견된 모든 파티션이 표시됩니다.
  5. 복구하려는 파티션을 선택하고 'p' 키를 눌러 해당 파티션의 파일을 미리 볼 수 있습니다.
  6. 올바른 파티션을 찾았다면, 해당 파티션을 선택하고 Enter를 누릅니다.
  7. [Write] 옵션을 선택하여 파티션 테이블을 저장합니다.
  8. TestDisk가 변경 사항을 저장할지 묻습니다. [Y]를 선택하여 확인합니다.



## 6\. 심층 검색 (필요한 경우)

Quick Search로 파티션을 찾지 못했다면:

  1. [Deeper Search] 옵션을 선택합니다.
  2. 이 과정은 Quick Search보다 더 오래 걸리지만 더 철저히 스캔합니다.
  3. 검색이 완료되면 위의 5번 단계와 같이 파티션 복구 과정을 진행합니다.



## 주요 단축키

  * 방향키: 메뉴 탐색
  * Enter: 선택 확인
  * q: 이전 메뉴로 돌아가기
  * p: 파일 미리보기
  * h: 도움말 표시



## 주의사항

  * TestDisk 사용 시 파일을 덮어쓰지 않도록 주의하세요.
  * 가능하면 원본 디스크에 직접 쓰기 작업을 하지 마세요.
  * 중요한 데이터가 있는 경우, 가능하면 디스크 이미지를 만들어 작업하는 것이 안전합니다.



* * *

# 두번째 시도 Wise Data Recovery (성공 했지만 양심은 버렸던)

[https://apps.microsoft.com/detail/xp9jzfjls46dh7?hl=ko-KR&gl=KR](<https://apps.microsoft.com/detail/xp9jzfjls46dh7?hl=ko-KR&gl=KR>) 좋아요 다운을 받읍시다. 가서 GUI 완져니 쉽게나와있으니까 가서 내 **D드라이브 내.놔.** 하시면 바로 이렇게나옵니다.

![](https://velog.velcdn.com/images/jammy0903/post/5d401f89-0fb9-404c-b31c-422bc058e09a/image.png)

하나씩 복구되는거 확인해보면 감동의 파도🌊
