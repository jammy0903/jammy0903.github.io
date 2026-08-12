"""Flood It — 왼쪽 위에서 색을 번지게 해서 판 전체를 한 색으로."""
import random

from .base import DIM, Game, LINE, center_text, rrect
from .i18n import t

COLORS = ["#c9384a", "#e08a2f", "#c9a227", "#4c8f3f", "#2f6ea8", "#8155b8"]
LEVELS = 60


def tier(level):
    """(판 크기, 쓰는 색 수, 봐주는 여유 수). 뒤로 갈수록 크고 빡빡해진다."""
    n = min(20, 11 + level // 4)
    colors = min(len(COLORS), 5 + level // 25)
    slack = max(1, 5 - level // 12)
    return n, colors, slack


def blob_of(grid, n):
    """왼쪽 위와 이어진 같은 색 덩어리."""
    color = grid[0][0]
    out, stack = {(0, 0)}, [(0, 0)]
    while stack:
        r, c = stack.pop()
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < n and 0 <= nc < n and (nr, nc) not in out \
                    and grid[nr][nc] == color:
                out.add((nr, nc))
                stack.append((nr, nc))
    return out


def greedy_moves(grid, n, ncolors):
    """매번 가장 많이 먹는 색을 고르는 풀이의 수.

    허용 횟수를 이 값에 맞춰 정한다. 사람이 실제로 쓸 수 있는 전략이므로
    '이론상 불가능한 판'이 나오지 않는다.
    """
    grid = [row[:] for row in grid]
    for moves in range(n * n):
        blob = blob_of(grid, n)
        if len(blob) == n * n:
            return moves
        best, best_n = None, -1
        for col in range(ncolors):
            if col == grid[0][0]:
                continue
            trial = [row[:] for row in grid]
            for r, c in blob:
                trial[r][c] = col
            got = len(blob_of(trial, n))
            if got > best_n:
                best_n, best = got, col
        for r, c in blob:
            grid[r][c] = best
    return n * n


class FloodIt(Game):
    name = "FLOOD IT"
    help = "← → 색 고르기 · Space 칠하기 · , . 단계 넘기기"

    LEVELS = LEVELS

    def reset(self):
        """R은 '이 판 다시'다. 올라온 단계는 그대로 둔다."""
        self.level = getattr(self, "level", 0)
        self.score = getattr(self, "score", 0)
        self.load_level()

    def load_level(self):
        self.n, self.ncolors, slack = tier(self.level)
        rnd = random.Random(7717 + self.level * 3313)
        self.grid = [[rnd.randrange(self.ncolors) for _ in range(self.n)]
                     for _ in range(self.n)]
        self.limit = greedy_moves(self.grid, self.n, self.ncolors) + slack
        self.moves = 0
        self.sel = 0
        self.over = False
        self.won = False

    def next_level(self):
        self.level = (self.level + 1) % LEVELS
        self.load_level()

    def blob(self):
        return blob_of(self.grid, self.n)

    def flood(self, color):
        if self.done:
            return
        cells = self.blob()
        if color == self.grid[0][0]:
            return                          # 같은 색은 한 수를 버리는 것뿐
        for r, c in cells:
            self.grid[r][c] = color
        self.moves += 1
        if len(self.blob()) == self.n * self.n:
            self.won = True                 # 성공은 '게임 오버'가 아니다
            # 적게 쓸수록 많이 받는다
            self.bump(100 + 40 * max(0, self.limit - self.moves))
        elif self.moves >= self.limit:
            self.over = True

    @property
    def done(self):
        return self.won or self.over

    @property
    def banner(self):
        if self.won:
            return (t("성공! Enter 로 다음"), "#2f6ea8")
        if self.over:
            return (t("횟수 초과 — Enter 로 다시"), "#c9384a")
        return None

    def key(self, k):
        if self.done:
            if k in ("Return", "KP_Enter", "space"):
                if self.won:
                    self.next_level()
                else:
                    self.load_level()       # 실패하면 같은 판 다시
                return True
            return False
        if k == "Left":
            self.sel = (self.sel - 1) % self.ncolors
        elif k == "Right":
            self.sel = (self.sel + 1) % self.ncolors
        elif k in ("space", "Return", "KP_Enter", "Down", "Up"):
            self.flood(self.sel)
        else:
            return False
        return True

    # --- 저장 ---
    def state(self):
        return {"level": self.level, "grid": self.grid, "moves": self.moves,
                "sel": self.sel, "score": self.score, "over": self.over,
                "won": self.won, "limit": self.limit}

    def load(self, d):
        self.level = d["level"] % LEVELS
        self.load_level()
        saved = d["grid"]
        if len(saved) == self.n and all(len(r) == self.n for r in saved):
            self.grid = [list(r) for r in saved]
        self.moves, self.sel = d["moves"], d["sel"]
        self.limit = d.get("limit", self.limit)
        self.score, self.over, self.won = d["score"], d["over"], d["won"]

    # --- 그리기 ---
    def draw(self, c, x, y, w, h):
        N = self.n
        cell = int(min((w - 40) / N, (h - 90) / N))
        bw = cell * N
        ox = x + (w - bw) / 2
        oy = y + 12

        owned = self.blob()
        for r in range(N):
            for col in range(N):
                bx, by = ox + col * cell, oy + r * cell
                c.create_rectangle(bx, by, bx + cell, by + cell,
                                   fill=COLORS[self.grid[r][col]], outline="")
        # 이어진 덩어리 테두리를 그려서 어디까지 내 땅인지 보이게
        for r, col in owned:
            bx, by = ox + col * cell, oy + r * cell
            for dr, dc, x0, y0, x1, y1 in (
                    (-1, 0, 0, 0, cell, 0), (1, 0, 0, cell, cell, cell),
                    (0, -1, 0, 0, 0, cell), (0, 1, cell, 0, cell, cell)):
                if (r + dr, col + dc) not in owned:
                    c.create_line(bx + x0, by + y0, bx + x1, by + y1,
                                  fill="#ffffff", width=2)

        # 색 고르기 줄
        pad, size = 10, 30
        total = self.ncolors * size + (self.ncolors - 1) * pad
        px = x + (w - total) / 2
        py = oy + bw + 18
        for i, color in enumerate(COLORS[:self.ncolors]):
            bx = px + i * (size + pad)
            rrect(c, bx, py, bx + size, py + size, 5, fill=color, outline="")
            if i == self.sel:
                c.create_rectangle(bx - 4, py - 4, bx + size + 4, py + size + 4,
                                   outline="#1f2733", width=2)

        left = self.limit - self.moves
        center_text(c, x + w / 2, py + size + 16,
                    t("%d단계   %d / %d 칸   남은 횟수 %d")
                    % (self.level + 1, len(owned), N * N, left),
                    9, DIM if left > 5 else "#c9384a")

