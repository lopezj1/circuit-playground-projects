# /// script
# requires-python = ">=3.10"
# dependencies = ["pillow"]
# ///
"""Turn a picture of the hero into the buddy's face.

    uv run tools/make_face.py projects/05-buddy/hero_source.png

Writes into projects/05-buddy/:
  hero.bmp      the picture, 240x240 with 16 colors, for the TFT Gizmo
  hero_face.py  where the eyes are, so the game can draw pupils and
                eyelids on top of the picture
and a preview (hero_preview.png) with the eye outlines drawn in green.

The eyes are found as the two biggest white areas, so draw them as empty
white shapes. If a thin blue or purple line circles each eye a little way out (like a
mask's lens), the eye is widened to that line: the gap gets the eye's color
and the eyelids reach the line. All three files are gitignored: a hero picture may not be
yours to publish.
"""
import math
import sys
from collections import Counter
from pathlib import Path

from PIL import Image, ImageDraw

SIZE = 240
COLORS = 16
EXPAND = 2          # eyelids reach this many pixels past the white
RAYS = 24           # directions to look for a line around each eye
LINE_GAP = 12       # how far past the white that line may be, in pixels
OUT = Path(__file__).resolve().parent.parent / "projects" / "05-buddy"


def load(path):
    img = Image.open(path).convert("RGBA")
    black = Image.new("RGBA", img.size, (0, 0, 0, 255))
    img = Image.alpha_composite(black, img).convert("RGB")
    w, h = img.size
    side = max(w, h)
    square = Image.new("RGB", (side, side))
    square.paste(img, ((side - w) // 2, (side - h) // 2))
    return square.resize((SIZE, SIZE), Image.LANCZOS)


def white_blobs(img):
    px = img.load()
    is_white = [[min(px[x, y]) > 170 for x in range(SIZE)] for y in range(SIZE)]
    seen = set()
    blobs = []
    for y in range(SIZE):
        for x in range(SIZE):
            if not is_white[y][x] or (x, y) in seen:
                continue
            blob = []
            todo = [(x, y)]
            seen.add((x, y))
            while todo:
                cx, cy = todo.pop()
                blob.append((cx, cy))
                for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                    if 0 <= nx < SIZE and 0 <= ny < SIZE and is_white[ny][nx] \
                            and (nx, ny) not in seen:
                        seen.add((nx, ny))
                        todo.append((nx, ny))
            blobs.append(blob)
    blobs.sort(key=len, reverse=True)
    return blobs


def hull(points):
    pts = sorted(set(points))

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower, upper = [], []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


def is_line(p):
    """Blue or purple: some blue, and not the bright red or pink around it."""
    r, g, b = p
    return b > 0x50 and r < 0xB0 and b > g + 0x20


def line_around(px, center):
    """Points just inside a thin line that circles the eye, or None if
    there's no such line all the way around."""
    cx, cy = center
    points = []
    for i in range(RAYS):
        a = 2 * math.pi * i / RAYS
        dx, dy = math.cos(a), math.sin(a)
        r = 1.0
        last_white = 0
        hit = None
        while r < SIZE:
            x, y = round(cx + dx * r), round(cy + dy * r)
            if not (0 <= x < SIZE and 0 <= y < SIZE):
                break
            p = px[x, y]
            if min(p) > 170:
                last_white = r
            elif is_line(p):
                hit = r
                break
            elif r - last_white > LINE_GAP:
                break
            r += 0.5
        if hit is None:
            return None
        points.append((round(cx + dx * (hit - 0.5)), round(cy + dy * (hit - 0.5))))
    return points


def edge_distance(c, a, b):
    (x, y), (x1, y1), (x2, y2) = c, a, b
    length = math.hypot(x2 - x1, y2 - y1) or 1
    return abs((x2 - x1) * (y1 - y) - (x1 - x) * (y2 - y1)) / length


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    img = load(sys.argv[1])
    blobs = white_blobs(img)
    if len(blobs) < 2 or len(blobs[1]) < 200:
        sys.exit("Couldn't find two white eyes in the picture.")

    px = img.load()
    eyes = []
    rim = Counter()
    for blob in sorted(blobs[:2], key=lambda b: min(p[0] for p in b)):
        cx = sum(p[0] for p in blob) / len(blob)
        cy = sum(p[1] for p in blob) / len(blob)
        outline = []
        for x, y in hull(blob):
            d = math.hypot(x - cx, y - cy) or 1
            outline.append((round(x + (x - cx) / d * EXPAND),
                            round(y + (y - cy) / d * EXPAND)))
            # The color just outside the white is what the eyelids use.
            rx = round(x + (x - cx) / d * 7)
            ry = round(y + (y - cy) / d * 7)
            if 0 <= rx < SIZE and 0 <= ry < SIZE:
                rim[px[rx, ry]] += 1
        line = line_around(px, (cx, cy))
        if line:
            outline = line
            print("found the line around eye %d" % (len(eyes) + 1))
        inside = min(edge_distance((cx, cy), outline[i - 1], outline[i])
                     for i in range(len(outline)))
        eyes.append({
            "widen": bool(line),
            "color": tuple(sum(px[x, y][c] for x, y in blob) // len(blob)
                           for c in range(3)),
            "center": (round(cx), round(cy)),
            "top": min(p[1] for p in outline),
            "bottom": max(p[1] for p in outline),
            "room": round(inside),
            "outline": outline,
        })
    r, g, b = rim.most_common(1)[0][0]
    lid = (r << 16) | (g << 8) | b

    # Widen the eyes: paint the gap between the white and the line.
    for e in eyes:
        if not e["widen"]:
            continue
        mask = Image.new("L", (SIZE, SIZE))
        ImageDraw.Draw(mask).polygon(e["outline"], fill=255)
        inside = mask.load()
        for y in range(SIZE):
            for x in range(SIZE):
                if inside[x, y] and min(px[x, y]) <= 170 and not is_line(px[x, y]):
                    px[x, y] = e["color"]

    img.quantize(colors=COLORS, method=Image.Quantize.MEDIANCUT).save(OUT / "hero.bmp")

    lines = [
        "# Made by tools/make_face.py from the hero picture. PRIVATE: gitignored.",
        "# Where the eyes are in hero.bmp, so the game can draw pupils and lids.",
        'IMAGE = "hero.bmp"',
        "LID_COLOR = 0x%06X" % lid,
        "EYES = [",
    ]
    for e in eyes:
        lines.append("    {\"center\": %r, \"top\": %d, \"bottom\": %d, \"room\": %d,"
                     % (e["center"], e["top"], e["bottom"], e["room"]))
        lines.append("     \"outline\": %r}," % (e["outline"],))
    lines.append("]")
    (OUT / "hero_face.py").write_text("\n".join(lines) + "\n", encoding="utf-8")

    preview = img.resize((SIZE * 2, SIZE * 2), Image.NEAREST)
    draw = ImageDraw.Draw(preview)
    for e in eyes:
        draw.polygon([(x * 2, y * 2) for x, y in e["outline"]], outline=(0, 255, 0))
        cx, cy = e["center"]
        draw.ellipse([cx * 2 - 4, cy * 2 - 4, cx * 2 + 4, cy * 2 + 4], fill=(0, 255, 0))
    preview.save(OUT / "hero_preview.png")

    for i, e in enumerate(eyes):
        print("eye %d: center %s, %d to %d tall, room %d, %d outline points"
              % (i + 1, e["center"], e["top"], e["bottom"], e["room"], len(e["outline"])))
    print("eyelid color 0x%06X" % lid)
    print("wrote hero.bmp, hero_face.py, hero_preview.png in", OUT)


if __name__ == "__main__":
    main()
