"""Triple Town — 같은 것 3개 이상이 붙으면 한 단계 위로."""
import random

from .base import DIM, EMPTY, Game, LINE, center_text, ink_on, rrect
from .i18n import t

N = 6

# 값: (이름, 색, 다음 단계, 점수)
ITEMS = {
    1: ("풀", "#4f8f4a", 2, 5),
    2: ("덤불", "#3f7a5c", 3, 20),
    3: ("나무", "#2f6f45", 4, 100),
    4: ("오두막", "#a8763a", 5, 500),
    5: ("집", "#c08a3e", 6, 1500),
    6: ("저택", "#c9a227", 7, 5000),
    7: ("성", "#d9c06a", 8, 20000),
    8: ("공중성", "#e8e2b0", None, 0),
    20: ("곰", "#8a5a3a", None, 0),
    21: ("묘비", "#6b7280", 22, 500),
    22: ("교회", "#8b93a3", 23, 5000),
    23: ("대성당", "#b9c0cc", None, 0),
}
SPAWN = [(1, 58), (2, 22), (3, 12), (20, 8)]


def roll():
    n = random.randrange(100)
    acc = 0
    for v, wgt in SPAWN:
        acc += wgt
        if n < acc:
            return v
    return 1


class TripleTown(Game):
    name = "TRIPLE TOWN"
    help = "방향키 커서 · Space 놓기 · S 보관칸 교체"

    def reset(self):
        self.grid = [[0] * N for _ in range(N)]
        self.cur = roll()
        self.hold = 0
        self.cr = self.cc = N // 2
        self.score = 0
        self.over = False

    # --- 병합 ---
    def group(self, r, c):
        """(r,c)와 같은 값으로 이어진 칸들."""
        v = self.grid[r][c]
        seen, stack = {(r, c)}, [(r, c)]
        while stack:
            cr, cc = stack.pop()
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nr, nc = cr + dr, cc + dc
                if 0 <= nr < N and 0 <= nc < N and (nr, nc) not in seen \
                        and self.grid[nr][nc] == v:
                    seen.add((nr, nc))
                    stack.append((nr, nc))
        return seen

    def resolve(self, r, c):
        """놓은 자리에서 연쇄 병합."""
        while True:
            v = self.grid[r][c]
            nxt = ITEMS.get(v, (None, None, None, 0))[2]
            if nxt is None:
                return
            cells = self.group(r, c)
            if len(cells) < 3:
                return
            for rr, cc in cells:
                self.grid[rr][cc] = 0
            self.grid[r][c] = nxt
            self.bump(ITEMS[v][3] * len(cells))

    # --- 곰 ---
    def move_bears(self):
        bears = [(r, c) for r in range(N) for c in range(N) if self.grid[r][c] == 20]
        random.shuffle(bears)
        for r, c in bears:
            if self.grid[r][c] != 20:
                continue
            free = [(r + dr, c + dc) for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1))
                    if 0 <= r + dr < N and 0 <= c + dc < N and self.grid[r + dr][c + dc] == 0]
            if not free:
                self.grid[r][c] = 21          # 갇힌 곰은 묘비가 된다
                self.resolve(r, c)
                continue
            nr, nc = random.choice(free)
            self.grid[r][c] = 0
            self.grid[nr][nc] = 20

    # --- 조작 ---
    def key(self, k):
        if self.over:
            return False
        if k == "Left":
            self.cc = (self.cc - 1) % N
        elif k == "Right":
            self.cc = (self.cc + 1) % N
        elif k == "Up":
            self.cr = (self.cr - 1) % N
        elif k == "Down":
            self.cr = (self.cr + 1) % N
        elif k in ("s", "S"):
            if self.hold == 0:
                self.hold, self.cur = self.cur, roll()
            else:
                self.hold, self.cur = self.cur, self.hold
        elif k == "space":
            if self.grid[self.cr][self.cc] != 0:
                return True
            self.grid[self.cr][self.cc] = self.cur
            self.resolve(self.cr, self.cc)
            self.move_bears()
            self.cur = roll()
            if not any(0 in row for row in self.grid):
                self.over = True
        else:
            return False
        return True

    # --- 저장 ---
    def state(self):
        return {"grid": self.grid, "cur": self.cur, "hold": self.hold,
                "cr": self.cr, "cc": self.cc, "score": self.score, "over": self.over}

    def load(self, d):
        self.grid = [list(r) for r in d["grid"]]
        self.cur, self.hold = d["cur"], d["hold"]
        self.cr, self.cc = d["cr"], d["cc"]
        self.score, self.over = d["score"], d["over"]

    # --- 그리기 ---
    def draw(self, c, x, y, w, h):
        side = 44
        cell = int(min((w - side) / N, h / N)) - 3
        gap = 3
        bw = N * (cell + gap) - gap
        ox = x + (w - side - bw) / 2
        oy = y + (h - bw) / 2

        for r in range(N):
            for col in range(N):
                v = self.grid[r][col]
                bx, by = ox + col * (cell + gap), oy + r * (cell + gap)
                rrect(c, bx, by, bx + cell, by + cell, 4,
                      fill=ITEMS[v][1] if v else EMPTY, outline="")
                if v:
                    center_text(c, bx + cell / 2, by + cell / 2,
                                t(ITEMS[v][0])[0], 11, ink_on(ITEMS[v][1]))

        # 커서
        bx, by = ox + self.cc * (cell + gap), oy + self.cr * (cell + gap)
        c.create_rectangle(bx - 2, by - 2, bx + cell + 2, by + cell + 2,
                           outline="#1f66b0", width=2)

        px = ox + bw + 12
        for label, v, dy in (("놓을 것", self.cur, 8), ("보관 S", self.hold, 74)):
            center_text(c, px + 16, oy + dy, t(label), 7, DIM)
            if v:
                rrect(c, px + 2, oy + dy + 12, px + 30, oy + dy + 40, 4,
                      fill=ITEMS[v][1], outline="")
                center_text(c, px + 16, oy + dy + 26, t(ITEMS[v][0])[0], 11, ink_on(ITEMS[v][1]))
            else:
                c.create_rectangle(px + 2, oy + dy + 12, px + 30, oy + dy + 40,
                                   outline=LINE)
