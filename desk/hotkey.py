"""작업표시줄에서 창을 다시 꺼내는 전역 단축키.

창이 작업표시줄로 내려가 있으면 tkinter는 키를 받지 못한다.
그래서 OS에 직접 등록해야 한다. 윈도우는 ctypes로 RegisterHotKey를 쓰고,
그 외 환경에서는 조용히 비활성 상태가 된다(작업표시줄 아이콘 클릭으로 복귀).
표준 라이브러리만 쓴다.

단축키를 바꾸려면 아래 HOTKEY 한 줄만 고치면 된다.
  "F9"  "F8"  "Alt+`"  "Ctrl+Alt+G"  "Shift+F9" …

왜 전용 스레드를 쓰나
---------------------
RegisterHotKey는 WM_HOTKEY를 '등록한 스레드의 메시지 큐'로 보낸다.
메인 스레드에서 등록하면 tkinter의 메시지 펌프가 그 메시지를 먼저 꺼내
버리는 일이 생겨서, 아무리 PeekMessage를 돌려도 잡히지 않는다.
그래서 등록과 대기를 별도 스레드에서 하고, 눌린 사실만 플래그로 넘긴다.
"""
import sys
import threading

from games.i18n import t

HOTKEY = "F8"

# HOTKEY가 이미 다른 프로그램에 잡혀 있으면 이 순서대로 대신 시도한다.
# (이 PC에서는 F9와 F12가 이미 사용 중이었다)
FALLBACKS = ["F8", "F7", "F6", "F10", "Alt+`", "Ctrl+`", "Ctrl+Alt+G"]

MODS = {"alt": 0x0001, "ctrl": 0x0002, "control": 0x0002,
        "shift": 0x0004, "win": 0x0008}
MOD_NOREPEAT = 0x4000
WM_HOTKEY = 0x0312
WM_QUIT = 0x0012
HOTKEY_ID = 0xBEE

# 이름 → 윈도우 가상 키 코드
KEYS = {"`": 0xC0, "-": 0xBD, "=": 0xBB, "[": 0xDB, "]": 0xDD,
        "\\": 0xDC, ";": 0xBA, "'": 0xDE, ",": 0xBC, ".": 0xBE, "/": 0xBF,
        "space": 0x20, "insert": 0x2D, "pause": 0x13, "scrolllock": 0x91}
for _i in range(1, 25):
    KEYS["f%d" % _i] = 0x6F + _i          # VK_F1 = 0x70
for _ch in "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789":
    KEYS[_ch.lower()] = ord(_ch)


def parse(spec):
    """'Ctrl+Alt+G' → (모디파이어 비트, 가상 키 코드). 모르는 키면 None."""
    parts = [p.strip().lower() for p in spec.split("+") if p.strip()]
    if not parts:
        return None
    mods = 0
    for p in parts[:-1]:
        if p not in MODS:
            return None
        mods |= MODS[p]
    vk = KEYS.get(parts[-1])
    return None if vk is None else (mods | MOD_NOREPEAT, vk)


def label(spec=None):
    """화면에 보여 줄 이름."""
    spec = HOTKEY if spec is None else spec
    return "+".join(p.strip().capitalize() for p in spec.split("+"))


class GlobalHotkey:
    """poll()을 주기적으로 불러 주면 눌렸을 때 callback을 실행한다.

    poll()은 tkinter 스레드에서 불린다. 실제 대기는 별도 스레드가 하고,
    여기서는 Event 하나만 주고받는다.
    """

    def __init__(self, callback, spec=None):
        self.callback = callback
        self.spec = HOTKEY if spec is None else spec
        self.active = False
        self.error = None
        self._fired = threading.Event()
        self._thread = None
        self._tid = None
        self._ready = threading.Event()

    def start(self):
        """설정한 키부터 시도하고, 이미 잡혀 있으면 대체 키로 넘어간다."""
        if not sys.platform.startswith("win"):
            self.error = t("전역 단축키는 윈도우에서만 동작 (작업표시줄 클릭으로 복귀)")
            return False
        tried = []
        for spec in [self.spec] + [f for f in FALLBACKS if f != self.spec]:
            combo = parse(spec)
            if combo is None:
                continue
            self.spec = spec
            self._ready.clear()
            self._thread = threading.Thread(target=self._run, args=combo,
                                            daemon=True)
            self._thread.start()
            self._ready.wait(2.0)
            if self.active:
                if tried:
                    self.error = (t("%s 는 사용 중이라 %s 로 잡았다")
                                  % (", ".join(tried), label(spec)))
                else:
                    self.error = None
                return True
            tried.append(label(spec))
        self.error = t("쓸 수 있는 전역 단축키가 없음 (작업표시줄 클릭으로 복귀)")
        return False

    def _run(self, mods, vk):
        try:
            import ctypes
            from ctypes import wintypes
            user32 = ctypes.windll.user32
            kernel32 = ctypes.windll.kernel32
            self._tid = kernel32.GetCurrentThreadId()
            if not user32.RegisterHotKey(None, HOTKEY_ID, mods, vk):
                self.error = (t("%s 는 다른 프로그램이 이미 쓰고 있음")
                              % label(self.spec))
                self._ready.set()
                return
            self.active = True
            self._user32 = user32
            self._ready.set()

            msg = wintypes.MSG()
            # 이 스레드는 이 메시지 하나만 기다린다. tkinter와 큐가 겹치지 않는다.
            while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
                if msg.message == WM_HOTKEY and msg.wParam == HOTKEY_ID:
                    self._fired.set()
            user32.UnregisterHotKey(None, HOTKEY_ID)
        except Exception as e:                     # 환경이 안 맞으면 조용히 포기
            self.error = str(e)
        finally:
            self.active = False
            self._ready.set()

    def poll(self):
        """tkinter 쪽에서 매 프레임 호출. 눌렸으면 callback을 실행한다."""
        if self._fired.is_set():
            self._fired.clear()
            self.callback()

    def stop(self):
        if self._tid is not None:
            try:
                import ctypes
                ctypes.windll.user32.PostThreadMessageW(self._tid, WM_QUIT, 0, 0)
            except Exception:
                pass
        self.active = False
