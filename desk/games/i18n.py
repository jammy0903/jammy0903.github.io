"""한국어 / 영어 전환.

번역표의 열쇠(key)를 한국어 원문 그대로 쓴다. 그래야 코드를 읽을 때
화면에 뭐가 나오는지 바로 보이고, 번역이 빠진 문장은 한국어로 나올 뿐
깨지지 않는다.

  center_text(c, x, y, t("새 판"), 9)
  ... % (t("%d단계"), n)      ← 서식 문자열도 통째로 열쇠로 쓴다
"""

LANG = "ko"

EN = {
    # 셸
    "게임 고르기": "Choose a game",
    "↑ ↓ 로 고르고 Enter · 숫자키로 바로 · M 닫기":
        "Up/Down then Enter · number keys jump · M closes",
    "새 판": "new game",
    "진행 중 %d점": "in progress, %d pts",
    "게임 오버": "game over",
    "M 메뉴": "M menu",
    "ESC 내리기 · %s 꺼내기 · Ctrl+Q 종료":
        "ESC hide · %s bring back · Ctrl+Q quit",
    "%s 로 작업표시줄에서 꺼낸다": "%s brings it back from the taskbar",
    "한국어": "English",
    "투명도": "Opacity",

    # 도움말 한 줄
    "← → 이동 · ↑ 회전 · Z 반시계 · ↓ 내리기 · Space 하드드롭":
        "Left/Right move · Up rotate · Z counter-clockwise · Down · Space drop",
    "← → 위치 · Space 떨어뜨리기": "Left/Right aim · Space drop",
    "← → 이동 · ↑ 회전 · Z 반시계 · ↓ 내리기 · Space 떨구기":
        "Left/Right move · Up rotate · Z counter-clockwise · Down · Space drop",
    "방향키로 밀기 · Backspace 한 수 무르기":
        "Arrows to slide · Backspace undoes one move",
    "Backspace 로 한 수 무르기": "Backspace undoes that move",
    "방향키로 한 칸씩 · 1+2=3 · 3부터는 같은 수끼리":
        "Arrows move one step · 1+2=3 · from 3 on, equal numbers",
    "방향키 커서 · Space 놓기 · S 보관칸 교체":
        "Arrows move · Space place · S swap storage",
    "클릭·드래그로 칠하기 · Tab 칠하기/X 전환 · 다 채운 줄은 X 자동":
        "Click or drag · Tab switches fill/X · finished lines get X automatically",
    "칠하기": "fill",
    "X 표시": "X mark",
    "← → 색 고르기 · Space 칠하기 · , . 단계 넘기기":
        "Left/Right pick colour · Space flood · , . change stage",
    "방향키로 밀기 · U 무르기 · , . 판 넘기기 · Enter 다음 판":
        "Arrows push · U undo · , . change level · Enter next",

    # 게임 안
    "%d연쇄": "%d chain",
    "가장 큰 수 %d": "highest %d",
    "놓을 것": "next",
    "보관 S": "hold S",
    "%d / %d 판   %dx%d  (S 크기)": "%d / %d   %dx%d  (S size)",
    "완성! Enter 로 다음 판": "Solved! Enter for next",
    "%d단계   %d / %d 칸   남은 횟수 %d": "stage %d   %d / %d cells   %d moves left",
    "성공! Enter 로 다음": "Cleared! Enter for next",
    "횟수 초과 — Enter 로 다시": "Out of moves — Enter to retry",
    "%d / %d 판   %d수   상자 %d": "%d / %d   %d moves   %d boxes",
    "성공! Enter 로 다음 판": "Cleared! Enter for next",

    # Triple Town 물건 이름 (화면에는 첫 글자만 나온다)
    "풀": "Grass", "덤불": "Bush", "나무": "Tree", "오두막": "Hut",
    "집": "House", "저택": "Mansion", "성": "Castle", "공중성": "Floating castle",
    "곰": "Bear", "묘비": "Tombstone", "교회": "Church", "대성당": "Cathedral",

    # 전역 단축키 안내
    "전역 단축키는 윈도우에서만 동작 (작업표시줄 클릭으로 복귀)":
        "Global hotkeys are Windows-only (click the taskbar icon instead)",
    "%s 는 다른 프로그램이 이미 쓰고 있음": "%s is already taken by another app",
    "%s 는 사용 중이라 %s 로 잡았다": "%s was taken, using %s instead",
    "쓸 수 있는 전역 단축키가 없음 (작업표시줄 클릭으로 복귀)":
        "No global hotkey available (click the taskbar icon instead)",
    "'%s' 는 알 수 없는 키 조합": "'%s' is not a key combination I know",
}


def t(s):
    """화면에 나갈 문장 하나. 번역이 없으면 원문 그대로."""
    return s if LANG == "ko" else EN.get(s, s)


def set_lang(lang):
    global LANG
    LANG = "en" if lang == "en" else "ko"
    return LANG


def toggle():
    return set_lang("en" if LANG == "ko" else "ko")
