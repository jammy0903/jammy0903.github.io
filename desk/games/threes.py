"""Threes! — 1+2=3, 그 뒤로는 같은 수끼리."""
import random

from .base import DIM, EMPTY, Game, LINE, center_text, rrect

N = 4
TILE = "#ffffff"            # 3 이상은 전부 흰 타일 + 검은 숫자
COLORS = {1: "#2f6ea8", 2: "#c9384a"}
ON_COLOR = "#ffffff"        # 1·2 타일 위 글자
ON_TILE = "#1f2733"         # 흰 타일 위 글자


def merged(a, b):
    """b가 a 위로 합쳐진 결과. 못 합치면 None."""
    if a == 0:
        return b
    if (a == 1 and b == 2) or (a == 2 and b == 1):
        return 3
    if a == b and a >= 3:
        return a + b
    return None


def tile_score(v):
    """3, 6, 12 … 은 3^(단계). 1과 2는 0점."""
    if v < 3:
        return 0
    step = 1
    x = 3
    while x < v:
        x *= 2
        step += 1
    return 3 ** step


def slide_line(line):
    """한 줄을 앞쪽(index 0)으로 한 칸씩. (새 줄, 움직였는가)."""
    out = list(line)
    moved = False
    for i in range(1, N):
        if out[i] == 0:
            continue
        m = merged(out[i - 1], out[i])
        if m is None:
            continue
        # 빈칸으로 미는 건 언제나 가능, 합치기는 이번 이동에서 한 번씩만
        out[i - 1] = m
        out[i] = 0
        moved = True
    return out, moved


class Threes(Game):
    name = "THREES!"
    help = "방향키로 한 칸씩 · 1+2=3 · 3부터는 같은 수끼리"

    def reset(self):
        self.grid = [[0] * N for _ in range(N)]
        self.deck = []
        self.score = 0
        self.over = False
        self.next_val = self.pull()
        spots = random.sample([(r, c) for r in range(N) for c in range(N)], 9)
        for r, c in spots:
            self.grid[r][c] = self.pull()

    def pull(self):
        if not self.deck:
            self.deck = [1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3]
            random.shuffle(self.deck)
        return self.deck.pop()

    # --- 이동 ---
    def lines(self, d):
        """이동 방향 기준으로 '앞쪽이 index 0'이 되도록 줄을 뽑는다."""
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
        if self.over or k not in ("Left", "Right", "Up", "Down"):
            return False
        moved_lines = []
        for i, line in enumerate(self.lines(k)):
            new, moved = slide_line(line)
            self.put_line(k, i, new)
            if moved:
                moved_lines.append(i)
        if not moved_lines:
            return True
        i = random.choice(moved_lines)
        line = self.lines(k)[i]      # 새 타일은 들어온 쪽(뒤쪽) 끝에
        line[N - 1] = self.next_val
        self.put_line(k, i, line)
        self.next_val = self.pull()
        self.rescore()
        if not self.any_move():
            self.over = True
        return True

    def rescore(self):
        self.score = sum(tile_score(v) for row in self.grid for v in row)
        if self.score > self.best:
            self.best = self.score

    def any_move(self):
        for r in range(N):
            for c in range(N):
                v = self.grid[r][c]
                if v == 0:
                    return True
                if c + 1 < N and merged(v, self.grid[r][c + 1]) is not None:
                    return True
                if r + 1 < N and merged(v, self.grid[r + 1][c]) is not None:
                    return True
        return False

    # --- 저장 ---
    def state(self):
        return {"grid": self.grid, "score": self.score, "next": self.next_val,
                "deck": self.deck, "over": self.over}

    def load(self, d):
        self.grid = [list(r) for r in d["grid"]]
        self.score, self.next_val = d["score"], d["next"]
        self.deck, self.over = list(d["deck"]), d["over"]

    # --- 그리기 ---
    def draw(self, c, x, y, w, h):
        side = 40
        cell = int(min((w - side) / N, h / N)) - 8
        gap = 8
        bw = N * cell + (N - 1) * gap
        ox = x + (w - side - bw) / 2
        oy = y + (h - bw) / 2

        for r in range(N):
            for col in range(N):
                v = self.grid[r][col]
                bx, by = ox + col * (cell + gap), oy + r * (cell + gap)
                fill = COLORS.get(v, TILE) if v else EMPTY
                rrect(c, bx, by, bx + cell, by + cell, 6, fill=fill,
                      outline=LINE if v > 2 else "")
                if v:
                    ink = ON_COLOR if v <= 2 else ON_TILE
                    size = 17 if v < 100 else 13
                    center_text(c, bx + cell / 2, by + cell / 2, str(v), size, ink)

        px = ox + bw + 14
        center_text(c, px + 14, oy + 8, "NEXT", 7, DIM)
        v = self.next_val
        rrect(c, px, oy + 20, px + 28, oy + 48, 5,
              fill=COLORS.get(v, TILE), outline=LINE)
        center_text(c, px + 14, oy + 34, str(v), 12,
                    ON_COLOR if v <= 2 else ON_TILE)
