#!/usr/bin/env python3
"""icon.ico 만들기. 외부 라이브러리 없이 ICO(BMP 방식)를 직접 쓴다.

작업표시줄에서 16px로 줄어들어도 알아볼 수 있어야 하므로,
자잘한 그림 대신 색 블록 네 개만 크게 놓는다.
"""
import os
import struct

BG = (0x1f, 0x27, 0x33)          # 어두운 바탕 — 밝은 작업표시줄에서도 또렷하다
BLOCKS = [(0xc9, 0x38, 0x4a),    # 빨강
          (0x3f, 0xb6, 0xd6),    # 하늘
          (0x4c, 0x8f, 0x3f),    # 초록
          (0xc9, 0xa2, 0x27)]    # 노랑
SIZES = (16, 24, 32, 48, 64, 128)


def render(n):
    """(r, g, b, a) 픽셀을 위에서 아래로."""
    px = [[(0, 0, 0, 0)] * n for _ in range(n)]
    pad = max(1, round(n * 0.06))
    r = max(2, round(n * 0.18))               # 모서리 둥글기

    def inside(x, y):
        """둥근 사각형 안쪽인가."""
        lo, hi = pad, n - 1 - pad
        cx = lo + r if x < lo + r else (hi - r if x > hi - r else x)
        cy = lo + r if y < lo + r else (hi - r if y > hi - r else y)
        if not (lo <= x <= hi and lo <= y <= hi):
            return False
        return (x - cx) ** 2 + (y - cy) ** 2 <= r * r

    for y in range(n):
        for x in range(n):
            if inside(x, y):
                px[y][x] = BG + (255,)

    # 가운데 2x2 블록
    gap = max(1, round(n * 0.05))
    span = n - 2 * (pad + gap + max(1, round(n * 0.08)))
    cell = (span - gap) // 2
    if cell < 1:
        cell = max(1, (n - 2 * pad - 3 * gap) // 2)
    ox = (n - (cell * 2 + gap)) // 2
    oy = (n - (cell * 2 + gap)) // 2
    for i, color in enumerate(BLOCKS):
        bx = ox + (i % 2) * (cell + gap)
        by = oy + (i // 2) * (cell + gap)
        for y in range(by, by + cell):
            for x in range(bx, bx + cell):
                if 0 <= x < n and 0 <= y < n:
                    px[y][x] = color + (255,)
    return px


def bmp_entry(px, n):
    """ICO 안에 들어가는 BMP(DIB). 높이는 XOR+AND 두 장이라 2배로 적는다."""
    header = struct.pack("<IiiHHIIiiII", 40, n, n * 2, 1, 32, 0,
                         n * n * 4, 0, 0, 0, 0)
    body = bytearray()
    for y in range(n - 1, -1, -1):            # BMP는 아래에서 위로
        for x in range(n):
            r, g, b, a = px[y][x]
            body += bytes((b, g, r, a))       # BGRA
    # AND 마스크: 알파를 쓰므로 전부 0이지만 자리는 있어야 한다
    row = ((n + 31) // 32) * 4
    body += bytes(row * n)
    return header + bytes(body)


def main():
    images = [(n, bmp_entry(render(n), n)) for n in SIZES]
    out = bytearray(struct.pack("<HHH", 0, 1, len(images)))
    offset = 6 + 16 * len(images)
    for n, data in images:
        out += struct.pack("<BBBBHHII", n % 256, n % 256, 0, 0, 1, 32,
                           len(data), offset)
        offset += len(data)
    for _, data in images:
        out += data

    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.ico")
    with open(path, "wb") as f:
        f.write(out)
    print("%s (%d바이트, %s)" % (path, len(out),
                                 " ".join("%dx%d" % (n, n) for n in SIZES)))


if __name__ == "__main__":
    main()
