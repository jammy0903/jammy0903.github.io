"""수박게임 — 같은 과일 둘이 닿으면 다음 과일로. Verlet 물리."""
import math
import random

from .base import DIM, Game, LINE, PANEL, center_text

WW, WH = 250.0, 330.0          # 통 안쪽 크기(월드 좌표)
DANGER = 34.0                  # 이 선 위에 과일이 얹혀 있으면 위험
GRAVITY = 900.0
SUB_DT = 1.0 / 120.0
SUBSTEPS = 4
RELAX = 4
DAMP = 0.995
DROP_DELAY = 0.30
OVER_DELAY = 1.6

R = [9, 12, 15, 19, 24, 29, 35, 41, 48, 56, 65]
COLORS = ["#c94f4f", "#d97b3f", "#c9a227", "#d6d24a", "#8fc44a", "#4caf6a",
          "#3fb6a8", "#3f8fd6", "#7a63d6", "#c24fa8", "#3f9f4a"]
POINTS = [1, 3, 6, 10, 15, 21, 28, 36, 45, 55, 66]
DROPPABLE = 5                  # 0~4 티어만 떨어뜨린다
TOP = len(R) - 1


class Suika(Game):
    name = "SUIKA"
    help = "← → 위치 · Space 떨어뜨리기"

    def reset(self):
        self.balls = []
        self.score = 0
        self.over = False
        self.dx = WW / 2
        self.cool = 0.0
        self.danger_t = 0.0
        self.cur = random.randrange(DROPPABLE)
        self.next_t = random.randrange(DROPPABLE)

    # --- 조작 ---
    def key(self, k):
        if self.over:
            return False
        r = R[self.cur]
        if k == "Left":
            self.dx = max(r, self.dx - 12)
        elif k == "Right":
            self.dx = min(WW - r, self.dx + 12)
        elif k == "space":
            if self.cool > 0:
                return True
            self.balls.append({"x": self.dx, "y": r + 2, "px": self.dx,
                               "py": r + 2, "t": self.cur})
            self.cool = DROP_DELAY
            self.cur, self.next_t = self.next_t, random.randrange(DROPPABLE)
            self.dx = min(max(self.dx, R[self.cur]), WW - R[self.cur])
        else:
            return False
        return True

    # --- 물리 ---
    def tick(self, dt):
        if self.over:
            return False
        self.cool = max(0.0, self.cool - dt)
        for _ in range(SUBSTEPS):
            self.integrate()
            for _ in range(RELAX):
                self.solve()
        self.merge()
        self.check_over(dt)
        return True

    def integrate(self):
        for b in self.balls:
            vx = (b["x"] - b["px"]) * DAMP
            vy = (b["y"] - b["py"]) * DAMP
            b["px"], b["py"] = b["x"], b["y"]
            b["x"] += vx
            b["y"] += vy + GRAVITY * SUB_DT * SUB_DT

    def solve(self):
        bs = self.balls
        for i in range(len(bs)):
            a = bs[i]
            ra = R[a["t"]]
            for j in range(i + 1, len(bs)):
                b = bs[j]
                rb = R[b["t"]]
                dx = b["x"] - a["x"]
                dy = b["y"] - a["y"]
                d2 = dx * dx + dy * dy
                lim = ra + rb
                if d2 >= lim * lim or d2 == 0:
                    continue
                d = math.sqrt(d2)
                push = (lim - d) * 0.5
                nx, ny = dx / d, dy / d
                # 위치만 밀어낸다. Verlet에서는 이전 위치를 그대로 두는 것이
                # 곧 속도 보정이 되어, 쌓인 과일이 저절로 멈춘다.
                for k, sign in ((a, -1), (b, 1)):
                    k["x"] += sign * nx * push
                    k["y"] += sign * ny * push
            # 벽·바닥: 부딪힌 축의 속도를 없앤다(이전 위치 = 새 위치).
            # 위치만 되돌리면 중력이 만든 속도가 끝없이 쌓인다.
            for axis, prev, lo, hi in (("x", "px", ra, WW - ra),
                                       ("y", "py", -1e9, WH - ra)):
                v = min(max(a[axis], lo), hi)
                if v != a[axis]:
                    a[axis] = a[prev] = v

    def merge(self):
        bs = self.balls
        for i in range(len(bs)):
            a = bs[i]
            for j in range(i + 1, len(bs)):
                b = bs[j]
                if a["t"] != b["t"] or a["t"] == TOP:
                    continue
                # 충돌 해소 뒤라 정확히 접해 있으므로 여유를 조금 준다
                lim = R[a["t"]] * 2 + 1.5
                dx, dy = b["x"] - a["x"], b["y"] - a["y"]
                if dx * dx + dy * dy > lim * lim:
                    continue
                t = a["t"] + 1
                x, y = (a["x"] + b["x"]) / 2, (a["y"] + b["y"]) / 2
                self.balls = [z for k, z in enumerate(bs) if k not in (i, j)]
                self.balls.append({"x": x, "y": y, "px": x, "py": y, "t": t})
                self.bump(POINTS[t])
                return            # 한 프레임에 한 쌍씩

    def check_over(self, dt):
        risky = False
        for b in self.balls:
            speed = abs(b["x"] - b["px"]) + abs(b["y"] - b["py"])
            if b["y"] - R[b["t"]] < DANGER and speed < 0.35:
                risky = True
                break
        self.danger_t = self.danger_t + dt if risky else 0.0
        if self.danger_t > OVER_DELAY:
            self.over = True

    # --- 저장 ---
    def state(self):
        return {"balls": self.balls, "score": self.score, "cur": self.cur,
                "next": self.next_t, "dx": self.dx, "over": self.over}

    def load(self, d):
        self.balls = [dict(b) for b in d["balls"]]
        self.score, self.cur, self.next_t = d["score"], d["cur"], d["next"]
        self.dx, self.over = d["dx"], d["over"]

    # --- 그리기 ---
    def draw(self, c, x, y, w, h):
        side = 40
        s = min((w - side) / WW, h / WH)
        ox = x + (w - side - WW * s) / 2
        oy = y + (h - WH * s) / 2

        def px(wx, wy):
            return ox + wx * s, oy + wy * s

        c.create_rectangle(ox, oy, ox + WW * s, oy + WH * s,
                           outline="#b6c0ce", fill=PANEL)
        dy0 = oy + DANGER * s
        c.create_line(ox, dy0, ox + WW * s, dy0,
                      fill="#c9384a" if self.danger_t > 0.4 else LINE, dash=(3, 4))

        for b in self.balls:
            r = R[b["t"]] * s
            bx, by = px(b["x"], b["y"])
            c.create_oval(bx - r, by - r, bx + r, by + r,
                          fill=COLORS[b["t"]], outline="")

        if not self.over:
            r = R[self.cur] * s
            bx, _ = px(self.dx, 0)
            c.create_line(bx, oy, bx, oy + WH * s, fill=LINE)
            c.create_oval(bx - r, oy - r + 2, bx + r, oy + r + 2,
                          outline=COLORS[self.cur], width=2)

        nx = ox + WW * s + 14
        center_text(c, nx + 14, oy + 8, "NEXT", 7, DIM)
        r = R[self.next_t] * s
        c.create_oval(nx + 14 - r, oy + 34 - r, nx + 14 + r, oy + 34 + r,
                      fill=COLORS[self.next_t], outline="")
