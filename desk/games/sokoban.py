"""소코반 — 상자를 밀어서 목표 칸에 모두 올린다. 200판, 점점 어려워진다.

판은 **거꾸로** 만든다. 먼저 다 푼 모습(상자가 전부 목표 위)을 놓고,
거기서 상자를 '당겨서' 흐트러뜨린다. 당기기를 뒤집으면 그대로 정답이므로
만들어진 판은 반드시 풀린다 — 게임 중에 탐색을 돌릴 필요가 없다.
난이도는 '몇 번 당겼나'로 조절한다. 실제로 풀리는지는 테스트에서
min_pushes(앞으로 풀어 보는 탐색)로 따로 확인한다.

레벨 번호가 씨앗이라 같은 번호는 언제나 같은 판이다.
"""
import random
from collections import deque

from .base import DIM, Game, PANEL, center_text, rrect
from .i18n import t

LEVELS = 200
MOVES = {"Left": (0, -1), "Right": (0, 1), "Up": (-1, 0), "Down": (1, 0)}
DIRS = [(1, 0), (-1, 0), (0, 1), (0, -1)]


def tier(level):
    """(세로, 가로, 상자 수, 목표 당김 횟수)."""
    if level < 20:
        return 7, 7, 2, 8
    if level < 60:
        return 7, 8, 3, 12
    if level < 110:
        return 8, 8, 3, 16
    if level < 160:
        return 8, 9, 4, 20
    return 9, 9, 4, 24


def spread(boxes, goals):
    """상자들이 목표에서 얼마나 떨어져 있나. 클수록 어려운 판이다."""
    return sum(min(abs(r - gr) + abs(c - gc) for gr, gc in goals)
               for r, c in boxes)


def neighbors(cell):
    r, c = cell
    return [(r + dr, c + dc) for dr, dc in DIRS]


def reachable(floor, boxes, start):
    """상자를 벽으로 치고, 사람이 갈 수 있는 칸."""
    seen, q = {start}, deque([start])
    while q:
        cell = q.popleft()
        for n in neighbors(cell):
            if n in floor and n not in boxes and n not in seen:
                seen.add(n)
                q.append(n)
    return seen


def min_pushes(floor, goals, boxes, man, cap=60000):
    """앞으로 풀어 보기. 최소 밀기 수, 못 풀면 None."""
    goals = frozenset(goals)

    def norm(bs, m):
        """사람 위치는 '갈 수 있는 칸 중 가장 작은 것'으로 뭉뚱그린다."""
        return frozenset(bs), min(reachable(floor, bs, m))

    start = norm(frozenset(boxes), man)
    if start[0] == goals:
        return 0
    seen = {start}
    q = deque([(start, 0)])
    while q and len(seen) < cap:
        (bs, m), d = q.popleft()
        area = reachable(floor, bs, m)
        for box in bs:
            for dr, dc in DIRS:
                stand = (box[0] - dr, box[1] - dc)
                dest = (box[0] + dr, box[1] + dc)
                if stand not in area or dest not in floor or dest in bs:
                    continue
                nb = frozenset(bs - {box} | {dest})
                if nb == goals:
                    return d + 1
                key = norm(nb, box)
                if key not in seen:
                    seen.add(key)
                    q.append((key, d + 1))
    return None


def build(level, trace=False):
    """레벨 번호로 판 하나. (벽, 목표, 상자, 사람, 세로, 가로).

    같은 번호는 언제나 같은 판이다.
    trace=True 면 당긴 기록도 함께 돌려준다 — 뒤집으면 그대로 정답이라
    탐색 없이도 '이 판이 풀린다'를 증명할 수 있다(verify 참고).
    """
    rows, cols, nbox, need = tier(level)
    rnd = random.Random(4211 + level * 6421)
    best = None

    for _ in range(8):          # 몇 번 만들어 보고 가장 잘 흐트러진 것을 쓴다
        # 1. 방 만들기 — 테두리는 벽, 안쪽에 벽 몇 개
        floor = {(r, c) for r in range(1, rows - 1) for c in range(1, cols - 1)}
        for cell in list(floor):
            if rnd.random() < 0.12 and len(floor) > nbox * 4 + 6:
                floor.discard(cell)
        if len(floor) < nbox * 4 + 6:
            continue
        # 바닥이 하나로 이어져 있어야 한다
        floor = reachable(floor, set(), next(iter(floor)))
        if len(floor) < nbox * 4 + 6:
            continue

        # 2. 다 푼 모습에서 시작 — 상자가 목표 위에 있다
        cells = sorted(floor)
        rnd.shuffle(cells)
        goals = set(cells[:nbox])
        boxes = set(goals)
        man = cells[nbox]

        # 3. 거꾸로 당겨서 흐트러뜨리기
        pulls = 0
        log = []
        for _ in range(30 + level):
            area = reachable(floor, boxes, man)
            picks = []
            for box in boxes:
                for dr, dc in DIRS:
                    back = (box[0] + dr, box[1] + dc)            # 상자가 갈 자리
                    stand = (box[0] + 2 * dr, box[1] + 2 * dc)   # 사람이 설 자리
                    if back in floor and back not in boxes and stand in floor \
                            and stand not in boxes and back in area:
                        picks.append((box, back, stand))
            if not picks:
                break
            # 그냥 무작위로 당기면 상자가 갔다 왔다 하면서 서로 상쇄돼
            # 목표 바로 옆에 머문다. 대체로 '목표에서 멀어지는' 당기기를
            # 고르되, 가끔 무작위를 섞어 판이 뻔해지지 않게 한다.
            if rnd.random() < 0.8:
                best_pick, best_far = None, None
                for cand in picks:
                    moved = (boxes - {cand[0]}) | {cand[1]}
                    far = spread(moved, goals)
                    if best_far is None or far > best_far:
                        best_pick, best_far = cand, far
                box, back, stand = best_pick
            else:
                box, back, stand = picks[rnd.randrange(len(picks))]
            # 당기기: 사람이 back(자기 자리)에서 stand로 물러나면서 상자를
            # box → back 으로 끌고 온다. 사람은 stand에 선다.
            # (여기서 man = box 로 두면 사람이 상자를 넘어가 버려서
            #  되돌릴 수 없는 판이 만들어진다 — 실제로 그 버그가 있었다)
            boxes.discard(box)
            boxes.add(back)
            man = stand
            log.append((box, back, stand))
            if back not in goals:
                pulls += 1

        if boxes == goals:
            continue                        # 하나도 안 움직였다
        walls = {(r, c) for r in range(rows) for c in range(cols)
                 if (r, c) not in floor}
        # 여러 번 만들어 보고 '가장 멀리 흩어진' 판을 고른다.
        # 당긴 횟수보다 실제로 벌어진 거리가 난이도에 더 잘 맞는다.
        cand = (spread(boxes, goals), walls, goals, boxes, man, rows, cols, log)
        if best is None or cand[0] > best[0]:
            best = cand
        if pulls >= need and cand[0] >= need:
            break

    if best is not None:
        return best[1:] if trace else best[1:-1]

    # 여기까지 오는 일은 거의 없다. 아주 단순한 판으로 대신한다.
    floor = {(1, c) for c in range(1, 5)}
    walls = {(r, c) for r in range(3) for c in range(6) if (r, c) not in floor}
    plain = (walls, {(1, 1)}, {(1, 2)}, (1, 3), 3, 6)
    return plain + ([((1, 1), (1, 2), (1, 3))],) if trace else plain


def verify(level):
    """당긴 기록을 뒤집어 실제로 밀어 보고, 상자가 목표에 다 오르는지 본다.

    탐색이 아니라 '만들 때 쓴 수순'을 그대로 되짚는 것이라 즉시 끝난다.
    도중에 한 수라도 규칙에 어긋나면 False.
    """
    walls, goals, boxes, man, rows, cols, log = build(level, trace=True)
    floor = {(r, c) for r in range(rows) for c in range(cols)
             if (r, c) not in walls}
    boxes, man = set(boxes), man
    for box, back, stand in reversed(log):
        # 당길 때 상자는 box → back, 사람은 back → stand 였다.
        # 되짚으면 사람이 stand → back 으로 가서 상자를 back → box 로 민다.
        if back not in boxes or box in boxes or box not in floor:
            return False
        if stand not in reachable(floor, boxes, man):
            return False
        boxes.discard(back)
        boxes.add(box)
        man = back
    return boxes == set(goals)


class Sokoban(Game):
    name = "SOKOBAN"
    help = "방향키로 밀기 · U 무르기 · , . 판 넘기기 · Enter 다음 판"

    LEVELS = LEVELS

    def reset(self):
        """R은 '이 판 다시'다. 올라온 레벨은 그대로 둔다."""
        self.level = getattr(self, "level", 0)
        self.score = getattr(self, "score", 0)
        self.over = False
        self.load_level()

    def load_level(self):
        self.walls, self.goals, boxes, self.man, self.rows, self.cols = \
            build(self.level)
        self.boxes = set(boxes)
        self.moves = 0
        self.history = []
        self.cleared = False

    def next_level(self):
        self.level = (self.level + 1) % LEVELS
        self.load_level()

    def solved(self):
        return self.boxes == set(self.goals)

    # --- 조작 ---
    def key(self, k):
        if k in ("u", "U"):
            return self.undo()
        if k in ("Return", "KP_Enter"):
            if self.cleared:
                self.next_level()
                return True
            return False
        if k == "BackSpace":
            self.load_level()
            return True
        if self.cleared or k not in MOVES:
            return False
        return self.step(*MOVES[k])

    def step(self, dr, dc):
        r, c = self.man
        nr, nc = r + dr, c + dc
        if (nr, nc) in self.walls:
            return True
        pushed = None
        if (nr, nc) in self.boxes:
            br, bc = nr + dr, nc + dc
            if (br, bc) in self.walls or (br, bc) in self.boxes:
                return True                       # 뒤가 막혀 못 민다
            self.boxes.discard((nr, nc))
            self.boxes.add((br, bc))
            pushed = (nr, nc)
        self.history.append((self.man, pushed, (dr, dc)))
        self.man = (nr, nc)
        self.moves += 1
        if self.solved():
            self.cleared = True
            self.bump(max(60, 400 - self.moves * 4))
        return True

    def undo(self):
        if not self.history:
            return True
        man, pushed, (dr, dc) = self.history.pop()
        if pushed:
            self.boxes.discard((pushed[0] + dr, pushed[1] + dc))
            self.boxes.add(pushed)
        self.man = man
        self.moves = max(0, self.moves - 1)
        self.cleared = self.solved()
        return True

    # --- 저장 ---
    def state(self):
        return {"level": self.level, "score": self.score, "moves": self.moves,
                "boxes": sorted(self.boxes), "man": list(self.man),
                "cleared": self.cleared}

    def load(self, d):
        self.level = d["level"] % LEVELS
        self.load_level()
        self.score, self.moves = d["score"], d["moves"]
        self.boxes = {tuple(b) for b in d["boxes"]}
        self.man = tuple(d["man"])
        self.cleared = d["cleared"]
        self.over = False

    # --- 그리기 ---
    def draw(self, c, x, y, w, h):
        cell = int(min((w - 40) / self.cols, (h - 70) / self.rows))
        cell = min(cell, 44)
        bw, bh = cell * self.cols, cell * self.rows
        ox = x + (w - bw) / 2
        oy = y + (h - bh) / 2 - 12

        for r in range(self.rows):
            for col in range(self.cols):
                bx, by = ox + col * cell, oy + r * cell
                if (r, col) in self.walls:
                    rrect(c, bx, by, bx + cell, by + cell, 3,
                          fill="#8a94a4", outline="")
                    continue
                c.create_rectangle(bx, by, bx + cell, by + cell,
                                   fill=PANEL, outline="#eceff4")
                if (r, col) in self.goals:
                    m = cell * 0.32
                    c.create_oval(bx + m, by + m, bx + cell - m, by + cell - m,
                                  outline="#c9a227", width=2)

        for r, col in self.boxes:
            bx, by = ox + col * cell, oy + r * cell
            on = (r, col) in self.goals
            rrect(c, bx + 3, by + 3, bx + cell - 3, by + cell - 3, 4,
                  fill="#4c8f3f" if on else "#c9783a", outline="")

        r, col = self.man
        bx, by = ox + col * cell, oy + r * cell
        m = cell * 0.22
        c.create_oval(bx + m, by + m, bx + cell - m, by + cell - m,
                      fill="#2f6ea8", outline="")

        center_text(c, x + w / 2, oy + bh + 20,
                    t("%d / %d 판   %d수   상자 %d") %
                    (self.level + 1, LEVELS, self.moves, len(self.boxes)), 9, DIM)
        if self.cleared:
            center_text(c, x + w / 2, oy + bh / 2, t("성공! Enter 로 다음 판"), 13,
                        "#2f6ea8")
