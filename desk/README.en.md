# desk

Nine games in one small, translucent, always-available window.
Pure Python standard library (tkinter). Nothing to install.

```bash
python3 desk.py
```

On Windows, **double-click `desk.bat`** — it launches without a console window.

Press `L` at any time to switch between 한국어 and English.

## Keys

| Key | What it does |
| --- | --- |
| `ESC` | **Send the window to the taskbar.** The program keeps running; your board and score stay |
| `F8` | **Bring it back** (global hotkey, Windows) |
| `H` | Fade to fully transparent in place. Press again to return |
| `M` | **Game menu** (`↑` `↓` + `Enter`, or click). This is the first screen on launch |
| `1` – `9` | Jump straight to a game |
| `[` `]` | Dimmer / brighter — or drag the opacity slider on the menu screen |
| `L` | 한국어 / English |
| `R` | Restart the current game (or the current level, for the level-based ones) |
| `,` `.` | **Change level** in the level-based games. `PageUp`/`PageDown` moves 10 |
| `Ctrl+Q` | Quit (so does the window's X button) |

**`ESC` hides instead of quitting**, so a board is never lost by a panicked keypress.
To actually quit, use `Ctrl+Q` or the window's X button — either way your progress is saved.

`ESC` and `H` do different jobs:

- `ESC` — the window leaves the screen entirely and other windows cover its place.
  Come back with `F8` or by clicking the taskbar icon.
- `H` — the window stays exactly where it is and merely becomes invisible. It still
  receives keys, so a single `H` brings it straight back. This one is faster.

## The games

| # | Game | Controls |
| --- | --- | --- |
| 1 | Tetris | `←` `→` move · `↑` rotate · `↓` soft drop · `Space` hard drop |
| 2 | Suika (watermelon) | `←` `→` aim · `Space` drop |
| 3 | Puyo Puyo | `←` `→` move · `↑` rotate · `↓` lower · `Space` drop |
| 4 | 2048 | arrows |
| 5 | Threes! | arrows |
| 6 | Triple Town | arrows move · `Space` place · `S` swap storage |
| 7 | Nonogram | arrows · `Space` fill · `X` mark · **`S` board size** · `Enter` next |
| 8 | Flood It | `←` `→` pick colour · `Space` flood · `Enter` next stage |
| 9 | Sokoban | arrows push · `U` undo · `Enter` next level |

## Levels

| Game | Count | How it gets harder |
| --- | --- | --- |
| Nonogram | **500 per size** | `S` picks 10x10 · 15x15 · 20x20; density drifts so clues say less |
| Sokoban | **200 levels** | bigger rooms, 2 → 4 boxes, deeper scrambles |
| Flood It | **60 stages** | 11x11/5 colours → 20x20/6 colours, move slack 5 → 1 |
| Tetris | endless | a level every 8 lines: faster drops, bigger score multiplier |
| Puyo Puyo | endless | a level every 24 puyos popped, with 5 colours |
| the rest | endless | until the board fills up |

In the three level-based games, **`R` retries the current level only** — hard-won
progress is never thrown away — and **`,` `.` jump straight to any level.** Shipping
500 puzzles you can only reach one at a time would be pointless.

Nonogram keeps **separate progress per size**, so switching to 20x20 and back leaves
your 10x10 puzzle exactly where it was.

Levels are **not stored as 500 data files.** Each one is generated from its level
number as the random seed, so level 300 is always the same puzzle and the program
stays small. The interesting part is guaranteeing every generated board is
actually **solvable**, which each game does differently:

- **Nonogram** — a line solver runs over each candidate; only boards that are fully
  determined by line logic alone (no guessing) ship. All 500 verified, ~0.1 s each.
- **Sokoban** — built backwards. Start from the solved position and *pull* boxes
  around; reversing the pulls is a solution by construction, so no search is needed
  at play time.
- **Flood It** — the move limit is derived from a greedy solve ("always take the
  colour that swallows the most") plus slack. Since that is a strategy a human can
  actually follow, no stage is impossible.

## Records

Everything lives in one file, `~/.deskgames.json`: each game's board in progress,
its best score, the opacity, the language, and which game you had open.
No accounts, no login, no server.

- The best score updates whenever the score rises and survives `R` and a lower score.
- Saved when the window is hidden, when you switch games, on quit, and every 10 seconds.
- Written to a temp file and swapped in, so a crash mid-write can't corrupt the old file.

Delete the file to reset everything.

## Notes on the rules

- **Tetris** — standard. 7-bag randomiser, landing preview, 100/300/500/800 per
  1/2/3/4 lines multiplied by level, faster every 10 lines.
- **Suika** — same fruit twice makes the next one, 11 tiers. The physics is Verlet
  integration with positional (PBD) constraints, so fruit settles instead of bouncing.
  A fruit resting above the dashed line for 1.6 s ends the game.
- **Puyo Puyo** — 6x12 with 5 colours. Four of a colour orthogonally connected pop, the rest falls,
  and the chain multiplier climbs steeply.
- **2048** — standard; new tiles are 2 (90%) or 4 (10%).
- **Threes!** — everything moves exactly one cell. `1+2=3`, and from 3 on only equal
  numbers merge. The new tile enters from the edge you pushed away from.
- **Triple Town** — 6x6. Three or more alike, orthogonally connected, become the next
  tier where you placed it, and it cascades. Grass → bush → tree → hut → house →
  mansion → castle → floating castle. Bears wander into empty cells each turn and turn
  into tombstones when boxed in; three tombstones → church → cathedral.
- **Nonogram** — clues for a fully satisfied line grey out. Score equals board area.
- **Flood It** — your connected region is outlined in white. Fewer moves, more points.
- **Sokoban** — push boxes onto the yellow circles. You cannot pull (but `U` undoes).

The original games never published their exact scoring or probability tables, so
these use their own.

## Environment notes

**Opacity** — `-alpha` only works where the desktop composites windows. On an X
session without a compositor the window may come up opaque.

**`F8`** — while the window sits in the taskbar, tkinter receives no keys at all, so
the hotkey has to be registered with the OS. That path is Windows-only
(`ctypes` + `RegisterHotKey`). Elsewhere it silently turns off and you click the
taskbar icon instead.

A global hotkey can only be held by **one program on the whole machine**. If it is
already taken, registration fails — on the machine this was written on, `F9` and
`F12` were already in use. So on failure the fallback list is tried in order, and
**the menu screen always shows which key actually got registered.** If none work it
says so in red.

To change it, edit one line at the top of `hotkey.py`:

```python
HOTKEY = "F8"      # "F7", "Alt+`", "Ctrl+Alt+G", "Shift+F9", …
```

F1–F24, letters, digits and punctuation are supported, with `Ctrl` `Alt` `Shift` `Win`.

## Tests

```bash
python3 smoke_test.py
```

Covers the rules (merges, line clears, chains, bears), the physics (settling,
merging, game over), save/restore through a JSON round-trip, the render path for all
nine games, hide/restore and best-score persistence, the language switch and the
opacity slider — and that generated levels really are solvable (nonogram line solver,
sokoban search, flood-it greedy solve).

Level checks run on a sample. For the exhaustive nonogram run:

```bash
python3 -c "
from games import nonogram as n
print(sum(n.line_solve(*n.make(s, i)[1:], s) == n.make(s, i)[0]
          for s in n.SIZES for i in range(n.LEVELS)))"
```

## Layout

```
desk.py          window, menu, save file, keys
hotkey.py        global hotkey (Windows, ctypes)
games/base.py    shared Game interface, palette, drawing helpers
games/i18n.py    Korean / English strings
games/*.py       one file per game — rules and drawing, no shared state
smoke_test.py    everything above
```

Each game only implements `reset / key / tick / draw / state / load`. The shell knows
nothing about any specific game, so adding a tenth is one file plus one list entry.
