"""2048 — 방향키로 밀어서 같은 수끼리 합치기."""
import random

from .base import DIM, EMPTY, Game, LINE, center_text, ink_on, rrect
from .i18n import t

N = 4
COLORS = {
    2: "#eef2f8", 4: "#e2eaf4", 8: "#8fb8dd", 16: "#6aa2d4", 32: "#4a8cc9",
    64: "#2f6ea8", 128: "#e8c86a", 256: "#e0b84a", 512: "#d9a72f",
    1024: "#d18c2a", 2048: "#c9724f",
}
BIG = "#c9384a"


def slide_row(row):
    """왼쪽으로 밀고 합치기. (새 줄, 얻은 점수)."""
    vals = [v for v in row if v]
    out, gained, i = [], 0, 0
    while i < len(vals):
        if i + 1 < len(vals) and vals[i] == vals[i + 1]:
            out.append(vals[i] * 2)
            gained += vals[i] * 2
            i += 2
        else:
            out.append(vals[i])
            i += 1
    return out + [0] * (N - len(out)), gained


class G2048(Game):
    name = "2048"
    help = "방향키로 밀기 · Backspace 한 수 무르기"

    def reset(self):
        self.grid = [[0] * N for _ in range(N)]
        self.score = 0
        self.over = False
        self.prev = None            # 원래 규칙대로 한 수만 무른다
        self.spawn()
        self.spawn()

    def spawn(self):
        empty = [(r, c) for r in range(N) for c in range(N) if self.grid[r][c] == 0]
        if not empty:
            return False
        r, c = random.choice(empty)
        self.grid[r][c] = 2 if random.random() < 0.9 else 4
        return True

    def lines(self, d):
        g = self.grid
        if d == "Left":
            return [[g[r][c] for c in range(N)] for r in range(N)]
        if d == "Right":
            return [[g[r][c] for c in reversed(range(N))] for r in range(N)]
        if d == "Up":
            return [[g[r][c] for r in range(N)] for c in range(N)]
        return [[g[r][c] for r in reversed(range(N))] for c in range(N)]

    def put_line(self, d, i, line):
        g = self.grid
        for j, v in enumerate(line):
            if d == "Left":
                g[i][j] = v
            elif d == "Right":
                g[i][N - 1 - j] = v
            elif d == "Up":
                g[j][i] = v
            else:
                g[N - 1 - j][i] = v

    def key(self, k):
        if k == "BackSpace":
            return self.undo()
        if self.over or k not in ("Left", "Right", "Up", "Down"):
            return False
        # 새 타일이 어디 생길지는 무작위라, 되돌리려면 판을 통째로 기억해야 한다
        snapshot = ([row[:] for row in self.grid], self.score)
        moved = False
        for i, line in enumerate(self.lines(k)):
            new, gained = slide_row(line)
            if new != line:
                moved = True
            self.bump(gained)
            self.put_line(k, i, new)
        if moved:
            self.prev = snapshot
            self.spawn()
            self.over = self.stuck()
        return True

    def undo(self):
        """직전 한 수만 되돌린다. 점수도 같이 되돌아간다(최고 기록은 그대로).

        연달아 눌러도 더 되돌아가지 않는다 — 원래 2048 규칙이 그렇다.
        """
        if self.prev is None:
            return True
        grid, self.score = self.prev
        self.grid = [row[:] for row in grid]
        self.prev = None
        self.over = False
        return True

    def stuck(self):
        for r in range(N):
            for c in range(N):
                if self.grid[r][c] == 0:
                    return False
                if c + 1 < N and self.grid[r][c] == self.grid[r][c + 1]:
                    return False
                if r + 1 < N and self.grid[r][c] == self.grid[r + 1][c]:
                    return False
        return True

    # --- 저장 ---
    def state(self):
        return {"grid": self.grid, "score": self.score, "over": self.over,
                "prev": [self.prev[0], self.prev[1]] if self.prev else None}

    def load(self, d):
        self.grid = [list(r) for r in d["grid"]]
        self.score, self.over = d["score"], d["over"]
        prev = d.get("prev")
        self.prev = ([list(r) for r in prev[0]], prev[1]) if prev else None

    # --- 그리기 ---
    def draw(self, c, x, y, w, h):
        gap = 8
        cell = int(min((w - 60) / N, h / N)) - gap
        bw = N * cell + (N - 1) * gap
        ox = x + (w - bw) / 2
        oy = y + (h - bw) / 2 - 10

        rrect(c, ox - gap, oy - gap, ox + bw + gap, oy + bw + gap, 8,
              fill=EMPTY, outline=LINE)
        best_tile = max((v for row in self.grid for v in row), default=0)
        for r in range(N):
            for col in range(N):
                v = self.grid[r][col]
                bx, by = ox + col * (cell + gap), oy + r * (cell + gap)
                fill = COLORS.get(v, BIG) if v else "#f7f9fc"
                rrect(c, bx, by, bx + cell, by + cell, 6, fill=fill, outline="")
                if v:
                    size = 19 if v < 100 else 16 if v < 1000 else 13
                    center_text(c, bx + cell / 2, by + cell / 2, str(v), size,
                                ink_on(fill))
        center_text(c, ox + bw / 2, oy + bw + 22,
                    t("가장 큰 수 %d") % best_tile, 8, DIM)
        if self.prev is not None:
            center_text(c, ox + bw / 2, oy + bw + 36,
                        t("Backspace 로 한 수 무르기"), 7, DIM)
