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
# Web3Forms のアクセスキー（公開してよいキー）。入っていれば FormSubmit の代わりに使う。
# Googleアナリティクス4 の測定ID（G-で始まる）。入っていれば全ページにタグを入れる。
GA_ID = ""
WEB3_KEY = "35ca5628-eec1-49e4-a5bc-9cf34081bbbd"

ORG_LD = '{"@context": "https://schema.org", "@type": "ProfessionalService", "name": "株式会社DSK", "url": "SITEURL", "foundingDate": "2012-11", "founder": {"@type": "Person", "name": "五十嵐大輔", "jobTitle": "代表取締役"}, "address": {"@type": "PostalAddress", "postalCode": "104-0031", "addressRegion": "東京都", "addressLocality": "中央区", "streetAddress": "京橋2-7-8 2F", "addressCountry": "JP"}, "areaServed": "JP", "sameAs": ["https://www.dsk-real.co.jp/"]}'

LINE_URL = "https://lin.ee/SuhoSRC"
LINE_CTA = ('<div class="line-cta"><div><b>いきなり相談は、まだ早いかなという方へ</b>'
            '<p>LINEで友だち追加だけでもOKです。気になったことをLINEで気軽に質問できます。</p></div>'
            f'<a class="btn line" href="{LINE_URL}" rel="noopener">LINEで友だち追加</a></div>')

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700&display=swap">')

HEADER = """<header class="site-head"><div class="wrap">
  <a class="brand" href="{root}index.html"><b>株式会社DSK</b><small>東京の独立系FP ／ 全国の社長のご相談</small></a>
  <nav class="nav" aria-label="メイン">
    <a href="{root}houjin.html">法人のご相談</a>
    <a href="{root}column/houjin-nisa.html">法人NISA</a>
    <a href="{root}column/index.html">コラム</a>
    <a href="{root}index.html#profile">代表紹介</a>
    <a href="{root}company.html">会社概要</a>
    <a href="{root}yoyaku.html">無料相談</a>
  </nav>
</div></header>"""

FOOTER = """<footer class="site-foot"><div class="wrap">
  <p><b>株式会社DSK</b>　〒104-0031 東京都中央区京橋2-7-8 2F　全国オンライン対応／福岡は毎月1回対面</p>
  <p class="foot-links"><a href="{root}company.html">会社概要</a><a href="{root}houjin.html#faq">よくあるご質問</a><a href="https://www.dsk-real.co.jp/blank-8" rel="noopener">個人情報保護方針</a><a href="{root}seminar.html">無料セミナー</a><a href="https://lin.ee/SuhoSRC" rel="noopener">LINE公式アカウント</a><a href="https://www.dsk-real.co.jp/" rel="noopener">個人のお客様向けサイト</a></p>
  <p>当サイトの情報は一般的な内容です。個別の税務判断は税理士にご確認ください。</p>
  <p>&copy; 2026 株式会社DSK</p>
</div></footer>
<div class="mobile-bar"><a class="btn" href="{root}yoyaku.html">無料相談を予約</a></div>"""


ICONS = {
    "people": '<circle cx="9" cy="8" r="3.5"/><circle cx="17" cy="9" r="2.5"/><path d="M2.5 20c0-3.6 2.9-6 6.5-6s6.5 2.4 6.5 6"/><path d="M15.5 14.2c3.2-.4 6 1.6 6 5.3"/>',
    "briefcase": '<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M8 7V5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/><path d="M3 12h18"/>',
    "house": '<path d="M3 11l9-7 9 7"/><path d="M5 10v10h14V10"/><path d="M10 20v-5h4v5"/>',
    "shield": '<path d="M12 3l8 3v6c0 4.5-3.4 8-8 9-4.6-1-8-4.5-8-9V6z"/><path d="M8.5 12l2.5 2.5 4.5-5"/>',
    "doc": '<path d="M6 3h9l4 4v14H6z"/><path d="M14 3v5h5"/><path d="M9 13h6M9 17h4"/>',
    "check": '<path d="M4 12.5l5 5 11-11"/>',
    "monitor": '<rect x="3" y="4" width="18" height="12" rx="2"/><path d="M8 20h8M12 16v4"/>',
    "pin": '<path d="M12 21s-7-6.2-7-11.5a7 7 0 0 1 14 0C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/>',
    "yen": '<circle cx="12" cy="12" r="9"/><path d="M8.5 7l3.5 5 3.5-5M12 12v6M9 13h6M9 16h6"/>',
    "handshake": '<path d="M3 12l4-4 4 2 3-2 4 4-6 6z"/><path d="M11 10l-3 3 2 2"/>',
}


def icon_svg(name):
    return (f'<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[name]}</svg>')


def parse(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"<!--\s*(.*?)-->\s*", text, re.S)
    meta = dict(line.split(": ", 1) for line in m.group(1).strip().splitlines())
    return meta, text[m.end():]


def column_items():
    """src/column/*.body.html から一覧用の情報を集める（新しい順）。"""
    items = []
    for p in SRC.glob("column/*.body.html"):
        if p.name == "index.body.html":
            continue
        meta, body = parse(p)
        cat = re.search(r"コラム ／ ([^<]+)</p>", body)
        date = re.search(r'<time datetime="([0-9-]+)"', body)
        items.append({"href": "column/" + p.name.replace(".body.html", ".html"),
                      "title": meta.get("list") or meta["title"].split("｜")[0],
                      "cat": cat.group(1).strip() if cat else "コラム",
                      "date": date.group(1) if date else "",
                      "mtime": p.stat().st_mtime})
    return sorted(items, key=lambda i: (i["date"], i["mtime"]), reverse=True)


def column_list_html(items):
    return "\n".join(f'<li><a href="{{{{root}}}}{i["href"]}"><span class="t">{i["title"]}</span>'
                     f'<span class="cat">{i["cat"]}</span></a></li>' for i in items)


def render(rel, meta, body, bare):
    if "{{column_" in body:
        items = column_items()
        body = body.replace("{{column_list}}", column_list_html(items))
        body = re.sub(r"\{\{column_latest:(\d+)\}\}", lambda m: column_list_html(items[:int(m.group(1))]), body)
    depth = rel.count("/")
    root = "../" * depth
    body = body.replace("{{root}}", root).replace("{{site_url}}", SITE_URL).replace("{{line_cta}}", LINE_CTA)
    body = re.sub(r"\{\{icon:(\w+)\}\}", lambda m: icon_svg(m.group(1)), body)
    def hidden(m):
        subject, nxt = m.group(1), SITE_URL + m.group(2)
        if WEB3_KEY:
            return (f'<input type="hidden" name="access_key" value="{WEB3_KEY}">'
                    f'<input type="hidden" name="subject" value="{subject}">'
                    '<input type="hidden" name="from_name" value="DSK website">'
                    f'<input type="hidden" name="redirect" value="{nxt}">'
                    '<input type="checkbox" name="botcheck" class="hp" tabindex="-1" autocomplete="off" aria-hidden="true">')
        return (f'<input type="hidden" name="_subject" value="{subject}">'
                f'<input type="hidden" name="_next" value="{nxt}">'
                '<input type="hidden" name="_template" value="table">'
                '<input type="text" name="_honey" class="hp" tabindex="-1" autocomplete="off" aria-hidden="true">')
    body = re.sub(r"\{\{form_hidden:([^|]+)\|([^}]+)\}\}", hidden, body)
    if WEB3_KEY:
        body = body.replace("{{form_action}}", "https://api.web3forms.com/submit").replace("{{form_notice}}", "")
    elif FORM_TO:
        body = body.replace("{{form_action}}", "https://formsubmit.co/" + FORM_TO).replace("{{form_notice}}", "")
    else:
        body = body.replace("{{form_action}}", "#").replace(
            "{{form_notice}}", '<p class="callout">準備中：送信先メールアドレスの設定後にご利用いただけます。</p>')
    url = SITE_URL + rel.replace("index.html", "")
    head = (f'<title>{meta["title"]}</title>\n'
            f'<meta name="description" content="{meta["description"]}">\n'
            + ('<meta name="robots" content="noindex">\n' if rel.endswith("thanks.html") else "")
            + f'<link rel="canonical" href="{url}">\n'
            f'<meta property="og:title" content="{meta["title"]}">\n'
            f'<meta property="og:description" content="{meta["description"]}">\n'
            f'<meta property="og:type" content="{"article" if "column/" in rel else "website"}">\n'
            f'<meta property="og:url" content="{url}">\n'
            f'{FONTS}\n<link rel="stylesheet" href="{root}assets/style.css">\n'
            f'<script type="application/ld+json">{ORG_LD.replace("SITEURL", SITE_URL)}</script>')
    if GA_ID and not bare:
        head += (f'\n<script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>'
                 "<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}"
                 f"gtag('js',new Date());gtag('config','{GA_ID}');</script>")
    inner = HEADER.format(root=root) + "\n" + body + FOOTER.format(root=root)
    if bare:
        head = head.replace(f'<title>{meta["title"]}</title>', "<title>社長向けFPサイト</title>", 1)
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
    shutil.copytree(SRC / "assets/img", out / "assets/img")
    for f in SRC.glob("google*.html"):  # Search Console の所有権確認ファイル
        shutil.copy(f, out / f.name)
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
        urls = "".join(f"  <url><loc>{SITE_URL}{r.replace('index.html', '')}</loc></url>\n" for r in pages if not r.endswith('thanks.html'))
        (out / "sitemap.xml").write_text(
            '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + urls + "</urlset>\n")
    print(out, pages)


if __name__ == "__main__":
    main()
