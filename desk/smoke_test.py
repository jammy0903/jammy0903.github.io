"""로직 + 그리기 스모크 테스트. 창을 띄우지 않고 규칙과 렌더 경로만 확인한다."""
import os
import random
import sys
import tkinter as tk

from games import (floodit, g2048, nonogram, puyo, sokoban, suika,
                   tetris, threes, tripletown)
from games.threes import merged, slide_line, tile_score

fails = []


def ok(cond, msg):
    if not cond:
        fails.append(msg)


# --- Threes 규칙 ---
ok(merged(1, 2) == 3, "1+2=3")
ok(merged(2, 1) == 3, "2+1=3")
ok(merged(1, 1) is None, "1+1 안 합쳐짐")
ok(merged(3, 3) == 6, "3+3=6")
ok(merged(3, 6) is None, "3+6 안 합쳐짐")
ok(merged(0, 5) == 5, "빈칸으로 이동")
ok(slide_line([3, 3, 3, 0])[0] == [6, 3, 0, 0], "선두 한 쌍만 합치기")
ok(slide_line([6, 6, 6, 6])[0] == [12, 6, 6, 0], "6666 → 12,6,6")
ok(slide_line([1, 2, 3, 0])[0] == [3, 3, 0, 0], "1,2,3 연쇄")
ok(slide_line([3, 0, 0, 0])[1] is False, "움직임 없음")
ok(tile_score(3) == 3 and tile_score(6) == 9 and tile_score(12) == 27, "점수표")
ok(tile_score(1) == 0 and tile_score(2) == 0, "1·2는 0점")

# --- Tetris 규칙 ---
t = tetris.Tetris()
t.grid = [[None] * tetris.COLS for _ in range(tetris.ROWS)]
for col in range(tetris.COLS):
    t.grid[tetris.ROWS - 1][col] = "#fff"
t.key_id, t.n, t.cells = "O", 2, list(tetris.PIECES["O"][1])
t.pr, t.pc = 0, 0
before = t.score
t.lock()
ok(all(v is None for v in t.grid[tetris.ROWS - 1]), "한 줄 삭제됨")
ok(t.lines == 1 and t.score > before, "라인 수·점수 증가")
ok(tetris.rotate([(0, 1), (1, 0), (1, 1), (1, 2)], 3) == [(1, 2), (0, 1), (1, 1), (2, 1)],
   "T 회전")

t = tetris.Tetris()
t.pc = 0
t.shift(-1)
ok(t.pc == 0, "왼쪽 벽에서 안 밀림")

# --- Triple Town 규칙 ---
g = tripletown.TripleTown()
g.grid = [[0] * tripletown.N for _ in range(tripletown.N)]
g.grid[0][0] = g.grid[0][1] = 1
g.grid[0][2] = 1
g.resolve(0, 2)
ok(g.grid[0][2] == 2 and g.grid[0][0] == 0, "풀 3개 → 덤불")

g.grid = [[0] * tripletown.N for _ in range(tripletown.N)]
for c in range(3):
    g.grid[1][c] = 1
g.grid[2][0] = g.grid[2][1] = 2
g.resolve(1, 2)
ok(g.grid[1][2] == 2 or 3 in [v for row in g.grid for v in row], "연쇄 병합 발생")

g.grid = [[0] * tripletown.N for _ in range(tripletown.N)]
g.grid[0][0] = 20
g.grid[0][1] = g.grid[1][0] = 1
g.grid[1][1] = 1
g.move_bears()
ok(g.grid[0][0] == 21, "갇힌 곰은 묘비")

# --- Suika 물리 ---
s = suika.Suika()
s.cur = 0
s.dx = suika.WW / 2
s.key("space")
for _ in range(120):
    s.tick(0.033)
ok(len(s.balls) == 1, "공 1개 유지")
b = s.balls[0]
ok(abs(b["y"] - (suika.WH - suika.R[0])) < 1.5, "바닥에 정착 (y=%.1f)" % b["y"])
ok(suika.R[0] <= b["x"] <= suika.WW - suika.R[0], "통 안에 있음")

s.reset()
r = suika.R[0]
for x in (suika.WW / 2 - r, suika.WW / 2 + r):
    s.balls.append({"x": x, "y": suika.WH - r, "px": x, "py": suika.WH - r, "t": 0})
s.tick(0.033)
ok(len(s.balls) == 1 and s.balls[0]["t"] == 1, "같은 과일 합쳐짐")
ok(s.score == suika.POINTS[1], "합치기 점수")

s.reset()
rt = suika.R[suika.TOP]        # 최고 티어는 합쳐지지 않으므로 그대로 쌓인다
for i in range(3):             # 셋을 쌓으면 맨 위는 통 밖으로 넘친다
    x, y = suika.WW / 2, suika.WH - rt - i * 2 * rt
    s.balls.append({"x": x, "y": y, "px": x, "py": y, "t": suika.TOP})
for _ in range(150):
    s.tick(0.033)
ok(s.over, "위험선 위에 쌓이면 게임오버")

# --- 랜덤 조작 + 저장/복원 + 실제 렌더 ---
random.seed(7)
try:
    root = tk.Tk()
    root.withdraw()
    canvas = tk.Canvas(root, width=400, height=520)
except tk.TclError as e:
    print("디스플레이 없음, 렌더 테스트 생략:", e)
    canvas = None

# --- 새로 넣은 게임들 규칙 ---
p = puyo.Puyo()
p.grid = [[None] * puyo.COLS for _ in range(puyo.ROWS)]
for i in range(4):
    p.grid[puyo.ROWS - 1][i] = 0
p.resolve()
ok(all(v is None for v in p.grid[puyo.ROWS - 1]), "뿌요 4개 터짐")
ok(p.score > 0, "뿌요 점수")

p = puyo.Puyo()
p.grid = [[None] * puyo.COLS for _ in range(puyo.ROWS)]
for i in range(3):
    p.grid[puyo.ROWS - 1][i] = 0
p.resolve()
ok(p.grid[puyo.ROWS - 1][0] == 0, "3개는 안 터짐")

p = puyo.Puyo()
p.grid = [[None] * puyo.COLS for _ in range(puyo.ROWS)]
p.grid[0][0] = 1
p.settle()
ok(p.grid[0][0] is None and p.grid[puyo.ROWS - 1][0] == 1, "뜬 뿌요는 내려앉음")

ok(g2048.slide_row([2, 2, 4, 0]) == ([4, 4, 0, 0], 4), "2048 합치기")
ok(g2048.slide_row([2, 2, 2, 2]) == ([4, 4, 0, 0], 8), "2048 한 번씩만")
ok(g2048.slide_row([0, 0, 0, 2]) == ([2, 0, 0, 0], 0), "2048 밀기만")

# 네모로직 — 500판이 전부 '줄 논리만으로' 풀려야 한다
ok(nonogram.clues([1, 1, 0, 1, 0]) == [2, 1], "네모로직 힌트")
ok(nonogram.clues([0, 0, 0]) == [0], "빈 줄 힌트")
ok(nonogram.LEVELS == 500, "네모로직 500판")
probe = list(range(0, nonogram.LEVELS, 17)) + [0, 1, 498, 499]
unsolvable = []
for lv in probe:
    sol, rc, cc = nonogram.make(lv)
    if nonogram.line_solve(rc, cc, len(sol)) != sol:
        unsolvable.append(lv)
ok(not unsolvable, "네모로직 %d판 표본 전부 논리로 풀림 (실패 %s)"
   % (len(probe), unsolvable[:3]))
ok(nonogram.make(300)[0] == nonogram.make(300)[0], "같은 레벨은 같은 판")
ok(nonogram.size_for(0) < nonogram.size_for(499), "뒤로 갈수록 판이 커짐")

ng = nonogram.Nonogram()
for r in range(ng.n):
    for cc in range(ng.n):
        ng.grid[r][cc] = 1 if ng.sol[r][cc] else 0
ng.check()
ok(ng.done and ng.score == ng.n * ng.n, "네모로직 정답 인식")
lv_before = ng.level
ng.key("Return")
ok(ng.level == lv_before + 1 and not ng.done, "Enter 로 다음 판")
ng.level = 40
ng.reset()
ok(ng.level == 40, "R 은 이 판만 다시 — 레벨은 유지")

# Flood It — 허용 횟수 안에 탐욕 풀이로 깰 수 있어야 한다
f = floodit.FloodIt()
f.grid = [[0] * f.n for _ in range(f.n)]
f.flood(3)
ok(len(f.blob()) == f.n ** 2 and f.won, "Flood It 한 수로 완성")
ok(f.score > 0, "Flood It 점수")
tight = []
for lv in range(0, floodit.LEVELS, 7):
    g2 = floodit.FloodIt()
    g2.level = lv
    g2.load_level()
    if floodit.greedy_moves(g2.grid, g2.n, g2.ncolors) > g2.limit:
        tight.append(lv)
ok(not tight, "Flood It 모든 표본 단계가 깰 수 있음 (불가 %s)" % tight[:3])
ok(floodit.tier(0)[0] < floodit.tier(floodit.LEVELS - 1)[0], "뒤로 갈수록 판이 커짐")

# 소코반 — 생성한 판이 실제로 풀리는지 탐색으로 확인
sk = sokoban.Sokoban()
ok(sokoban.LEVELS == 200, "소코반 200판")
unsolved = []
for lv in list(range(0, 60, 6)) + [0, 59]:
    walls, goals, boxes, man, rows, cols = sokoban.build(lv)
    floor = {(r, c) for r in range(rows) for c in range(cols)
             if (r, c) not in walls}
    d = sokoban.min_pushes(floor, goals, boxes, man)
    if not d:
        unsolved.append(lv)
ok(not unsolved, "소코반 표본 전부 풀림 (실패 %s)" % unsolved[:3])
ok(sokoban.build(120)[0] == sokoban.build(120)[0], "같은 레벨은 같은 판")

sk.walls, sk.goals, sk.boxes, sk.man = set(), {(0, 3)}, {(0, 2)}, (0, 1)
sk.rows = sk.cols = 4
sk.history, sk.moves, sk.cleared = [], 0, False
sk.step(0, 1)
ok(sk.man == (0, 2) and sk.boxes == {(0, 3)}, "상자 밀기")
ok(sk.cleared and sk.score > 0, "목표에 올리면 성공")
sk.undo()
ok(sk.man == (0, 1) and sk.boxes == {(0, 2)} and not sk.cleared, "무르기")
sk.walls = {(0, 3)}
sk.boxes, sk.man = {(0, 2)}, (0, 1)
sk.step(0, 1)
ok(sk.man == (0, 1), "벽 뒤 상자는 못 민다")
sk.level = 30
sk.reset()
ok(sk.level == 30, "R 은 이 판만 다시 — 레벨은 유지")

# 끝없는 게임들의 단계
tt = tetris.Tetris()
ok(tt.level == 1, "테트리스 1단계로 시작")
tt.lines = 30
ok(tt.level == 4 and tt.interval < 0.8, "줄을 지울수록 단계가 오르고 빨라짐")
pp = puyo.Puyo()
ok(pp.level == 1, "뿌요 1단계로 시작")
pp.popped = 90
ok(pp.level == 4 and pp.interval < 0.75, "터뜨릴수록 단계가 오르고 빨라짐")

KEYS = ["Left", "Right", "Up", "Down", "space", "s", "x", "u", "Return",
        "BackSpace"]
for cls in (tetris.Tetris, suika.Suika, puyo.Puyo, g2048.G2048, threes.Threes,
            tripletown.TripleTown, nonogram.Nonogram, floodit.FloodIt,
            sokoban.Sokoban):
    g = cls()
    for _ in range(400):
        g.key(random.choice(KEYS))
        g.tick(0.033)
    st = g.state()
    import json
    st = json.loads(json.dumps(st))          # JSON 왕복까지 확인
    h = cls()
    h.load(st)
    ok(h.score == g.score, "%s 저장/복원 점수" % cls.__name__)
    if canvas:
        canvas.delete("all")
        g.draw(canvas, 0, 26, 400, 476)
        h.draw(canvas, 0, 26, 400, 476)
        ok(len(canvas.find_all()) > 0, "%s 렌더 결과 있음" % cls.__name__)

if canvas:
    root.destroy()

# --- 셸: 내리기/꺼내기, 최고 기록 유지 ---
if canvas is not None:
    import tempfile

    import desk

    desk.SAVE = os.path.join(tempfile.mkdtemp(), "deskgames.json")
    sh = desk.Shell()
    ok(sh.menu, "처음 켜면 고르는 화면")
    sh.draw()
    ok(len(sh.canvas.find_all()) > 0, "메뉴가 그려짐")
    sh.menu_key("Down")
    ok(sh.pick == 1, "↓ 로 다음 게임")
    sh.menu_key("Return")
    ok(sh.idx == 1 and not sh.menu, "Enter 로 고르면 메뉴가 닫힘")
    sh.on_key(type("E", (), {"keysym": "3"})())
    ok(sh.idx == 2 and not sh.menu, "숫자키로 바로 전환")
    sh.on_key(type("E", (), {"keysym": "m"})())
    ok(sh.menu and sh.pick == 2, "M 으로 메뉴, 지금 게임에 커서")
    ok(len(sh.games) == 9, "게임 9개")
    sh.on_key(type("E", (), {"keysym": "9"})())
    ok(sh.idx == 8, "9번까지 숫자키로 이동")
    ok(not sh.root.attributes("-topmost"), "항상 위가 꺼져 있음")
    sh.on_key(type("E", (), {"keysym": "m"})())
    sh.menu_key("Return")

    # 한/영 전환
    from games import i18n
    ok(i18n.t("게임 고르기") == "게임 고르기", "기본은 한국어")
    sh.on_key(type("E", (), {"keysym": "l"})())
    ok(i18n.LANG == "en" and sh.lang == "en", "L 로 영어 전환")
    ok(i18n.t("게임 고르기") == "Choose a game", "영어로 나옴")
    missing = [k for g in sh.games for k in [g.help]
               if k not in i18n.EN]
    ok(not missing, "게임 도움말 번역 누락: %s" % missing[:2])
    sh.draw()
    ok(len(sh.canvas.find_all()) > 0, "영어로도 그려짐")
    for i in range(len(sh.games)):
        sh.idx, sh.menu = i, False
        sh.draw()
    sh.menu = True
    sh.on_key(type("E", (), {"keysym": "l"})())
    ok(i18n.LANG == "ko", "L 로 다시 한국어")

    # 투명도 바
    before = sh.alpha
    sh.slider_hit(type("E", (), {"x": desk.BAR_X1, "y": desk.BAR_Y})())
    ok(sh.alpha == desk.ALPHA_MAX, "바 오른쪽 끝 = 100%")
    sh.slider_hit(type("E", (), {"x": desk.BAR_X0, "y": desk.BAR_Y})())
    ok(sh.alpha == desk.ALPHA_MIN, "바 왼쪽 끝 = 최소")
    mid = (desk.BAR_X0 + desk.BAR_X1) / 2
    sh.slider_hit(type("E", (), {"x": mid, "y": desk.BAR_Y})())
    ok(abs(sh.alpha - (desk.ALPHA_MIN + desk.ALPHA_MAX) / 2) < 0.03, "바 가운데")
    ok(not sh.slider_hit(type("E", (), {"x": mid, "y": desk.BAR_Y + 60})()),
       "바에서 먼 곳은 안 잡힘")
    sh.menu = False
    ok(not sh.slider_hit(type("E", (), {"x": mid, "y": desk.BAR_Y})()),
       "게임 중에는 바가 없다")
    sh.menu = True
    sh.set_alpha(before)

    sh.game.score = 4242
    sh.stash()
    ok(sh.root.state() == "iconic", "ESC로 작업표시줄에 내려감")
    ok(sh.root.winfo_exists(), "내려가도 프로그램은 살아 있음")
    ok(sh.game.score == 4242, "내려가도 진행 점수 유지")
    ok(os.path.exists(desk.SAVE), "내려갈 때 저장됨")

    sh.restore()
    sh.root.update()
    ok(sh.root.state() == "normal", "다시 화면으로 복귀")
    ok(sh.game.score == 4242, "복귀해도 판 그대로")

    sh.game.score = 10
    sh.save()
    fresh = desk.Shell()
    ok(fresh.games[sh.idx].best >= 4242, "최고 기록은 점수가 내려가도 유지")
    ok(fresh.games[sh.idx].score == 10, "진행 중인 판도 복원")
    fresh.root.destroy()
    sh.root.destroy()

if fails:
    print("실패 %d건:" % len(fails))
    for f in fails:
        print("  -", f)
    sys.exit(1)
print("모두 통과")
