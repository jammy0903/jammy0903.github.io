---
layout: page
title: "desk — Python으로 만든 9종 데스크톱 미니게임"
subtitle: "짧은 휴식을 위한 오프라인 게임 모음과 GUI·퍼즐 알고리즘 구현 프로젝트"
description: "Python 표준 라이브러리로 구현한 9종 미니게임. 자동 저장, 다국어 전환, 퍼즐 생성과 검증을 지원하며 Windows 실행 파일로 설치 없이 즐길 수 있다."
---

**[⬇ desk.exe 받기 (11MB)]({{ '/assets/files/desk.exe' | relative_url }})** ·
[소스 zip (58KB)]({{ '/assets/files/desk.zip' | relative_url }}) ·
[GitHub Releases](https://github.com/jammy0903/jammy0903.github.io/releases/latest)

exe 는 받아서 더블클릭만 하면 됨. **파이썬 없어도 되고, 설치·회원가입·인터넷 전부 필요 없음.**
작업표시줄 아이콘 오른쪽 클릭 → "작업 표시줄에 고정" 해 두면 클릭 한 번으로 열림.

만든 이야기 →
[한국어 글]({{ '/2026-08-12-python-tkinter-mini-game-launcher/' | relative_url }}) ·
[English]({{ '/2026-08-12-python-tkinter-mini-game-launcher-en/' | relative_url }})

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

## 조작과 창 제어

| 키 | 하는 일 |
|---|---|
| `ESC` | **작업표시줄로 내림.** 프로그램은 안 꺼지고 판·점수 그대로 |
| `F8` | 작업표시줄에서 **다시 꺼냄** |
| `H` | 현재 위치에서 투명도 0 / 원래 표시 상태 전환 |
| `[` `]` | 흐리게 / 진하게 (마우스로 바를 끌어도 됨) |
| `M` | 게임 고르기 |
| `1`~`9` | 게임 바로 가기 |
| `,` `.` | 판 넘기기 (레벨 있는 게임) |
| `L` | 한국어 / English |
| `R` | 이 판 다시 |
| `Ctrl+Q` | 종료 (창 X 버튼도 종료. `ESC`는 안 꺼짐) |

기본 투명도 55%. 20%까지 내리면 뒤 문서가 비쳐 보임.
항상 맨 위에 뜨지 않아서 다른 창이 자연스럽게 위를 덮음.

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

<small>Python · tkinter · 데스크톱 GUI · 게임 개발 · 절차적 생성 · 퍼즐 검증 · 오프라인 게임 · 네모로직 · 소코반</small>
