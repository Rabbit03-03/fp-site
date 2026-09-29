"""src/*.body.html にヘッダー・フッターを付けて site/ に書き出す。

python3 build.py            -> docs/ (GitHub Pages 公開用、完全なHTML)
python3 build.py --preview  -> preview/ (Claudeのプレビュー用。index.html だけ doctype/head なし)
"""
import pathlib, re, shutil, sys

ROOT = pathlib.Path(__file__).parent
SRC = ROOT / "src"
SITE_URL = "https://rabbit03-03.github.io/fp-site/"  # 独自ドメインが決まったら差し替え
# 予約フォームの送信先メール（FormSubmit.co 経由）。初回送信時に確認メールが届くので承認する。
FORM_TO = "50dskreal@gmail.com"

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=BIZ+UDGothic&family=BIZ+UDPGothic:wght@400;700&family=Shippori+Mincho+B1:wght@700&display=swap">')

HEADER = """<header class="site-head"><div class="wrap">
  <a class="brand" href="{root}index.html"><b>株式会社DSK</b><small>東京の独立系FP ／ 福岡の経営者のご相談</small></a>
  <nav class="nav" aria-label="メイン">
    <a href="{root}houjin.html">法人のご相談</a>
    <a href="{root}column/houjin-nisa.html">法人NISA</a>
    <a href="{root}index.html#profile">プロフィール</a>
    <a href="{root}yoyaku.html">無料相談</a>
  </nav>
</div></header>"""

FOOTER = """<footer class="site-foot"><div class="wrap">
  <p><b>株式会社DSK</b>　〒104-0031 東京都中央区京橋2-7-8 2F　全国オンライン対応／福岡は毎月1回対面</p>
  <p>当サイトの情報は一般的な内容です。個別の税務判断は税理士にご確認ください。</p>
  <p>&copy; 2026 株式会社DSK</p>
</div></footer>
<div class="mobile-bar"><a class="btn" href="{root}yoyaku.html">無料相談を予約</a></div>"""


def parse(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"<!--\s*(.*?)-->\s*", text, re.S)
    meta = dict(line.split(": ", 1) for line in m.group(1).strip().splitlines())
    return meta, text[m.end():]


def render(rel, meta, body, bare):
    depth = rel.count("/")
    root = "../" * depth
    body = body.replace("{{root}}", root).replace("{{site_url}}", SITE_URL)
    if FORM_TO:
        body = body.replace("{{form_action}}", "https://formsubmit.co/" + FORM_TO).replace("{{form_notice}}", "")
    else:
        body = body.replace("{{form_action}}", "#").replace(
            "{{form_notice}}", '<p class="callout">準備中：送信先メールアドレスの設定後にご利用いただけます。</p>')
    url = SITE_URL + rel.replace("index.html", "")
    head = (f'<title>{meta["title"]}</title>\n'
            f'<meta name="description" content="{meta["description"]}">\n'
            + ('<meta name="robots" content="noindex">\n' if rel == "thanks.html" else "")
            + f'<link rel="canonical" href="{url}">\n'
            f'<meta property="og:title" content="{meta["title"]}">\n'
            f'<meta property="og:description" content="{meta["description"]}">\n'
            f'<meta property="og:type" content="{"article" if "column/" in rel else "website"}">\n'
            f'<meta property="og:url" content="{url}">\n'
            f'{FONTS}\n<link rel="stylesheet" href="{root}assets/style.css">')
    inner = HEADER.format(root=root) + "\n" + body + FOOTER.format(root=root)
    if bare:
        head = head.replace(f'<title>{meta["title"]}</title>', "<title>福岡社長向けFPサイト</title>", 1)
        return head + "\n" + inner
    return ('<!doctype html>\n<html lang="ja">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            f'{head}\n</head>\n<body>\n{inner}\n</body>\n</html>\n')


def main():
    preview = "--preview" in sys.argv
    out = ROOT / ("preview" if preview else "docs")
    shutil.rmtree(out, ignore_errors=True)
    (out / "assets").mkdir(parents=True)
    shutil.copy(SRC / "assets/style.css", out / "assets/style.css")
    pages = []
    for p in sorted(SRC.rglob("*.body.html")):
        rel = str(p.relative_to(SRC)).replace(".body.html", ".html")
        meta, body = parse(p)
        dest = out / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(render(rel, meta, body, bare=preview and rel == "index.html"), encoding="utf-8")
        pages.append(rel)
    if not preview:
        (out / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}sitemap.xml\n")
        urls = "".join(f"  <url><loc>{SITE_URL}{r.replace('index.html', '')}</loc></url>\n" for r in pages if r != 'thanks.html')
        (out / "sitemap.xml").write_text(
            '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + urls + "</urlset>\n")
    print(out, pages)


if __name__ == "__main__":
    main()
