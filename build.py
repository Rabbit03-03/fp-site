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
GA_ID = "G-X73G794F7J"
WEB3_KEY = "35ca5628-eec1-49e4-a5bc-9cf34081bbbd"

ORG_LD = '{"@context": "https://schema.org", "@type": "ProfessionalService", "name": "株式会社DSK", "url": "SITEURL", "foundingDate": "2012-11", "founder": {"@type": "Person", "name": "五十嵐大輔", "jobTitle": "代表取締役"}, "address": {"@type": "PostalAddress", "postalCode": "104-0031", "addressRegion": "東京都", "addressLocality": "中央区", "streetAddress": "京橋2-7-8 2F", "addressCountry": "JP"}, "areaServed": "JP", "sameAs": ["https://www.dsk-real.co.jp/", "https://note.com/dsk_real_50"]}'

LINE_URL = "https://line.me/R/ti/p/@934yeqps"
DL_BANNER = ('<div class="dl-banner"><img src="{{root}}assets/img/checksheet-cover.jpg" alt="" width="84" height="119" loading="lazy">'
             '<div><p><b>【無料PDF】社長のお金 見直しチェックシート</b><br>21の質問で退職金・保険・相続を点検。登録不要です。</p>'
             '<a class="btn" href="{{root}}tool/checksheet.html">無料でダウンロード</a></div></div>')
LINE_CTA = ('<div class="line-cta"><div><b>いきなり相談は、まだ早いかなという方へ</b>'
            '<p>LINEで友だち追加だけでもOKです。気になったことをLINEで気軽に質問できます。</p>'
            '<p class="trust-line">強引な勧誘はしません ・ 全国オンライン対応 ・ 初回60分無料</p></div>'
            f'<a class="btn line" href="{LINE_URL}" rel="noopener">LINEで友だち追加</a></div>')

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         # 表示を止めないよう、フォントは後から読み込む（届くまでは端末の標準フォントで表示）。500は400に寄せて1種類減らす
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700&display=swap" media="print" onload="this.media=\'all\'">'
         '<noscript><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700&display=swap"></noscript>')

HEADER = """<header class="site-head"><div class="wrap">
  <a class="brand" href="{root}index.html"><b>株式会社DSK</b><small>東京の独立系FP ／ 全国の社長のご相談</small></a>
  <nav class="nav" aria-label="メイン">
    <a href="{root}houjin.html">法人のご相談</a>
    <a href="{root}column/houjin-nisa.html">法人NISA</a>
    <a href="{root}column/index.html">コラム</a>
    <a href="{root}profile.html">代表紹介</a>
    <a href="{root}company.html">会社概要</a>
    <a href="{root}yoyaku.html">無料相談</a>
  </nav>
</div></header>"""

FOOTER = """<footer class="site-foot"><div class="wrap">
  <p><b>株式会社DSK</b>　〒104-0031 東京都中央区京橋2-7-8 2F　全国オンライン対応／福岡は毎月1回対面</p>
  <p class="foot-links"><a href="{root}company.html">会社概要</a><a href="{root}houjin.html#faq">よくあるご質問</a><a href="{root}yougo.html">用語集</a><a href="https://www.dsk-real.co.jp/blank-8" rel="noopener">個人情報保護方針</a><a href="{root}seminar.html">無料セミナー</a><a href="https://line.me/R/ti/p/@934yeqps" rel="noopener">LINE公式アカウント</a><a href="https://note.com/dsk_real_50" rel="noopener">note</a><a href="https://www.dsk-real.co.jp/" rel="noopener">個人のお客様向けサイト</a></p>
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


OG_FONT = "/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf"


def og_title(meta):
    return meta.get("list") or meta["title"].split("｜")[0]


def make_og(out, rel, meta):
    """SNSでシェアされたときの見出し画像（1200x630）を作る。"""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return None
    import os
    if not os.path.exists(OG_FONT):
        return None
    name = rel.replace("/", "_").replace(".html", ".png")
    dest = out / "assets/og" / name
    dest.parent.mkdir(parents=True, exist_ok=True)
    W, H = 1200, 630
    im = Image.new("RGB", (W, H), "#0d4a87")
    d = ImageDraw.Draw(im)
    for y in range(H):  # 上から下へ濃くなるグラデーション
        k = y / H
        d.line([(0, y), (W, y)], fill=(int(13 - 6 * k), int(74 - 32 * k), int(135 - 56 * k)))
    d.rectangle([0, H - 14, W, H], fill="#e2682c")
    small = ImageFont.truetype(OG_FONT, 34)
    d.text((80, 70), "株式会社DSK ｜ 社長のお金の相談", font=small, fill="#ffd27a")
    title = og_title(meta)
    size = 64 if len(title) <= 28 else 54
    font = ImageFont.truetype(OG_FONT, size)
    lines, line = [], ""
    for ch in title:
        if d.textlength(line + ch, font=font) > W - 160:
            lines.append(line); line = ch
        else:
            line += ch
    lines.append(line)
    lines = lines[:4]
    y = (H - len(lines) * (size + 22)) // 2 + 10
    for ln in lines:
        d.text((80, y), ln, font=font, fill="#ffffff", stroke_width=1, stroke_fill="#ffffff")
        y += size + 22
    d.text((80, H - 90), "独立系FP 五十嵐大輔 ／ 全国オンライン・初回無料", font=small, fill="#dbe7f5")
    im.save(dest, optimize=True)
    return "assets/og/" + name


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
                      "mtime": p.name})
    return sorted(items, key=lambda i: (i["date"], i["mtime"]), reverse=True)


def column_list_html(items):
    return "\n".join(f'<li><a href="{{{{root}}}}{i["href"]}"><span class="t">{i["title"]}</span>'
                     f'<span class="cat">{i["cat"]}</span></a></li>' for i in items)


# テーマ（カテゴリをまとめた大きな分類）と、関連する無料ツール
THEMES = [
    ("shacho", "社長の退職金", ["社長の退職金"], "利益を社長の退職金に変える準備と、受け取るときの税金。",
     [("tool/taishokukin.html", "退職金の手取りシミュレーター"), ("tool/taishokukin-hayami.html", "退職金の手取り早見表")]),
    ("staff", "従業員の退職金・福利厚生", ["従業員の退職金"], "中退共・企業型DC・養老保険など、社員のための制度づくり。",
     [("tool/shindan.html", "1分でわかる無料診断")]),
    ("hoken", "法人保険・事業保障", ["法人保険", "事業保障"], "社長に万一のときの備えと、加入中の保険の見直し。",
     [("tool/hosyougaku.html", "必要保障額シミュレーター")]),
    ("souzoku", "相続・事業承継", ["相続・事業承継", "相続税対策"], "自社株、相続税、後継者へのバトンタッチ。",
     [("tool/souzokuzei.html", "相続税かんたん試算"), ("tool/souzokuzei-hayami.html", "相続税の早見表")]),
    ("keiei", "経営のお金", ["経営のお金"], "資金繰り、節税、会社のお金の使い方。", []),
]


# 記事の途中の相談案内（定型文のときだけ、テーマに合わせた一文に差し替える）
CTA_TEXT = {
    "shacho": "利益と在任年数から、社長の退職金をいくら・どう準備できるか一緒に試算します。",
    "staff": "従業員の人数と給与から、御社に合う退職金・福利厚生の組み合わせを一緒に考えます。",
    "hoken": "加入中の保険証券を見ながら、保険の目的と解約したときの戻り額を一緒に整理します。",
    "souzoku": "自社株や保険を含めて、相続税の目安と納税資金を一緒に整理します。",
    "keiei": "決算書を見ながら、会社と社長個人にお金を残す方法を一緒に考えます。",
}


def theme_of(cat):
    for t in THEMES:
        if cat in t[2]:
            return t
    return THEMES[-1]


def column_hubs_html(items):
    out = ['<nav class="hub-nav" aria-label="テーマ">' + "".join(
        f'<a href="#{t[0]}">{t[1]}</a>' for t in THEMES if any(theme_of(i["cat"]) is t for i in items)) + "</nav>"]
    for t in THEMES:
        its = [i for i in items if theme_of(i["cat"]) is t]
        if not its:
            continue
        tools = "".join(f'<li><a href="{{{{root}}}}{h}"><span class="t">{n}</span><span class="cat">無料ツール</span></a></li>' for h, n in t[4])
        out.append(f'<section class="hub" id="{t[0]}"><h2>{t[1]}</h2><p>{t[3]}</p>'
                   f'<ul class="col-list">{column_list_html(its)}{tools}</ul></section>')
    return "\n".join(out)


def related_html(rel, body):
    """記事の最後に「あわせて読みたい」を入れる（同じテーマを優先）。"""
    items = column_items()
    me = next((i for i in items if i["href"] == rel), None)
    if not me:
        return ""
    t = theme_of(me["cat"])
    same = [i for i in items if i is not me and theme_of(i["cat"]) is t]
    other = [i for i in items if i is not me and theme_of(i["cat"]) is not t]
    picks = (same + other)[:4]
    tools = "".join(f'<li><a href="{{{{root}}}}{h}"><span class="t">{n}</span><span class="cat">無料ツール</span></a></li>' for h, n in t[4] if h not in body)
    return (f'<section class="related"><h2>あわせて読みたい</h2><ul class="col-list">{column_list_html(picks)}{tools}</ul>'
            f'<p class="note"><a href="{{{{root}}}}column/index.html#{t[0]}">「{t[1]}」の記事をすべて見る</a></p></section>\n')


import hashlib
CSS_VER = hashlib.md5((SRC / "assets/style.css").read_bytes()).hexdigest()[:8]


def render(rel, meta, body, bare, og=None):
    if rel.startswith("column/") and rel != "column/index.html" and '<aside class="author">' in body:
        body = body.replace('<aside class="author">', related_html(rel, body) + DL_BANNER + '\n    <aside class="author">', 1)
        cat = re.search(r"コラム ／ ([^<]+)</p>", body)
        if cat:
            t = theme_of(cat.group(1).strip())
            body = re.sub(r'(<div class="inline-cta">\s*<p>)(?:読んで気になったことは、)?オンラインで60分、無料でご相談いただけます。[^<]*(</p>)',
                          lambda m: m.group(1) + CTA_TEXT[t[0]] + "オンラインで60分、初回は無料です。全国どこからでもご利用いただけます。" + m.group(2), body)
            body = body.replace(f"／ コラム ／ {cat.group(1)}</p>",
                                f'／ <a href="{{{{root}}}}column/index.html">コラム</a> ／ <a href="{{{{root}}}}column/index.html#{t[0]}">{cat.group(1)}</a></p>', 1)
    if meta.get("updated") and '<time datetime="' in body:
        y, m, d = meta["updated"].split("-")
        body = re.sub(r'(公開：<time datetime="[0-9-]+">[^<]+</time></span>)',
                      lambda mm: mm.group(1) + f'<span>更新：<time datetime="{meta["updated"]}">{y}年{int(m)}月{int(d)}日</time></span>', body, count=1)
    if "{{column_" in body:
        items = column_items()
        body = body.replace("{{column_hubs}}", column_hubs_html(items))
        body = body.replace("{{column_list}}", column_list_html(items))
        body = re.sub(r"\{\{column_latest:(\d+)\}\}", lambda m: column_list_html(items[:int(m.group(1))]), body)
    depth = rel.count("/")
    root = SITE_URL if rel == "404.html" else "../" * depth
    body = re.sub(r"\{\{include:([\w-]+)\}\}", lambda m: (SRC / "partials" / (m.group(1) + ".html")).read_text(encoding="utf-8"), body)
    body = body.replace("{{dl_banner}}", DL_BANNER)
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
            + ('<meta name="robots" content="noindex">\n' if rel.endswith("thanks.html") or rel == "404.html" else "")
            + f'<link rel="canonical" href="{url}">\n'
            f'<meta property="og:title" content="{meta["title"]}">\n'
            f'<meta property="og:description" content="{meta["description"]}">\n'
            f'<meta property="og:type" content="{"article" if "column/" in rel else "website"}">\n'
            f'<meta property="og:url" content="{url}">\n'
            + (f'<meta property="og:image" content="{SITE_URL}{og}">\n<meta name="twitter:card" content="summary_large_image">\n' if og else "")
            + '<meta property="og:site_name" content="株式会社DSK">\n<meta property="og:locale" content="ja_JP">\n'
            + f'<link rel="icon" href="{root}assets/img/favicon.svg" type="image/svg+xml">\n<link rel="icon" href="{root}assets/img/favicon-32.png" sizes="32x32">\n<link rel="apple-touch-icon" href="{root}assets/img/apple-touch-icon.png">\n<meta name="theme-color" content="#0d4a87">\n'
            + f'{FONTS}\n<link rel="stylesheet" href="{root}assets/style.css?v={CSS_VER}">\n'
            f'<script type="application/ld+json">{ORG_LD.replace("SITEURL", SITE_URL)}</script>')
    if rel.startswith("column/") and rel != "column/index.html":
        import json
        date = re.search(r'<time datetime="([0-9-]+)"', body)
        cat = re.search(r"コラム ／ ([^<]+)</p>", body)
        art = {"@context": "https://schema.org", "@type": "BlogPosting", "headline": og_title(meta),
               "description": meta["description"], "mainEntityOfPage": url,
               "author": {"@type": "Person", "name": "五十嵐 大輔", "jobTitle": "代表取締役・AFP", "url": SITE_URL + "profile.html"},
               "publisher": {"@type": "Organization", "name": "株式会社DSK", "url": SITE_URL}}
        if date:
            art["datePublished"] = date.group(1)
            art["dateModified"] = meta.get("updated", date.group(1))
        if og:
            art["image"] = SITE_URL + og
        crumbs = [("トップ", SITE_URL), ("コラム", SITE_URL + "column/")]
        if cat:
            crumbs.append((cat.group(1).strip(), None))
        crumbs.append((og_title(meta), url))
        bc = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            dict({"@type": "ListItem", "position": i + 1, "name": n}, **({"item": u} if u else {})) for i, (n, u) in enumerate(crumbs)]}
        head += "\n" + "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in (art, bc))
    if GA_ID and not bare:
        head += (f'\n<script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>'
                 "<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}"
                 f"gtag('js',new Date());gtag('config','{GA_ID}');"
                 "document.addEventListener('click',function(e){var a=e.target.closest&&e.target.closest('a[href$=\".pdf\"]');"
                 "if(a)gtag('event','pdf_download',{file_name:a.getAttribute('href').split('/').pop(),page_path:location.pathname});"
                 # ボタンのクリックを場所ごとに記録（GAの「イベント」→ cta_click で、cta_place 別に見られる）
                 "var b=e.target.closest&&e.target.closest('a.btn');if(b){var w=b.closest('.inline-cta,.line-cta,.mobile-bar,.dl-banner,.hero,.cta,.related,.sim-result,.site-head');"
                 "gtag('event','cta_click',{cta_place:w?w.className.split(' ')[0]:'other',cta_text:b.textContent.trim().slice(0,30),link_url:b.getAttribute('href'),page_path:location.pathname});}});</script>")
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
    shutil.copytree(SRC / "assets/dl", out / "assets/dl")
    for f in SRC.glob("google*.html"):  # Search Console の所有権確認ファイル
        shutil.copy(f, out / f.name)
    pages = []
    for p in sorted(SRC.rglob("*.body.html")):
        rel = str(p.relative_to(SRC)).replace(".body.html", ".html")
        meta, body = parse(p)
        dest = out / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        og = None if preview or rel.endswith("thanks.html") or rel == "404.html" else make_og(out, rel, meta)
        dest.write_text(render(rel, meta, body, bare=preview and rel == "index.html", og=og), encoding="utf-8")
        date = meta.get("updated") or (re.search(r'<time datetime="([0-9-]+)"', body) or [None, None])[1]
        pages.append((rel, date))
    if not preview:
        (out / ".nojekyll").write_text("")
        (out / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}sitemap.xml\n")
        urls = "".join(f"  <url><loc>{SITE_URL}{r.replace('index.html', '')}</loc>" + (f"<lastmod>{d}</lastmod>" if d else "") + "</url>\n"
                       for r, d in pages if not r.endswith('thanks.html') and r != "404.html")
        (out / "sitemap.xml").write_text(
            '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + urls + "</urlset>\n")
    print(out, [r for r, _ in pages])


if __name__ == "__main__":
    main()
