#!/usr/bin/env python3
"""항상 위에 뜨는 반투명 게임 창. 표준 라이브러리(tkinter)만 사용.

  L            한국어 / English 전환
  M            게임 고르기 (↑↓ + Enter). 처음 켜면 이 화면부터
  1 ~ 9        게임 바로 가기
  , .          레벨 있는 게임에서 판 넘기기 (PageUp/PageDown 은 10판씩)
  [ ]          흐리게 / 진하게 (메뉴 화면의 바를 마우스로 끌어도 된다)
  ESC          작업표시줄로 내리기 (프로그램은 계속 돈다)
  F8           작업표시줄에서 다시 꺼내기 (윈도우 전역 단축키)
               이미 쓰는 프로그램이 있으면 빈 키를 자동으로 찾는다
  H            투명도만 0으로. 한 번 더 누르면 복귀
  R            지금 게임만 새로 시작
  Ctrl+Q       종료 (창 닫기 버튼도 종료)

복귀 단축키는 hotkey.py의 HOTKEY 한 줄로 바꿀 수 있다.

ESC로 내려도 판·점수·최고점은 그대로 남는다. 끄는 건 Ctrl+Q 또는 창 닫기 버튼.
"""
import json
import os
import sys
import tkinter as tk

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from games import (floodit, g2048, nonogram, puyo, sokoban, suika,     # noqa: E402
                   tetris, threes, tripletown)
from games.base import ACCENT, BG, DIM, FONT, INK, LINE, PANEL  # noqa: E402
from games.i18n import t                                     # noqa: E402
from games import i18n                                       # noqa: E402
from games.base import rrect                                 # noqa: E402
import hotkey                                                # noqa: E402
from hotkey import GlobalHotkey                              # noqa: E402

SAVE = os.path.join(os.path.expanduser("~"), ".deskgames.json")
W, H = 400, 520
BAR = 26
FPS_MS = 33
AUTOSAVE_MS = 10000
ALPHA_MIN, ALPHA_MAX = 0.15, 1.0

# 메뉴 화면의 투명도 바 위치
BAR_X0, BAR_X1 = 56, W - 56
BAR_Y = BAR + 74
BAR_GRAB = 14                 # 이 정도 세로 범위 안을 누르면 바를 잡은 것


class Shell:
    def __init__(self):
        self.games = [tetris.Tetris(), suika.Suika(), puyo.Puyo(),
                      g2048.G2048(), threes.Threes(), tripletown.TripleTown(),
                      nonogram.Nonogram(), floodit.FloodIt(), sokoban.Sokoban()]
        self.idx = 0
        self.menu = True          # 처음 켜면 고르는 화면부터
        self.pick = 0
        self.alpha = 0.55
        self.faded = False
        self.stashed = False        # 작업표시줄로 내려가 있나
        self.lang = "ko"
        self.load()
        i18n.set_lang(self.lang)

        self.root = tk.Tk()
        self.root.title("desk")
        self.root.resizable(False, False)
        self.root.configure(bg=BG)
        self.canvas = tk.Canvas(self.root, width=W, height=H, bg=BG,
                                highlightthickness=0)
        self.canvas.pack()

        self.apply_alpha()
        sw = self.root.winfo_screenwidth()
        self.root.geometry("%dx%d+%d+%d" % (W, H, max(0, sw - W - 60), 80))

        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<Button-3>", lambda e: self.on_click(e, button=3))
        self.canvas.bind("<B3-Motion>", lambda e: self.on_drag(e, button=3))
        self.root.bind("<Key>", self.on_key)
        self.root.bind("<Control-q>", lambda e: self.quit())
        # 창 상태는 직접 추적한다. root.state() 는 환경에 따라 내려가 있어도
        # "normal" 을 돌려줘서, 그것만 믿으면 숨긴 채로 게임이 계속 돌아간다.
        self.root.bind("<Unmap>", self.on_unmap)
        self.root.bind("<Map>", self.on_map)
        self.root.protocol("WM_DELETE_WINDOW", self.quit)

        # 작업표시줄로 내려가 있는 동안에는 창이 키를 못 받으므로 전역 단축키가 필요하다
        self.hotkey = GlobalHotkey(self.restore)
        self.hotkey.start()

        self.root.after(FPS_MS, self.loop)
        self.root.after(AUTOSAVE_MS, self.autosave)

    @property
    def paused(self):
        """화면에서 안 보이는 동안에는 시간이 흐르지 않는다."""
        return self.faded or self.stashed

    @property
    def game(self):
        return self.games[self.idx]

    def apply_alpha(self):
        self.root.attributes("-alpha", 0.0 if self.faded else self.alpha)

    # --- 내리기 / 꺼내기 ---
    def stash(self):
        """작업표시줄로. 프로그램은 계속 돌고 판은 그 자리에 멈춘다."""
        self.save()
        self.faded = False
        self.stashed = True
        self.apply_alpha()
        self.root.iconify()

    def restore(self):
        self.faded = False
        self.stashed = False
        self.apply_alpha()
        self.root.deiconify()
        self.root.lift()
        try:
            self.root.focus_force()
        except tk.TclError:
            pass

    def on_unmap(self, e):
        """작업표시줄 단추로 내려도 여기로 온다. 저장하고 게임을 멈춘다."""
        if e.widget is self.root:
            self.stashed = True
            self.save()

    def on_map(self, e):
        if e.widget is self.root:
            self.stashed = False

    # --- 저장 ---
    def load(self):
        try:
            with open(SAVE) as f:
                d = json.load(f)
        except (OSError, ValueError):
            return
        self.alpha = d.get("alpha", self.alpha)
        self.lang = d.get("lang", self.lang)
        self.idx = self.pick = d.get("idx", 0) % len(self.games)
        for g in self.games:
            saved = d.get("games", {}).get(g.name)
            if not saved:
                continue
            g.best = saved.get("best", 0)
            if saved.get("state"):
                try:
                    g.load(saved["state"])
                except Exception:
                    g.reset()
            # 저장 직전에 갱신되지 못한 점수가 있어도 최고 기록은 잃지 않는다
            g.best = max(g.best, g.score)

    def save(self):
        data = {"alpha": self.alpha, "idx": self.idx, "lang": self.lang,
                "games": {}}
        for g in self.games:
            g.best = max(g.best, g.score)
            data["games"][g.name] = {"best": g.best, "state": g.state()}
        tmp = SAVE + ".tmp"
        try:
            with open(tmp, "w") as f:
                json.dump(data, f)
            os.replace(tmp, SAVE)      # 쓰다 죽어도 기존 기록이 깨지지 않게
        except OSError:
            pass

    def autosave(self):
        self.save()
        self.root.after(AUTOSAVE_MS, self.autosave)

    # --- 게임 고르기 ---
    def choose(self, i):
        self.idx = i % len(self.games)
        self.menu = False
        self.save()

    def menu_key(self, k):
        if k in ("Up", "Left"):
            self.pick = (self.pick - 1) % len(self.games)
        elif k in ("Down", "Right"):
            self.pick = (self.pick + 1) % len(self.games)
        elif k in ("Return", "KP_Enter", "space"):
            self.choose(self.pick)
        elif k.isdigit() and 1 <= int(k) <= len(self.games):
            self.choose(int(k) - 1)

    def draw_menu(self, c):
        c.create_rectangle(0, BAR, W, H, fill=PANEL, outline="")
        c.create_text(W / 2, BAR + 30, text=t("게임 고르기"), fill=INK,
                      font=(FONT, 15, "bold"))
        c.create_text(W / 2, BAR + 50, fill=DIM, font=(FONT, 8),
                      text=t("↑ ↓ 로 고르고 Enter · 숫자키로 바로 · M 닫기"))
        note = self.hotkey.error or (t("%s 로 작업표시줄에서 꺼낸다")
                                     % hotkey.label(self.hotkey.spec))
        c.create_text(W / 2, H - 26, fill=DIM if self.hotkey.active else "#c9384a",
                      font=(FONT, 7), text=note)

        self.draw_slider(c)

        top = BAR + 100
        row = (H - 26 - top) / len(self.games)
        for i, g in enumerate(self.games):
            y = top + i * row
            on = i == self.pick
            rrect(c, 22, y, W - 22, y + row - 4, 6,
                  fill="#e8f0fa" if on else BG,
                  outline=ACCENT if on else LINE, width=2 if on else 1)
            mid = y + (row - 4) / 2
            c.create_text(40, mid, text=str(i + 1), fill=DIM,
                          font=(FONT, 9, "bold"))
            c.create_text(58, mid, text=g.name, anchor="w",
                          fill=ACCENT if on else INK, font=(FONT, 11, "bold"))
            note = t("게임 오버") if g.over else \
                   (t("진행 중 %d점") % g.score if g.score else t("새 판"))
            c.create_text(W - 34, mid, anchor="e", fill=DIM, font=(FONT, 8),
                          text="%s   best %d" % (note, g.best))

    def draw_slider(self, c):
        """투명도 바. 마우스로 끌거나 [ ] 로도 움직인다."""
        y = BAR_Y
        span = BAR_X1 - BAR_X0
        frac = (self.alpha - ALPHA_MIN) / (ALPHA_MAX - ALPHA_MIN)
        kx = BAR_X0 + span * frac

        c.create_text(BAR_X0, y - 15, anchor="w", fill=DIM, font=(FONT, 7),
                      text=t("투명도"))
        c.create_text(BAR_X1, y - 15, anchor="e", fill=INK, font=(FONT, 8, "bold"),
                      text="%d%%" % round(self.alpha * 100))
        c.create_line(BAR_X0, y, BAR_X1, y, fill=LINE, width=4,
                      capstyle="round")
        c.create_line(BAR_X0, y, kx, y, fill=ACCENT, width=4, capstyle="round")
        c.create_oval(kx - 7, y - 7, kx + 7, y + 7, fill=PANEL,
                      outline=ACCENT, width=2)

    def slider_hit(self, e):
        """바를 잡았으면 그 위치로 투명도를 맞추고 True."""
        if not self.menu:
            return False
        if abs(e.y - BAR_Y) > BAR_GRAB or not (BAR_X0 - 12 <= e.x <= BAR_X1 + 12):
            return False
        frac = (e.x - BAR_X0) / float(BAR_X1 - BAR_X0)
        frac = min(1.0, max(0.0, frac))
        self.set_alpha(ALPHA_MIN + frac * (ALPHA_MAX - ALPHA_MIN))
        return True

    def set_alpha(self, value):
        self.alpha = min(ALPHA_MAX, max(ALPHA_MIN, round(value, 2)))
        self.apply_alpha()

    # --- 입력 ---
    def on_drag(self, e, button=1):
        if self.menu:
            if self.slider_hit(e):
                self.draw()
        elif self.game.click(e.x, e.y, button, drag=True):
            self.draw()

    def on_release(self, _e):
        self.save()

    def on_click(self, e, button=1):
        """메뉴에서는 클릭으로 고르고, 게임 중에는 게임에 넘긴다."""
        if not self.menu:
            if self.game.click(e.x, e.y, button):
                self.draw()
            return
        if self.slider_hit(e):
            self.draw()
            return
        top = BAR + 100
        i = int((e.y - top) // ((H - 26 - top) / len(self.games)))
        if 0 <= i < len(self.games):
            self.pick = i
            self.choose(i)
            self.draw()

    def on_key(self, e):
        k = e.keysym
        if k == "Escape":
            return self.stash()
        if k in ("h", "H"):
            self.faded = not self.faded
            self.apply_alpha()
            return
        if self.faded:
            return
        if k in ("bracketleft", "bracketright"):
            self.set_alpha(self.alpha + (-0.05 if k == "bracketleft" else 0.05))
            self.save()
        elif k in ("l", "L"):
            self.lang = i18n.toggle()
            self.save()
        elif k in ("m", "M"):
            # Tab 은 게임 쪽에 넘긴다 (네모로직에서 칠하기/X 전환)
            self.menu = not self.menu
            self.pick = self.idx
        elif self.menu:
            self.menu_key(k)
        elif k.isdigit() and 1 <= int(k) <= len(self.games):
            self.choose(int(k) - 1)
        elif k in ("r", "R"):
            self.game.reset()
        elif k in ("comma", "less", "period", "greater", "Prior", "Next"):
            step = 10 if k in ("Prior", "Next") else 1
            back = k in ("comma", "less", "Prior")
            self.game.jump(-step if back else step)
        else:
            self.game.key(k)
        self.draw()

    # --- 루프 ---
    def loop(self):
        self.hotkey.poll()
        if not self.paused:
            if not self.menu:            # 메뉴가 떠 있을 때도 멈춘다
                self.game.tick(FPS_MS / 1000.0)
            self.draw()
        self.root.after(FPS_MS, self.loop)

    def draw(self):
        if self.paused:
            return
        c = self.canvas
        c.delete("all")
        g = self.game
        g.best = max(g.best, g.score)

        c.create_rectangle(0, 0, W, BAR, fill=PANEL, outline="")
        c.create_line(0, BAR, W, BAR, fill=LINE)
        c.create_text(10, BAR / 2, text=g.name, fill=INK, anchor="w",
                      font=(FONT, 9, "bold"))
        c.create_text(W - 10, BAR / 2, anchor="e", fill=DIM, font=(FONT, 9),
                      text="%d   best %d" % (g.score, g.best))
        for i in range(len(self.games)):
            c.create_text(110 + i * 16, BAR / 2, text=str(i + 1), font=(FONT, 8),
                          fill=INK if i == self.idx else "#b9c2ce")
        c.create_text(W - 10, BAR / 2 + 9, anchor="e", fill="#b9c2ce",
                      font=(FONT, 6), text="L: %s" % t("한국어"))

        if self.menu:
            self.draw_menu(c)
            c.create_text(W / 2, H - 9, fill=DIM, font=(FONT, 7),
                          text=t("ESC 내리기 · %s 꺼내기 · Ctrl+Q 종료")
                               % hotkey.label(self.hotkey.spec))
            return

        g.draw(c, 0, BAR, W, H - BAR - 18)

        c.create_text(W / 2, H - 9, fill=DIM, font=(FONT, 7),
                      text=t("%s     M 게임 고르기 · ESC 내리기 · %s 꺼내기")
                           % (t(g.help), hotkey.label(self.hotkey.spec)))
        if g.over:
            c.create_text(W / 2, H / 2 + 1, text="GAME OVER — R", fill="#ffffff",
                          font=(FONT, 17, "bold"))
            c.create_text(W / 2, H / 2, text="GAME OVER — R", fill="#c9384a",
                          font=(FONT, 17, "bold"))

    def quit(self):
        self.save()
        self.hotkey.stop()
        self.root.destroy()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    Shell().run()
