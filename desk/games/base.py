"""게임 공통 인터페이스와 그리기 헬퍼."""

FONT = "Helvetica"

# 밝은 팔레트. 반투명으로 깔려도 글자가 읽히도록 대비를 충분히 둔다.
BG = "#f4f6f9"        # 창 바탕
PANEL = "#ffffff"     # 판 안쪽
EMPTY = "#e4e9f0"     # 빈 칸
INK = "#1f2733"       # 본문
DIM = "#8a94a4"       # 보조 글자
LINE = "#d3dae4"      # 테두리·구분선
ACCENT = "#2f6ea8"


class Game:
    """모든 게임이 상속하는 최소 인터페이스.

    셸(main.py)이 하는 일:
      - reset()          새 게임
      - key(keysym)      키 입력. 처리했으면 True
      - tick(dt)         매 프레임. 물리/중력이 있는 게임만 사용
      - draw(c, x,y,w,h) 주어진 사각형 안에 그리기
      - state()/load()   창을 닫아도 이어서 하기 위한 직렬화
    """

    name = "game"
    help = ""
    LEVELS = 0          # 0이면 레벨이 없는 게임

    def __init__(self):
        self.score = 0
        self.best = 0
        self.over = False
        self.reset()

    def reset(self):
        raise NotImplementedError

    def key(self, keysym):
        return False

    def click(self, x, y, button=1, drag=False):
        """캔버스 좌표로 들어오는 마우스 입력. 처리했으면 True.

        drag=True 면 누른 채 끌고 있는 중이다.
        """
        return False

    def tick(self, dt):
        return False

    def draw(self, c, x, y, w, h):
        raise NotImplementedError

    def state(self):
        return None

    def load(self, d):
        pass

    def jump(self, delta):
        """레벨 건너뛰기. 레벨이 있는 게임만 반응한다.

        500판을 넣어 놓고 한 판씩만 넘어갈 수 있으면 뒷판을 볼 길이 없다.
        """
        if not self.LEVELS:
            return False
        self.level = (self.level + delta) % self.LEVELS
        self.load_level()
        return True

    # --- 헬퍼 ---
    def bump(self, points):
        self.score += points
        if self.score > self.best:
            self.best = self.score


def rrect(c, x0, y0, x1, y1, r, **kw):
    """캔버스에 둥근 사각형. r=0이면 그냥 사각형."""
    if r <= 0:
        return c.create_rectangle(x0, y0, x1, y1, **kw)
    r = min(r, (x1 - x0) / 2, (y1 - y0) / 2)
    pts = [
        x0 + r, y0, x1 - r, y0, x1, y0, x1, y0 + r,
        x1, y1 - r, x1, y1, x1 - r, y1,
        x0 + r, y1, x0, y1, x0, y1 - r,
        x0, y0 + r, x0, y0,
    ]
    return c.create_polygon(pts, smooth=True, **kw)


def ink_on(color):
    """배경색 위에서 읽히는 글자색(밝기 기준)."""
    r, g, b = (int(color[i:i + 2], 16) for i in (1, 3, 5))
    return "#1f2733" if (r * 299 + g * 587 + b * 114) / 1000 > 150 else "#ffffff"


def center_text(c, x, y, text, size, fill=INK, bold=True):
    c.create_text(x, y, text=text, fill=fill,
                  font=(FONT, size, "bold" if bold else "normal"))
