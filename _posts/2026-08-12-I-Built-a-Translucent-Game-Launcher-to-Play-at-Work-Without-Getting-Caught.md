---
layout: post
title: "I Built a Translucent Game Launcher to Play at Work Without Getting Caught"
subtitle: "Nine games to play at work without getting caught — Tetris, Suika, Puyo Puyo, 2048, Nonogram. One key hides it to the taskbar, and there is nothing to install"
date: 2026-08-12 21:00:00 +0900
categories: blog
tags: ['games-at-work', 'stealth-game', 'office-games', 'boss-key', 'python', 'tkinter', 'side-project', 'tetris', 'nonogram', 'sokoban', 'procedural-generation']
description: "A translucent game launcher for playing at work without getting caught. Nine games — Tetris, Suika, Puyo Puyo, 2048, Nonogram and more — in one window that hides to the taskbar with one key. Python standard library only, no install, free download."
---

You want to goof off for five minutes at work, but opening a game is obvious.
A browser game leaves a conspicuous tab. Alt-tabbing swaps the whole screen, which
anyone walking past can see instantly.

So I built one. **A translucent launcher that sits quietly on top of your work and
drops into the taskbar with one press of `ESC`.** Nine games in a single window,
using nothing but the Python standard library (tkinter) — nothing to install.

> **[⬇ Get desk.exe (11MB)]({{ '/assets/files/desk.exe' | relative_url }})** —
> no Python needed, just double-click it. [Pin it to the taskbar](#pin-it-to-the-taskbar)
> and it opens with one click.
>
> [Source zip (58KB)]({{ '/assets/files/desk.zip' | relative_url }}) ·
> [Browse the source]({{ '/desk/' | relative_url }}) ·
> [GitHub Releases](https://github.com/jammy0903/jammy0903.github.io/releases/latest)

---

## What's in it

| # | Game | # | Game |
|---|---|---|---|
| 1 | Tetris | 6 | Triple Town |
| 2 | Suika (watermelon game) | 7 | Nonogram (1,500 puzzles) |
| 3 | Puyo Puyo | 8 | Flood It (60 stages) |
| 4 | 2048 | 9 | Sokoban (200 levels) |
| 5 | Threes! | | |

`M` opens a picker, `1`–`9` jump straight to a game. **All nine boards are saved
separately**, so wandering off to another game and coming back leaves yours untouched.

The level-based games (Nonogram, Sokoban, Flood It) let you jump to any level with
`,` `.` — shipping 1,500 puzzles you can only reach one at a time would be pointless.
Nonogram picks between **10x10 / 15x15 / 20x20** with `S`, and each size keeps its
own progress.

---

## The point isn't the games — it's the hiding

Games are everywhere. The reason this exists is **not getting caught.**

### 1. Translucency

55% by default, adjustable with `[` `]` or by **dragging the opacity slider** on the
menu screen. Down at 20% the document behind it shows through and a sideways glance
catches nothing.

It never darkens the background, so the screen doesn't visibly dim either.

### 2. `ESC` sends it to the taskbar

`ESC` **doesn't quit — it drops the window to the taskbar.** Your board and score
survive. `F8` brings it back.

`ESC` deliberately isn't quit — panic-pressing it shouldn't cost you a board.
To actually close it, `Ctrl+Q` or the window's X button. Either way progress is saved.

### 3. `H` is the fast one

This is what you actually end up using. `ESC` genuinely minimises the window, so you
need `F8` to get it back. `H` **leaves the window exactly where it is and just sets
opacity to zero.** It still receives keys, so one more `H` brings it straight back.
Much faster to react with.

### 4. Pin it to the taskbar

Run `desk.exe` once, right-click its taskbar icon, *Pin to taskbar*. From then on it
looks like just another program that lives there. The icon is deliberately plain.

The exe is a single PyInstaller file, so **copying that one file to a machine without
Python is enough.** Its icon is written by `make_icon.py` — raw ICO bytes from the
standard library, no image tooling.

### 5. Not always-on-top

I had it always-on-top at first and removed it. Other windows *should* cover it —
the goal is to look like one more window layered into your work, not a floating panel.

---

## Being honest about what it can't do

Worth stating plainly:

- **It does not defeat monitoring software.** Screen capture, process monitoring —
  this program does nothing about any of it. It's an ordinary window.
- **The process name is not disguised.** Task Manager shows `pythonw.exe`.

I deliberately left that out. This is for dodging a glance from the next desk, not
for getting around a company's security policy. That's a different thing, and not
one I'm going to build.

---

## The interesting parts

Code talk from here. Fine to stop if you just wanted the games.

### Fitting 500 nonograms in

**The 500 puzzles aren't stored anywhere.** Each is generated from its level number
used as the random seed. Puzzle 300 is identical every time you open it, and the
program stays small.

The catch: **generate carelessly and you get unsolvable boards.** Fill a grid at
random, derive the clues, and you often end up with a puzzle the clues can't pin
down — one that requires guessing. That isn't a puzzle, it's an annoyance.

So there's a **line solver** in the generator. For each line, enumerate every
arrangement the clue permits, drop the ones that contradict what's already known, and
commit only the cells **every survivor agrees on**. Rows, then columns, then rows,
until nothing changes. If the grid comes out fully determined, the puzzle is solvable
without a single guess. Otherwise, throw it away and generate another.

```python
fits = [o for o in options(clue[i], n)
        if all(k < 0 or k == v for k, v in zip(known, o))]
merged = [fits[0][j] if all(f[j] == fits[0][j] for f in fits) else -1
          for j in range(n)]
```

**All 1,500 verified — 500 per size. 100% pass**, most generated in under 0.01s.

Difficulty comes from the fill density, which drifts toward 0.5 so there are fewer
completely full or empty lines — the clues carry less information, so it gets harder.

I got one thing backwards here. I assumed **bigger boards should use a lower density**,
tried it, and the exhaustive check went from 5.8s to 80s with six unsolvable boards.
Sparser lines admit *more* possible arrangements, so **fewer cells get pinned down.**
Each size now has its own density floor — below 0.60 a 20x20 board takes seconds to
generate.

### Sokoban is built backwards

Generating solvable Sokoban is much harder. Boxes can only be pushed, never pulled,
so a randomly placed box easily ends up wedged in a corner forever.

So I **built it in reverse.** Start from the solved position — every box on a goal —
and *pull* boxes around to scramble it. Reversing the pulls is a solution by
construction, so **every generated board is solvable** and no search is needed at
play time.

I got the pull wrong at first:

```python
boxes.discard(box); boxes.add(back)
man = box            # ← wrong
```

After a pull the player should be standing **where they retreated to**, but I put
them on the box's old cell — effectively teleporting them through the box to the
other side. That produces positions that can't be undone. The verifier caught it on
level 7:

```
######
###  #
###@ #
#  $.#     ← to push the box right you must stand to its left,
# #  #        and the only path there is blocked by the box
######
```

Fixed to `man = stand`, then **BFS-solved all 200 levels for real. Zero failures.**
(That check alone takes 13 minutes — 9x9 with four boxes has a large state space.
Generating a board is still 0.01s, since that direction needs no search at all.)

### Why the global hotkey didn't work

Pressing `F9` did nothing. Two separate causes.

**One.** `RegisterHotKey` posts `WM_HOTKEY` to the message queue of the thread that
registered it. Register on the main thread and **tkinter's own message pump grabs it
first** — no amount of `PeekMessage` will ever see it. Fixed by registering and
waiting on a dedicated thread.

**Two.** The funnier one: **`F9` was already taken by another program.** A global
hotkey can be held by only one program on the entire machine. Scanning the keys, `F9`
and `F12` were in use while `F8`, `F7` and `F6` were free.

So the default moved to `F8`, with a fallback list tried in order on failure, and
**the menu screen always displays which key actually got registered.** If none of
them work, it says so in red.

### Suika physics

Verlet integration with positional (PBD) constraints, written from scratch. At first
fruit bounced apart, and fruit sitting perfectly still on the floor still counted as
"moving", so the game-over check never fired.

The cause was moving the **previous position along with the current one** when
resolving overlap. In Verlet, velocity *is* `current - previous`, so leaving the
previous position alone is itself the velocity correction — that's what lets a stack
settle. Walls and floor need the opposite: set previous to the new position, or
gravity's accumulated velocity grows without bound. I had the two backwards.

---

## Structure

```
desk.py          window, menu, save file, keys
hotkey.py        global hotkey (Windows, ctypes)
games/base.py    shared interface, palette, drawing helpers
games/i18n.py    Korean / English
games/*.py       one file per game
smoke_test.py    all of the above
```

A game implements six methods: `reset / key / tick / draw / state / load`. The shell
knows nothing about any particular game, so a tenth one is **one file plus one line
in a list**.

About 2,800 lines total. Zero external dependencies.

---

## Odds and ends

- **Records** — everything in one `~/.deskgames.json`. No accounts, no login. Best
  scores survive `R`. Autosaved every 10 seconds, written to a temp file and swapped
  in so a crash mid-write can't corrupt the old one.
- **Language** — `L` toggles Korean / English.
- **Tests** — `python3 smoke_test.py` covers rules, physics, save/restore, all nine
  render paths, hide/restore, and **whether generated levels are genuinely solvable.**

---

## Every key

| Key | What it does |
|---|---|
| `ESC` | **Drop to taskbar** (does not quit) |
| `F8` | **Bring it back** |
| `H` | Opacity to zero (fastest) |
| `M` | Game menu |
| `1`–`9` | Jump to a game |
| `[` `]` | Dimmer / brighter (or drag the slider in the menu) |
| `,` `.` | Change level (`PageUp`/`PageDown` moves 10) |
| `L` | Korean / English |
| `R` | Retry this board |
| `Ctrl+Q` | Quit (so does the X button) |

---

Enjoy your five minutes.
