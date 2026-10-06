"""note の見出し画像（1280×670）を作る。写真は毎回同じ、背景色はテーマごとに変える。
python3 scripts/gen_note_header.py <出力先.jpg> <テーマ> <タイトル1行目> <2行目> [<3行目>]
テーマ: shacho（社長の退職金）/ staff（従業員）/ hoken（法人保険）/ souzoku（相続）/ keiei（経営のお金）/ sonae（社長の万一）/ intro（自己紹介）"""
import sys, pathlib
from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
F = "/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf"
# (上の色, 下の色, タグの文字)
THEMES = {
    "intro":   ((13, 74, 135), (7, 42, 79), "自己紹介"),
    "shacho":  ((13, 74, 135), (7, 42, 79), "社長の退職金"),
    "staff":   ((18, 110, 100), (8, 62, 56), "従業員の退職金"),
    "hoken":   ((92, 52, 140), (50, 26, 84), "法人保険"),
    "souzoku": ((150, 70, 40), (88, 36, 18), "相続・事業承継"),
    "keiei":   ((48, 60, 80), (22, 28, 40), "経営のお金"),
    "sonae":   ((18, 110, 100), (8, 62, 56), "社長の万一への備え"),
}


def make(dest, theme, lines):
    top, bot, tag = THEMES[theme]
    W, H = 1280, 670
    im = Image.new("RGB", (W, H)); d = ImageDraw.Draw(im)
    for y in range(H):
        k = y / H
        d.line([(0, y), (W, y)], fill=tuple(int(a + (b - a) * k) for a, b in zip(top, bot)))
    ph = Image.open(ROOT / "src/assets/img/daihyo.jpg").convert("RGB").resize((536, 670))
    mask = Image.new("L", ph.size, 255); md = ImageDraw.Draw(mask)
    for x in range(140):
        md.line([(x, 0), (x, 670)], fill=int(255 * x / 140))
    im.paste(ph, (W - 536, 0), mask)
    size = 62
    while max(d.textlength(l, font=ImageFont.truetype(F, size)) for l in lines) > 700:
        size -= 2
    f2 = ImageFont.truetype(F, size)
    d.text((70, 170), tag, font=ImageFont.truetype(F, 34), fill="#ffd27a")
    y = 240
    for ln in lines:
        d.text((70, y), ln, font=f2, fill="white", stroke_width=1, stroke_fill="white"); y += size + 22
    d.text((70, 530), "独立系FP 五十嵐大輔（株式会社DSK）", font=ImageFont.truetype(F, 32), fill="#e6edf5")
    d.rectangle([0, H - 12, W, H], fill="#e2682c")
    im.save(dest, quality=90)


if __name__ == "__main__":
    make(sys.argv[1], sys.argv[2], sys.argv[3:])
