"""뿌요뿌요 — 같은 색 4개가 붙으면 터지고, 위에서 내려앉아 연쇄된다."""
import random

from .base import EMPTY, Game, LINE, PANEL, center_text
from .i18n import t

COLS, ROWS = 6, 12
COLORS = ["#c9384a", "#4c8f3f", "#2f6ea8", "#c9a227", "#8155b8"]
NEED = 4                                   # 몇 개 붙어야 터지나
CHAIN = [0, 8, 16, 32, 64, 96, 128, 160, 192, 224, 256]   # 연쇄 배수
# 회전 방향: 0=위 1=오른쪽 2=아래 3=왼쪽
OFF = [(-1, 0), (0, 1), (1, 0), (0, -1)]


class Puyo(Game):
    name = "PUYO"
    help = "← → 이동 · ↑ 회전 · Z 반시계 · ↓ 내리기 · Space 떨구기"

    def reset(self):
        self.grid = [[None] * COLS for _ in range(ROWS)]
        self.score = 0
        self.over = False
        self.fall = 0.0
        self.chain = 0                     # 마지막 연쇄 수(화면 표시용)
        self.popped = 0                    # 지금까지 터뜨린 뿌요 수
        self.next_pair = self.roll()
        self.spawn()

    def roll(self):
        return [random.randrange(len(COLORS)), random.randrange(len(COLORS))]

    def spawn(self):
        self.pair = self.next_pair
        self.next_pair = self.roll()
        self.pr, self.pc, self.rot = 0, COLS // 2, 0
        if self.grid[0][self.pc] is not None:
            self.over = True

    def cells(self, pr=None, pc=None, rot=None):
        """(축 뿌요, 자식 뿌요) 좌표. 자식은 판 위로 나갈 수 있다."""
        pr = self.pr if pr is None else pr
        pc = self.pc if pc is None else pc
        rot = self.rot if rot is None else rot
        dr, dc = OFF[rot]
        return [(pr, pc), (pr + dr, pc + dc)]

    def blocked(self, pr, pc, rot):
        for r, c in self.cells(pr, pc, rot):
            if c < 0 or c >= COLS or r >= ROWS:
                return True
            if r >= 0 and self.grid[r][c] is not None:
                return True
        return False

    # --- 조작 ---
    def key(self, k):
        if self.over:
            return False
        if k == "Left":
            if not self.blocked(self.pr, self.pc - 1, self.rot):
                self.pc -= 1
        elif k == "Right":
            if not self.blocked(self.pr, self.pc + 1, self.rot):
                self.pc += 1
        elif k in ("Up", "z", "Z"):
            rot = (self.rot + (1 if k == "Up" else 3)) % 4
            for dc in (0, -1, 1):          # 벽에 붙어 있으면 한 칸 밀어 준다
                if not self.blocked(self.pr, self.pc + dc, rot):
                    self.rot, self.pc = rot, self.pc + dc
                    break
        elif k == "Down":
            if not self.blocked(self.pr + 1, self.pc, self.rot):
                self.pr += 1
                self.fall = 0.0
                self.bump(1)
        elif k == "space":
            while not self.blocked(self.pr + 1, self.pc, self.rot):
                self.pr += 1
            self.lock()
        else:
            return False
        return True

    # --- 놓기 · 연쇄 ---
    def lock(self):
        for (r, c), color in zip(self.cells(), self.pair):
            if r < 0:
                self.over = True
                return
            self.grid[r][c] = color
        self.resolve()
        if not self.over:
            self.spawn()

    def settle(self):
        """빈칸 위에 뜬 뿌요를 바닥으로 내린다."""
        for c in range(COLS):
            col = [self.grid[r][c] for r in range(ROWS) if self.grid[r][c] is not None]
            for r in range(ROWS):
                i = r - (ROWS - len(col))
                self.grid[r][c] = col[i] if i >= 0 else None

    def group(self, r, c, seen):
        color = self.grid[r][c]
        out, stack = {(r, c)}, [(r, c)]
        while stack:
            cr, cc = stack.pop()
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nr, nc = cr + dr, cc + dc
                if 0 <= nr < ROWS and 0 <= nc < COLS and (nr, nc) not in out \
                        and self.grid[nr][nc] == color:
                    out.add((nr, nc))
                    stack.append((nr, nc))
        seen |= out
        return out

    def resolve(self):
        """터뜨리고 내려앉기를 더 이상 터질 게 없을 때까지."""
        chain = 0
        while True:
            self.settle()
            seen, popped = set(), []
            for r in range(ROWS):
                for c in range(COLS):
                    if self.grid[r][c] is None or (r, c) in seen:
                        continue
                    g = self.group(r, c, seen)
                    if len(g) >= NEED:
                        popped.append(g)
            if not popped:
                break
            chain += 1
            count = sum(len(g) for g in popped)
            self.popped += count
            mult = CHAIN[min(chain, len(CHAIN) - 1)]
            self.bump(count * 10 * max(1, mult) // 8)
            for g in popped:
                for r, c in g:
                    self.grid[r][c] = None
        self.chain = chain

    # --- 시간 ---
    @property
    def level(self):
        """24개 터뜨릴 때마다 한 단계. 색이 5개라 4개 붙이기가 만만치 않다."""
        return self.popped // 24 + 1

    @property
    def interval(self):
        return max(0.10, 0.55 - 0.03 * (self.level - 1))

    def tick(self, dt):
        if self.over:
            return False
        self.fall += dt
        if self.fall < self.interval:
            return False
        self.fall = 0.0
        if self.blocked(self.pr + 1, self.pc, self.rot):
            self.lock()
        else:
            self.pr += 1
        return True

    # --- 저장 ---
    def state(self):
        return {"grid": self.grid, "score": self.score, "pair": self.pair,
                "next": self.next_pair, "pr": self.pr, "pc": self.pc,
                "rot": self.rot, "chain": self.chain, "over": self.over,
                "popped": self.popped}

    def load(self, d):
        self.grid = [list(r) for r in d["grid"]]
        self.score, self.pair, self.next_pair = d["score"], d["pair"], d["next"]
        self.pr, self.pc, self.rot = d["pr"], d["pc"], d["rot"]
        self.chain, self.over = d["chain"], d["over"]
        self.popped = d.get("popped", 0)

    # --- 그리기 ---
    def draw(self, c, x, y, w, h):
        side = 46
        cell = int(min((w - side) / COLS, h / ROWS))
        bw, bh = cell * COLS, cell * ROWS
        ox = x + (w - side - bw) / 2
        oy = y + (h - bh) / 2

        c.create_rectangle(ox - 2, oy - 2, ox + bw + 2, oy + bh + 2,
                           outline=LINE, fill=PANEL)
        for i in range(1, COLS):
            c.create_line(ox + i * cell, oy, ox + i * cell, oy + bh, fill=EMPTY)

        def blob(r, col, color, ghost=False):
            if r < 0:
                return
            bx, by = ox + col * cell, oy + r * cell
            c.create_oval(bx + 2, by + 2, bx + cell - 2, by + cell - 2,
                          fill="" if ghost else COLORS[color],
                          outline="#b6c0ce" if ghost else "")

        for r in range(ROWS):
            for col in range(COLS):
                if self.grid[r][col] is not None:
                    blob(r, col, self.grid[r][col])

        if not self.over:
            gr = self.pr
            while not self.blocked(gr + 1, self.pc, self.rot):
                gr += 1
            for r, col in self.cells(pr=gr):
                blob(r, col, 0, ghost=True)
            for (r, col), color in zip(self.cells(), self.pair):
                blob(r, col, color)

        px = ox + bw + 12
        center_text(c, px + 16, oy + 8, "NEXT", 7)
        for i, color in enumerate(self.next_pair):
            cy = oy + 26 + (1 - i) * 16     # 자식이 위
            c.create_oval(px + 8, cy, px + 24, cy + 14, fill=COLORS[color], outline="")
        center_text(c, px + 16, oy + 72, "LEVEL", 7)
        center_text(c, px + 16, oy + 86, str(self.level), 12)
        if self.chain > 1:
            center_text(c, px + 16, oy + 112, t("%d연쇄") % self.chain, 9)
