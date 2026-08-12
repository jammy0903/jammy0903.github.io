---
layout: page
title: "desk — 회사에서 몰래 하는 월루게임 9개"
subtitle: "반투명 창 하나에 테트리스·수박게임·뿌요뿌요·2048·네모로직·소코반. ESC 한 번이면 작업표시줄로"
description: "회사에서 몰래, 눈치 안 보고 할 수 있는 월루게임 모음. 반투명 창에 9개가 들어있고 ESC 한 번이면 숨겨짐. 설치 없이 무료 다운로드. 파이썬 기본 라이브러리만 사용."
---

**[⬇ 다운로드 (zip, 49KB)]({{ '/assets/files/desk.zip' | relative_url }})**

압축 풀고 `desk.bat` 더블클릭. 파이썬만 있으면 됨. 설치·회원가입·인터넷 전부 필요 없음.

만든 이야기 →
[한국어 글]({{ '/2026-08-12-회사에서-몰래-게임하려고-반투명-게임-9개를-만들었다/' | relative_url }}) ·
[English]({{ '/2026-08-12-I-Built-a-Translucent-Game-Launcher-to-Play-at-Work-Without-Getting-Caught/' | relative_url }})

---

## 게임 9개

| # | 게임 | 판 수 |
|---|---|---|
| 1 | 테트리스 | 끝없음 |
| 2 | 수박게임 (Suika) | 끝없음 |
| 3 | 뿌요뿌요 | 끝없음 |
| 4 | 2048 | 끝없음 |
| 5 | Threes! | 끝없음 |
| 6 | Triple Town | 끝없음 |
| 7 | 네모로직 (노노그램) | **1,500판** (10·15·20 크기별 500판) |
| 8 | Flood It | **60단계** |
| 9 | 소코반 (창고지기) | **200판** |

## 숨기는 방법

| 키 | 하는 일 |
|---|---|
| `ESC` | **작업표시줄로 내림.** 프로그램은 안 꺼지고 판·점수 그대로 |
| `F8` | 작업표시줄에서 **다시 꺼냄** |
| `H` | 창은 그 자리에 두고 **투명도만 0.** 제일 빠름 |
| `[` `]` | 흐리게 / 진하게 (마우스로 바를 끌어도 됨) |
| `M` | 게임 고르기 |
| `1`~`9` | 게임 바로 가기 |
| `,` `.` | 판 넘기기 (레벨 있는 게임) |
| `L` | 한국어 / English |
| `R` | 이 판 다시 |
| `Ctrl+Q` | 종료 (창 X 버튼도 종료. `ESC`는 안 꺼짐) |

기본 투명도 55%. 20%까지 내리면 뒤 문서가 비쳐 보임.
항상 맨 위에 뜨지 않아서 다른 창이 자연스럽게 위를 덮음.

**못 하는 것** — 원격 모니터링 프로그램이나 화면 캡처는 못 피함. 작업 관리자에는
`pythonw.exe`로 그대로 보임. 옆자리 시선 정도를 피하는 용도지 보안 정책을 뚫는 물건이 아님.

## 소스

외부 라이브러리 0개, 약 2,800줄. 전부 파이썬 표준 라이브러리(tkinter).

| 파일 | 내용 |
|---|---|
| [desk.py]({{ '/desk/desk.py' | relative_url }}) | 창, 메뉴, 저장, 키 입력 |
| [hotkey.py]({{ '/desk/hotkey.py' | relative_url }}) | 전역 단축키 (윈도우, ctypes) |
| [games/base.py]({{ '/desk/games/base.py' | relative_url }}) | 공통 인터페이스·팔레트 |
| [games/i18n.py]({{ '/desk/games/i18n.py' | relative_url }}) | 한국어 / English |
| [games/tetris.py]({{ '/desk/games/tetris.py' | relative_url }}) | 테트리스 |
| [games/suika.py]({{ '/desk/games/suika.py' | relative_url }}) | 수박게임 (Verlet 물리) |
| [games/puyo.py]({{ '/desk/games/puyo.py' | relative_url }}) | 뿌요뿌요 |
| [games/g2048.py]({{ '/desk/games/g2048.py' | relative_url }}) | 2048 |
| [games/threes.py]({{ '/desk/games/threes.py' | relative_url }}) | Threes! |
| [games/tripletown.py]({{ '/desk/games/tripletown.py' | relative_url }}) | Triple Town |
| [games/nonogram.py]({{ '/desk/games/nonogram.py' | relative_url }}) | 네모로직 + 줄 논리 풀이기 |
| [games/floodit.py]({{ '/desk/games/floodit.py' | relative_url }}) | Flood It |
| [games/sokoban.py]({{ '/desk/games/sokoban.py' | relative_url }}) | 소코반 + 역방향 생성기 |
| [smoke_test.py]({{ '/desk/smoke_test.py' | relative_url }}) | 테스트 |
| [README.md]({{ '/desk/README.md' | relative_url }}) · [README.en.md]({{ '/desk/README.en.md' | relative_url }}) | 문서 |

---

<small>월루게임 · 회사에서 몰래 하는 게임 · 사무실 게임 · 눈치 안 보고 하는 게임 ·
공부하다가 딴짓 · 설치 없는 무료 게임 · 오프라인 게임 · 테트리스 · 수박게임 · 뿌요뿌요 ·
2048 · 네모로직 · 노노그램 · 소코반 · 파이썬 tkinter</small>
