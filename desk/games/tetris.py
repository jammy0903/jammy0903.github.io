"""테트리스."""
import random

from .base import DIM, EMPTY, Game, LINE, PANEL, center_text, rrect
from .i18n import t

COLS, ROWS = 10, 20

# 각 조각: (한 변 N, 셀 좌표, 색)
PIECES = {
    "I": (4, [(1, 0), (1, 1), (1, 2), (1, 3)], "#3fb6d6"),
    "O": (2, [(0, 0), (0, 1), (1, 0), (1, 1)], "#c9a227"),
    "T": (3, [(0, 1), (1, 0), (1, 1), (1, 2)], "#9152c4"),
    "S": (3, [(0, 1), (0, 2), (1, 0), (1, 1)], "#4caf6a"),
    "Z": (3, [(0, 0), (0, 1), (1, 1), (1, 2)], "#c9484f"),
    "J": (3, [(0, 0), (1, 0), (1, 1), (1, 2)], "#4569c4"),
    "L": (3, [(0, 2), (1, 0), (1, 1), (1, 2)], "#c9783a"),
}
ORDER = list(PIECES)
CLEAR_SCORE = {1: 100, 2: 300, 3: 500, 4: 800}
KICKS = (0, -1, 1, -2, 2)


def rotate(cells, n):
    """N x N 박스 안에서 시계방향 90도."""
    return [(c, n - 1 - r) for r, c in cells]


class Tetris(Game):
    name = "TETRIS"
    help = "← → 이동 · ↑ 회전 · ↓ 소프트드롭 · Space 하드드롭"

    def reset(self):
        self.grid = [[None] * COLS for _ in range(ROWS)]
        self.bag = []
        self.score = 0
        self.lines = 0
        self.over = False
        self.fall = 0.0
        self.next_key = self.pull()
        self.spawn()

    # --- 조각 ---
    def pull(self):
        if not self.bag:
            self.bag = ORDER[:]
            random.shuffle(self.bag)
        return self.bag.pop()

    def spawn(self):
        self.key_id = self.next_key
        self.next_key = self.pull()
        n, cells, _ = PIECES[self.key_id]
        self.n = n
        self.cells = list(cells)
        self.pr = -1 if self.key_id == "I" else 0
        self.pc = (COLS - n) // 2
        if self.collides(self.cells, self.pr, self.pc):
            self.over = True

    def blocks(self, cells=None, pr=None, pc=None):
        cells = self.cells if cells is None else cells
        pr = self.pr if pr is None else pr
        pc = self.pc if pc is None else pc
        return [(pr + r, pc + c) for r, c in cells]

    def collides(self, cells, pr, pc):
        for r, c in self.blocks(cells, pr, pc):
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
            return self.shift(-1)
        if k == "Right":
            return self.shift(1)
        if k == "Down":
            if self.step_down():
                self.fall = 0.0
                self.bump(1)
            return True
        if k == "Up":
            return self.spin()
        if k == "space":
            dropped = 0
            while self.step_down():
                dropped += 1
            self.bump(dropped * 2)
            self.lock()
            return True
        return False

    def shift(self, d):
        if not self.collides(self.cells, self.pr, self.pc + d):
            self.pc += d
        return True

    def spin(self):
        turned = rotate(self.cells, self.n)
        for dx in KICKS:
            if not self.collides(turned, self.pr, self.pc + dx):
                self.cells, self.pc = turned, self.pc + dx
                break
        return True

    def step_down(self):
        """한 칸 내려가면 True, 바닥이면 False."""
        if self.collides(self.cells, self.pr + 1, self.pc):
            return False
        self.pr += 1
        return True

    def lock(self):
        for r, c in self.blocks():
            if r < 0:
                self.over = True
                return
            self.grid[r][c] = PIECES[self.key_id][2]
        kept = [row for row in self.grid if any(v is None for v in row)]
        cleared = ROWS - len(kept)
        if cleared:
            self.lines += cleared
            self.bump(CLEAR_SCORE[cleared] * self.level)
            self.grid = [[None] * COLS for _ in range(cleared)] + kept
        self.spawn()

    # --- 시간 ---
    @property
    def level(self):
        """10줄마다 한 단계. 올라갈수록 빨리 떨어지고 점수 배수가 커진다."""
        return self.lines // 10 + 1

    @property
    def interval(self):
        return max(0.08, 0.80 - 0.07 * (self.level - 1))

    def tick(self, dt):
        if self.over:
            return False
        self.fall += dt
        if self.fall < self.interval:
            return False
        self.fall = 0.0
        if not self.step_down():
            self.lock()
        return True

    # --- 저장 ---
    def state(self):
        return {"grid": self.grid, "score": self.score, "lines": self.lines,
                "key": self.key_id, "next": self.next_key, "cells": self.cells,
                "n": self.n, "pr": self.pr, "pc": self.pc, "over": self.over}

    def load(self, d):
        self.grid = [list(row) for row in d["grid"]]
        self.score, self.lines = d["score"], d["lines"]
        self.key_id, self.next_key = d["key"], d["next"]
        self.cells = [tuple(x) for x in d["cells"]]
        self.n, self.pr, self.pc = d["n"], d["pr"], d["pc"]
        self.over = d["over"]

    # --- 그리기 ---
    def draw(self, c, x, y, w, h):
        preview = 46
        cell = int(min((w - preview) / COLS, h / ROWS))
        bw, bh = cell * COLS, cell * ROWS
        ox = x + (w - preview - bw) / 2
        oy = y + (h - bh) / 2

        c.create_rectangle(ox - 2, oy - 2, ox + bw + 2, oy + bh + 2,
                           outline=LINE, fill=PANEL)
        for i in range(1, COLS):
            c.create_line(ox + i * cell, oy, ox + i * cell, oy + bh, fill=EMPTY)

        def block(r, col, color):
            if r < 0:
                return
            bx, by = ox + col * cell, oy + r * cell
            rrect(c, bx + 1, by + 1, bx + cell - 1, by + cell - 1, 3,
                  fill=color, outline="")

        for r in range(ROWS):
            for col in range(COLS):
                if self.grid[r][col]:
                    block(r, col, self.grid[r][col])

        if not self.over:
            # 착지 위치 미리보기
            gr = self.pr
            while not self.collides(self.cells, gr + 1, self.pc):
                gr += 1
            for r, col in self.blocks(pr=gr):
                if r >= 0:
                    bx, by = ox + col * cell, oy + r * cell
                    c.create_rectangle(bx + 2, by + 2, bx + cell - 2, by + cell - 2,
                                       outline="#b6c0ce")
            color = PIECES[self.key_id][2]
            for r, col in self.blocks():
                block(r, col, color)

        # 다음 조각
        px = ox + bw + 12
        center_text(c, px + 16, oy + 8, "NEXT", 7, DIM)
        n, cells, color = PIECES[self.next_key]
        s = 9
        for r, col in cells:
            bx, by = px + 16 - n * s / 2 + col * s, oy + 22 + r * s
            rrect(c, bx + 1, by + 1, bx + s - 1, by + s - 1, 2, fill=color, outline="")
        center_text(c, px + 16, oy + 74, "LEVEL", 7, DIM)
        center_text(c, px + 16, oy + 88, str(self.level), 12)
        center_text(c, px + 16, oy + 110, "LINES", 7, DIM)
        center_text(c, px + 16, oy + 124, str(self.lines), 11)
