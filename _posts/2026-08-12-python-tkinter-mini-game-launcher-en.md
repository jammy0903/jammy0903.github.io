---
layout: post
title: "Building a Nine-Game Desktop Launcher with Python and tkinter"
subtitle: "Mini-games for short breaks, with procedural puzzles, physics, and a shared GUI architecture"
date: 2026-08-12 21:00:00 +0900
categories: blog
tags: ['python', 'tkinter', 'gui', 'game-development', 'side-project', 'nonogram', 'sokoban', 'procedural-generation', 'algorithms']
description: "A nine-game desktop launcher built with the Python standard library. Explore its shared GUI architecture, procedural puzzle generation and validation, physics, state persistence, and standalone distribution."
---

**desk brings nine mini-games into one desktop window for short breaks.**
Switch between games, close the application, and return to the saved boards later.
It runs offline, and the Windows executable does not require a Python installation.

The implementation uses Python's standard library, with tkinter for the interface.
As a development project, it combines a shared game interface, procedural puzzle
generation and validation, physics, and desktop event handling. This post covers
the application and the implementation problems solved along the way.

> **[⬇ Get desk.exe (11MB)]({{ '/assets/files/desk.exe' | relative_url }})** —
> no Python needed, just double-click it. [Pin it to the taskbar](#standalone-distribution)
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

## Window controls and distribution

### Adjustable opacity

Opacity defaults to 55% and can be adjusted with `[` `]` or the menu slider.
This is a window display setting that users can adjust to their preference.

### Minimize and restore

`ESC` minimizes the window to the taskbar while preserving the board and score.
`F8` restores it. Quitting is a separate action: `Ctrl+Q` or the window's close button.

`H` toggles between zero opacity and the previous display state without moving the
window. It still receives keyboard input while transparent, so minimizing is the
clearer choice when switching to another application.

### Standalone distribution

Run `desk.exe`, right-click its taskbar icon, and choose **Pin to taskbar**.
The executable is packaged as a single file with PyInstaller. `make_icon.py` writes
ICO data using the standard library, without additional image tooling.
The window is not always-on-top and follows ordinary desktop window switching.

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
| `H` | Toggle zero opacity / previous display state |
| `M` | Game menu |
| `1`–`9` | Jump to a game |
| `[` `]` | Dimmer / brighter (or drag the slider in the menu) |
| `,` `.` | Change level (`PageUp`/`PageDown` moves 10) |
| `L` | Korean / English |
| `R` | Retry this board |
| `Ctrl+Q` | Quit (so does the X button) |

---

## Development experience covered

- **Architecture:** a common game interface separates individual games from the launcher.
- **Algorithms:** a Nonogram solver and reverse Sokoban generation address puzzle solvability.
- **Validation:** generated boards, physics behavior, and global hotkey handling are checked and debugged.
- **Usability:** automatic state persistence, language switching, and standalone packaging support everyday use.

[Download desk.exe]({{ '/assets/files/desk.exe' | relative_url }}) or
[browse the source]({{ '/desk/' | relative_url }}) to explore the implementation.
