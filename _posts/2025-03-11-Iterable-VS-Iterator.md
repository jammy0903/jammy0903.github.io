---
post_number: 16
layout: post
title: "Iterable VS Iterator"
date: 2025-03-11 12:40:34 +0900
categories: blog
original_url: "https://velog.io/@jammy0903/Iterable-VS-Iterator"
tags: ['python']
---

-몰라도 잘 살지만 알면 좋은 정보-

파이썬에는 **iterable 이라는 개념과 Iterator 이라는 개념** 이 있다. 이를 혼동하면 안된다는 큰 깨달음을 (이제야) 얻고 포스팅을 시작한다.

# 개념 설명

정말 간단하다. 

> . 1. 이터러블(Iterable)

  * 모든 데이터를 메모리에 한번에 적재( 메모리 많이 잡아먹음)
    * for문에서 여러 번 순회 가능 (데이터가 메모리에 계속 존재)
    * 인덱싱, 슬라이싱 가능
    * 메모리 사용은 구현에 따라 다름 (리스트는 모든 데이터를 메모리에 저장, 제너레이터는 지연 평가) EX) 리스트, 튜플, 문자열, 딕셔너리, 세트 등



>   2. 이터레이터(Iterator)
> 


  * 데이터를 메모리에 한번에 적재하지 않고, 메모리 주소를 그때 그때 읽어오는 것.
  * 일회용 (한 번 순회하면 재사용 불가) 왜냐면 진짜 가지고있는 데이터가 아니라 일회용으로 만든 객체고, 포인터 느낌으로 한번 지나가는 거기 때문. 그런데 앞으로밖에 못감.
  * Iterable 함
  * next() 함수로 한 번에 하나씩 값을 꺼낼 수 있는 객체 다음 값의 위치 정보나 계산 방법만 저장 한 번 순회하면 소진됨 (메모리 효율적) 인덱싱, 슬라이싱 불가능



### 자료형에 관하여..

이터러블이었던 리스트를 이터레이터로 변환하면 Type이 어떻게 될까? ![](https://velog.velcdn.com/images/jammy0903/post/2a3e6789-c1fd-4ca2-9468-f6607b790893/image.png) 그리고 리스트였던 것을 map함수를씌워서 iterator로 만든 후 Type을 확인 해보면.. ![](https://velog.velcdn.com/images/jammy0903/post/a40639a8-7673-48c9-bb85-206bf2fee506/image.png) `<class 'list_iterator'> <class 'map'>` 이러한 결과를 볼 수 있다. 둘다 그냥 Iterator 이라는 이름의 타입이 아니라 "엥?" 했는데 Duck Typing 이라는 철학때문에 그냥 이름이 저럴 뿐이라네요.

hasattr(obj, '**iter** '): 이터러블 여부 확인내장함수 hasattr(obj, '**next** '): 이터레이터인지 확인, 을 활용하여 확인해보자.

객체 | 이터러블 | 이터레이터 | 설명  
---|---|---|---  
`list` ([1, 2, 3]) | O | X | 리스트는 이터러블이지만 이터레이터는 아님  
`map` (map(int, '123')) | O | O | map 객체는 이터러블이면서 동시에 이터레이터  
  
![실험vscode](https://velog.velcdn.com/images/jammy0903/post/31d9025e-6e16-4e56-9ec6-cb71fd5b1065/image.png)

* * *

정말 Iterator는 일회성일까? 확인하고 이해해보자 ![](https://velog.velcdn.com/images/jammy0903/post/6f8d7c00-29f7-4e93-977c-016ef39aadfb/image.png) 위 코드는 리스트를 만들고, 그걸 Iterator로 바꾼 후 for문을 2번 돌려 출력해본 코드이다. 그런데 첫 for문만 실행되고 두번째 꺼는 실행이 안되는걸 볼 수 있죠

이유는 '이미 iterator생성할 때만든 포인터같은 놈이 끝까지 가서' 그런 겁니다. _근데 우리 그냥 리스트할 때는 저런거 되잖아요..그리고 C언어나 다른 언어에서는 저런거 못봤던거같은데...?_

* * *

네.. C언어, C++, Java에 파이썬 처럼 '일회용'인 'Iterator'는 없다! 다들 C언어는 포인터! C++은 STL에 스마트포인터! 

  * Java : Iterator는 존재하지만, 컬렉션 객체에 연결되어 있어 hasNext()와 next() 메소드를 사용하며, 파이썬과 달리 컬렉션 자체는 여전히 메모리에 남아있어 새로운 Iterator를 언제든 생성할 수 있습니다.


