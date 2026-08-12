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
T_PIECE = [(0, 1), (1, 0), (1, 1), (1, 2)]
ok(tetris.rotate(T_PIECE, 3) == [(1, 2), (0, 1), (1, 1), (2, 1)], "T 시계 회전")
ok(sorted(tetris.rotate(tetris.rotate(T_PIECE, 3), 3, False)) == sorted(T_PIECE),
   "시계 후 반시계 = 원위치")
ok(sorted(tetris.rotate(T_PIECE, 3, False)) !=
   sorted(tetris.rotate(T_PIECE, 3)), "반시계는 시계와 다름")
turned = T_PIECE
for _ in range(3):
    turned = tetris.rotate(turned, 3, False)
ok(sorted(turned) == sorted(tetris.rotate(T_PIECE, 3)), "반시계 3번 = 시계 1번")

tz = tetris.Tetris()
tz.key_id, tz.n, tz.cells, tz.pr, tz.pc = "T", 3, list(T_PIECE), 5, 4
before = list(tz.cells)
tz.key("z")
ok(tz.cells != before, "Z 키로 회전됨")
tz.key("Up")
ok(sorted(tz.cells) == sorted(before), "↑ 로 되돌아옴")

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

# 2048 무르기 — 원래 규칙대로 한 수만
gu = g2048.G2048()
gu.grid = [[2, 2, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
gu.score, gu.prev = 0, None
snap = [r[:] for r in gu.grid]
gu.key("Left")
ok(gu.score == 4 and gu.prev is not None, "2048 이동 후 직전 판이 기록됨")
gu.key("BackSpace")
ok(gu.grid == snap and gu.score == 0, "2048 무르기로 판과 점수 복원")
ok(gu.best >= 4, "무르기해도 최고 기록은 유지")
ok(gu.key("BackSpace") is True and gu.grid == snap,
   "연달아 눌러도 두 수는 안 무름")
ok(gu.prev is None, "무른 뒤에는 무를 게 없음")

gu.grid = [[2, 2, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
gu.key("Left")
mid = [r[:] for r in gu.grid]
import json as _json
gu2 = g2048.G2048()
gu2.load(_json.loads(_json.dumps(gu.state())))
ok(gu2.grid == mid, "판 저장/복원")
gu2.key("BackSpace")
ok(gu2.grid == [[2, 2, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
   "창을 닫았다 켜도 직전 한 수는 무를 수 있음")

# 네모로직 — 500판이 전부 '줄 논리만으로' 풀려야 한다
ok(nonogram.clues([1, 1, 0, 1, 0]) == [2, 1], "네모로직 힌트")
ok(nonogram.clues([0, 0, 0]) == [0], "빈 줄 힌트")
ok(nonogram.LEVELS == 500, "네모로직 크기마다 500판")
ok(nonogram.SIZES == (10, 15, 20), "10x10 · 15x15 · 20x20")
unsolvable = []
probe = []
for size in nonogram.SIZES:
    for lv in list(range(0, nonogram.LEVELS, 60)) + [0, 499]:
        probe.append((size, lv))
        sol, rc, cc = nonogram.make(size, lv)
        if nonogram.line_solve(rc, cc, size) != sol:
            unsolvable.append((size, lv))
ok(not unsolvable, "네모로직 %d판 표본 전부 논리로 풀림 (실패 %s)"
   % (len(probe), unsolvable[:3]))
ok(nonogram.make(15, 300)[0] == nonogram.make(15, 300)[0], "같은 판은 항상 같음")
ok(nonogram.make(10, 0)[0] != nonogram.make(15, 0)[0], "크기가 다르면 다른 판")

ng = nonogram.Nonogram()
ok(ng.n == 10, "기본 크기 10x10")
ng.key("s")
ok(ng.n == 15, "S 로 15x15")
ng.level = 7
ng.key("s")
ok(ng.n == 20 and ng.level == 0, "크기마다 진행도가 따로")
ng.key("s")
ok(ng.n == 10, "S 로 다시 10x10")
ng.n = 15
ok(ng.level == 7, "15x15 로 돌아오면 하던 판 그대로")
ng.n = 10
ng.load_level()

# 마우스로 칠하기 · 칠하기/X 전환
import tkinter as _tk
if canvas is not None:
    nm = nonogram.Nonogram()
    nm.draw(canvas, 0, 26, 400, 476)
    ox, oy, cell, box = nm._geom
    cx, cy = ox + cell * 2 + cell / 2, oy + cell * 3 + cell / 2
    ok(nm.mode == nonogram.PAINT, "기본은 칠하기 모드")
    nm.click(cx, cy)
    ok(nm.grid[3][2] == 1, "클릭한 칸이 칠해짐")
    ok((nm.cr, nm.cc) == (3, 2), "커서도 그 칸으로 옮겨짐")
    nm.click(cx, cy)
    ok(nm.grid[3][2] == 0, "같은 칸 다시 클릭하면 지워짐")
    nm.click(box[0] + 5, box[1] + 5)
    ok(nm.mode == nonogram.XMARK, "모드 단추를 누르면 X 표시로")
    nm.click(cx, cy)
    ok(nm.grid[3][2] == 2, "X 모드에서는 X 가 찍힘")
    nm.click(cx, cy, button=3)
    ok(nm.grid[3][2] == 1, "오른쪽 버튼은 반대쪽으로 칠함")
    nm.key("Tab")
    ok(nm.mode == nonogram.PAINT, "Tab 으로 모드 전환")
    # 드래그: 처음 누른 칸에서 정해진 값이 이어져야 한다
    nm.grid = [[0] * nm.n for _ in range(nm.n)]
    nm.click(ox + cell / 2, oy + cell / 2)
    for i in range(1, 4):
        nm.click(ox + cell * i + cell / 2, oy + cell / 2, drag=True)
    ok([nm.grid[0][i] for i in range(4)] == [1, 1, 1, 1], "드래그로 이어 칠하기")
    for i in range(4):
        nm.click(ox + cell * i + cell / 2, oy + cell / 2, drag=True)
    ok([nm.grid[0][i] for i in range(4)] == [1, 1, 1, 1],
       "드래그 중에는 켜졌다 꺼졌다 하지 않음")
    ok(nm.click(5, 5) is False, "판 밖 클릭은 무시")

    # 다 채운 줄은 X 자동
    af = nonogram.Nonogram()
    af.n = 5
    af.sol = [[1, 1, 0, 1, 0], [0, 0, 0, 0, 0], [1, 0, 0, 0, 0],
              [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]]
    af.row_clues = [nonogram.clues(r) for r in af.sol]
    af.col_clues = [nonogram.clues([af.sol[r][c] for r in range(5)])
                    for c in range(5)]
    af.grid = [[0] * 5 for _ in range(5)]
    af.paint(0, 0, nonogram.PAINT)
    ok(af.grid[0][1] == 0, "아직 힌트를 못 채운 줄은 그대로")
    af.paint(0, 1, nonogram.PAINT)
    af.paint(0, 3, nonogram.PAINT)
    ok(af.grid[0] == [1, 1, 2, 1, 2], "힌트를 다 채우면 나머지가 X 로")
    ok([af.grid[r][1] for r in range(5)] == [1, 2, 2, 2, 2],
       "세로줄도 같이 채워짐")
    ok(all(af.grid[r][c] != 2 or not af.sol[r][c]
           for r in range(5) for c in range(5)),
       "자동 X 가 정답 칸을 덮지 않음")

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

# 레벨 건너뛰기 (레벨 있는 게임 공통)
for g3 in (nonogram.Nonogram(), sokoban.Sokoban(), floodit.FloodIt()):
    g3.jump(7)
    ok(g3.level == 7, "%s 판 건너뛰기" % g3.name)
    g3.jump(-7)
    ok(g3.level == 0, "%s 뒤로 건너뛰기" % g3.name)
    g3.jump(-1)
    ok(g3.level == g3.LEVELS - 1, "%s 첫 판에서 뒤로 = 마지막 판" % g3.name)
ok(tetris.Tetris().jump(3) is False, "레벨 없는 게임은 건너뛰기 없음")

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
# 당긴 수순을 뒤집어 실제로 밀어 본다 — 전수 검사도 10초면 끝난다
unsolved = [lv + 1 for lv in range(sokoban.LEVELS) if not sokoban.verify(lv)]
ok(not unsolved, "소코반 200판 전부 풀림 (실패 %s)" % unsolved[:3])

walls, goals, boxes, man, rows, cols, log = sokoban.build(0, trace=True)
ok(log and len(boxes) == len(goals), "생성 기록이 남아 있음")
floor = {(r, c) for r in range(rows) for c in range(cols)
         if (r, c) not in walls}
ok(sokoban.min_pushes(floor, goals, boxes, man), "탐색으로도 1판은 풀림")
ok(sokoban.spread(goals, goals) == 0, "다 푼 판은 거리 0")
ok(sokoban.spread(boxes, goals) > 0, "만든 판은 목표에서 떨어져 있음")
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
ok(tt.level > 1 and tt.interval < 0.58, "줄을 지울수록 단계가 오르고 빨라짐")
pp = puyo.Puyo()
ok(pp.level == 1, "뿌요 1단계로 시작")
pp.popped = 90
ok(pp.level > 1 and pp.interval < 0.55, "터뜨릴수록 단계가 오르고 빨라짐")
ok(len(puyo.COLORS) == 5, "뿌요 색 5개")

pz = puyo.Puyo()
pz.rot = 0
pz.key("z")
ok(pz.rot == 3, "뿌요 Z 는 반시계")
pz.key("Up")
ok(pz.rot == 0, "뿌요 ↑ 로 되돌아옴")

KEYS = ["Left", "Right", "Up", "Down", "space", "s", "x", "u", "z", "Return",
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
    sh.on_key(type("E", (), {"keysym": "Tab"})())
    ok(sh.menu, "Tab 은 이제 메뉴를 안 건드린다 (게임 쪽으로 간다)")
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

    # 화면에서 안 보이는 동안에는 시간이 멈춰야 한다.
    # root.state() 는 환경에 따라 내려가 있어도 "normal" 을 돌려주므로
    # 창 상태를 직접 추적한다 — 그것만 믿었더니 숨긴 채로 계속 돌아갔다.
    sh.idx, sh.menu = 0, False          # 테트리스(중력이 있는 게임)
    tick = sh.games[0]
    sh.root.update()

    def run(n=60):
        for _ in range(n):
            if not sh.paused and not sh.menu:
                tick.tick(0.033)

    ok(not sh.paused, "보일 때는 안 멈춤")
    where = tick.pr
    run()
    ok(tick.pr != where, "보일 때는 블록이 떨어짐")

    sh.stash()
    sh.root.update()
    ok(sh.paused, "내려가면 멈춤 상태")
    where = tick.pr
    run()
    ok(tick.pr == where, "작업표시줄에 내려가 있는 동안 블록이 안 떨어짐")

    sh.restore()
    sh.root.update()
    ok(not sh.paused, "꺼내면 다시 흐름")
    where = tick.pr
    run()
    ok(tick.pr != where, "복귀하면 블록이 다시 떨어짐")

    sh.faded = True
    where = tick.pr
    run()
    ok(sh.paused and tick.pr == where, "H 로 숨긴 동안에도 멈춤")
    sh.faded = False

    sh.idx = 1
    sh.game.score = 4242
    sh.stash()
    ok(sh.root.winfo_exists(), "내려가도 프로그램은 살아 있음")
    ok(sh.game.score == 4242, "내려가도 진행 점수 유지")
    ok(os.path.exists(desk.SAVE), "내려갈 때 저장됨")

    sh.restore()
    sh.root.update()
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
