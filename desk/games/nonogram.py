"""네모로직 — 줄 바깥의 숫자를 보고 칸을 칠한다. 500판, 점점 어려워진다.

판을 500개 저장해 두지 않고 **레벨 번호를 씨앗으로 만들어 낸다.**
같은 레벨은 언제 켜도 같은 판이 나오고, 파일도 늘지 않는다.

중요한 건 '풀리는 판'이다. 정답을 아무렇게나 만들면 힌트만 보고는
확정할 수 없는(찍어야 하는) 판이 나온다. 그래서 만들 때마다 줄 논리
풀이기를 돌려서, **줄 단위 추론만으로 끝까지 확정되는 판**만 내보낸다.
"""
import random

from .base import DIM, Game, LINE, PANEL, center_text
from .i18n import t

LEVELS = 500
FILL = "#2f3a49"
MARK = "#c4727f"        # X 표시. 반투명하게 깔아 놔도 보이도록 진한 색

# (마지막 레벨, 판 크기) — 10x10에서 시작해서 뒤로 갈수록 커진다
SIZES = [(80, 10), (180, 11), (300, 12), (400, 13),
         (470, 14), (LEVELS, 15)]

_options_cache = {}


def size_for(level):
    for last, n in SIZES:
        if level + 1 <= last:
            return n
    return SIZES[-1][1]


def clues(line):
    """[0,1,1,0,1] → [2,1]. 빈 줄은 [0]."""
    out, run = [], 0
    for v in line:
        if v == 1:
            run += 1
        elif run:
            out.append(run)
            run = 0
    if run:
        out.append(run)
    return out or [0]


def options(clue, n):
    """이 힌트로 만들 수 있는 모든 줄. (힌트, 길이)로 캐시한다."""
    key = (tuple(clue), n)
    hit = _options_cache.get(key)
    if hit is not None:
        return hit

    out = []

    def place(i, pos, line):
        if i == len(clue):
            out.append(tuple(line) + (0,) * (n - len(line)))
            return
        run = clue[i]
        last = n - (sum(clue[i:]) + len(clue) - i - 1)
        for start in range(pos, last + 1):
            new = line + [0] * (start - len(line)) + [1] * run
            if i < len(clue) - 1:
                new = new + [0]
            place(i + 1, len(new), new)

    if clue == [0]:
        out.append((0,) * n)
    else:
        place(0, 0, [])
    _options_cache[key] = out
    return out


def line_solve(row_clues, col_clues, n):
    """줄 논리만으로 풀어 본다. 끝까지 확정되면 정답, 아니면 None."""
    grid = [[-1] * n for _ in range(n)]        # -1 미정, 0 빈칸, 1 칠함

    def pass_lines(get, put, cl):
        changed = False
        for i in range(n):
            known = get(i)
            fits = [o for o in options(cl[i], n)
                    if all(k < 0 or k == v for k, v in zip(known, o))]
            if not fits:
                return None                     # 모순 — 이 판은 버린다
            merged = [fits[0][j] if all(f[j] == fits[0][j] for f in fits) else -1
                      for j in range(n)]
            if merged != list(known):
                put(i, merged)
                changed = True
        return changed

    while True:
        r = pass_lines(lambda i: grid[i],
                       lambda i, v: grid.__setitem__(i, v), row_clues)
        if r is None:
            return None
        c = pass_lines(lambda i: [grid[j][i] for j in range(n)],
                       lambda i, v: [grid[j].__setitem__(i, v[j])
                                     for j in range(n)],
                       col_clues)
        if c is None:
            return None
        if not (r or c):
            break
    return grid if all(v >= 0 for row in grid for v in row) else None


def make(level):
    """레벨 번호로 판 하나. 같은 번호면 언제나 같은 판."""
    n = size_for(level)
    rnd = random.Random(9173 + level * 7919)
    # 뒤로 갈수록 밀도를 0.5 쪽으로 — 꽉 차거나 텅 빈 줄이 줄어 힌트가 약해진다
    ramp = min(1.0, level / float(LEVELS))
    # 밀도는 뒤로 갈수록 0.5 쪽으로. 꽉 차거나 텅 빈 줄이 줄어 힌트가 약해진다.
    # (큰 판이라고 밀도를 더 낮춰 보면 오히려 논리로 안 풀리는 판이 늘어난다 —
    #  성긴 판은 줄마다 배치 경우의 수가 많아져서 확정되는 칸이 줄기 때문)
    density = 0.68 - 0.20 * ramp
    for _ in range(400):
        sol = [[1 if rnd.random() < density else 0 for _ in range(n)]
               for _ in range(n)]
        total = sum(map(sum, sol))
        if not (n <= total <= n * n - n):
            continue
        rc = [clues(r) for r in sol]
        cc = [clues([sol[r][c] for r in range(n)]) for c in range(n)]
        if line_solve(rc, cc, n) is not None:
            return sol, rc, cc
    # 여기까지 오면 밀도가 나빴던 것. 성긴 판은 거의 항상 풀린다.
    sol = [[1 if rnd.random() < 0.45 else 0 for _ in range(n)] for _ in range(n)]
    rc = [clues(r) for r in sol]
    cc = [clues([sol[r][c] for r in range(n)]) for c in range(n)]
    return sol, rc, cc


class Nonogram(Game):
    name = "NONOGRAM"
    help = "방향키 · Space 칠하기 · X 표시 · Enter 다음 판 · R 이 판 다시"

    def reset(self):
        """R은 '이 판 다시'다. 어렵게 올라온 레벨을 실수로 날리지 않게."""
        self.level = getattr(self, "level", 0)
        self.score = getattr(self, "score", 0)
        self.over = False
        self.load_level()

    def load_level(self):
        self.n = size_for(self.level)
        self.sol, self.row_clues, self.col_clues = make(self.level)
        self.grid = [[0] * self.n for _ in range(self.n)]   # 0 미정 1 칠함 2 X
        self.cr = self.cc = 0
        self.done = False

    def next_level(self):
        self.level = (self.level + 1) % LEVELS
        self.load_level()

    def key(self, k):
        n = self.n
        if k == "Left":
            self.cc = (self.cc - 1) % n
        elif k == "Right":
            self.cc = (self.cc + 1) % n
        elif k == "Up":
            self.cr = (self.cr - 1) % n
        elif k == "Down":
            self.cr = (self.cr + 1) % n
        elif k in ("Return", "KP_Enter"):
            if self.done:
                self.next_level()
        elif self.done:
            return False
        elif k == "space":
            self.grid[self.cr][self.cc] = 0 if self.grid[self.cr][self.cc] == 1 else 1
            self.check()
        elif k in ("x", "X", "f", "F"):
            self.grid[self.cr][self.cc] = 0 if self.grid[self.cr][self.cc] == 2 else 2
        else:
            return False
        return True

    def check(self):
        """칠한 칸이 정답과 똑같으면 한 판 끝. X 표시는 상관없다."""
        for r in range(self.n):
            for c in range(self.n):
                if (self.grid[r][c] == 1) != bool(self.sol[r][c]):
                    return
        self.done = True
        self.bump(self.n * self.n)          # 큰 판일수록 많이 준다

    # --- 저장 ---
    def state(self):
        return {"level": self.level, "grid": self.grid, "score": self.score,
                "cr": self.cr, "cc": self.cc, "done": self.done}

    def load(self, d):
        self.level = d["level"] % LEVELS
        self.load_level()
        saved = d["grid"]
        if len(saved) == self.n and all(len(r) == self.n for r in saved):
            self.grid = [list(r) for r in saved]
        self.score = d["score"]
        self.cr, self.cc, self.done = d["cr"], d["cc"], d["done"]
        self.over = False

    # --- 그리기 ---
    def draw(self, c, x, y, w, h):
        n = self.n
        pad = 86                                   # 힌트 자리
        cell = int(min((w - pad - 16) / n, (h - pad - 44) / n))
        fs = 8 if n <= 8 else 7 if n <= 10 else 6
        bw = cell * n
        ox = x + pad + (w - pad - bw) / 2
        oy = y + pad

        c.create_rectangle(ox, oy, ox + bw, oy + bw, fill=PANEL, outline=LINE)
        for i in range(n + 1):
            bold = i % 5 == 0
            c.create_line(ox + i * cell, oy, ox + i * cell, oy + bw,
                          fill="#9aa5b4" if bold else LINE, width=2 if bold else 1)
            c.create_line(ox, oy + i * cell, ox + bw, oy + i * cell,
                          fill="#9aa5b4" if bold else LINE, width=2 if bold else 1)

        for r in range(n):
            for col in range(n):
                v = self.grid[r][col]
                bx, by = ox + col * cell, oy + r * cell
                if v == 1:
                    c.create_rectangle(bx + 1, by + 1, bx + cell - 1, by + cell - 1,
                                       fill=FILL, outline="")
                elif v == 2:
                    m = max(3, cell // 5)
                    wide = 3 if cell >= 22 else 2
                    c.create_line(bx + m, by + m, bx + cell - m, by + cell - m,
                                  fill=MARK, width=wide, capstyle="round")
                    c.create_line(bx + cell - m, by + m, bx + m, by + cell - m,
                                  fill=MARK, width=wide, capstyle="round")

        for r, cl in enumerate(self.row_clues):
            ok = self.line_done([self.grid[r][i] for i in range(n)], cl)
            c.create_text(ox - 5, oy + r * cell + cell / 2, anchor="e",
                          text=" ".join(map(str, cl)),
                          fill=DIM if ok else "#1f2733",
                          font=("Helvetica", fs, "normal" if ok else "bold"))
        for col, cl in enumerate(self.col_clues):
            ok = self.line_done([self.grid[i][col] for i in range(n)], cl)
            c.create_text(ox + col * cell + cell / 2, oy - 4, anchor="s",
                          text="\n".join(map(str, cl)), justify="center",
                          fill=DIM if ok else "#1f2733",
                          font=("Helvetica", fs, "normal" if ok else "bold"))

        bx, by = ox + self.cc * cell, oy + self.cr * cell
        c.create_rectangle(bx - 1, by - 1, bx + cell + 1, by + cell + 1,
                           outline="#2f6ea8", width=2)

        center_text(c, x + w / 2, oy + bw + 24,
                    t("%d / %d 판   %dx%d") % (self.level + 1, LEVELS, n, n),
                    9, DIM)
        if self.done:
            center_text(c, x + w / 2, oy + bw / 2, t("완성! Enter 로 다음 판"), 13,
                        "#2f6ea8")

    @staticmethod
    def line_done(line, cl):
        return clues([1 if v == 1 else 0 for v in line]) == cl
