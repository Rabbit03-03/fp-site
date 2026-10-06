"""無料PDF「社長のお金 見直しチェックシート」を作る。
python3 scripts/gen_pdf.py → src/assets/dl/shacho-checksheet.pdf（Playwright の Chromium で印刷）"""
import base64, io, subprocess, sys
from pathlib import Path
import qrcode
sys.path.insert(0, str(Path(__file__).resolve().parent))
from gen_hayami import retire_net, souzoku

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://rabbit03-03.github.io/fp-site/"
LINE = "https://line.me/R/ti/p/@934yeqps"
FONT = "/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf"


def qr(url):
    b = io.BytesIO(); qrcode.make(url, box_size=6, border=1).save(b, format="PNG")
    return "data:image/png;base64," + base64.b64encode(b.getvalue()).decode()


def img(p):
    return "data:image/jpeg;base64," + base64.b64encode((ROOT / p).read_bytes()).decode()


def checks(items):
    return "<ul class='ck'>" + "".join(f"<li><span class='box'></span>{t}</li>" for t in items) + "</ul>"


SHACHO = ["自分の退職金を「いくら」「いつ」受け取るか決まっていない",
          "役員退職金規程がない、または5年以上見直していない",
          "決算の直前に、慌てて節税を考えることが多い",
          "役員報酬の額を、退職金とのバランスで決めていない",
          "退職金を受け取ったときの手取り額を計算したことがない"]
HOKEN = ["会社で入っている保険の「目的」を、それぞれ説明できない",
         "解約したときの戻り額が、いつ一番多くなるか知らない",
         "戻り額が一番多い時期と、自分の退任予定がずれている",
         "借入が増えたのに、死亡保障の額を見直していない",
         "2019年7月8日より前か後か、契約日を確認していない",
         "付き合いや勧められるままに入った保険がある",
         "保険証券と解約返戻金の推移表が、すぐに出てこない"]
STAFF = ["従業員の退職金制度がない、または中身をよく知らない",
         "社員の退職が重なったとき、退職金を払えるか分からない",
         "中退共の新規加入助成を知らなかった",
         "採用や定着のために、福利厚生を充実させたい"]
SOZOKU = ["自社株の評価額がいくらか知らない",
          "後継者について、家族とまだ話せていない",
          "自分の相続税がどのくらいかかるか把握していない",
          "相続税を払うお金（納税資金）をどう用意するか決めていない",
          "遺言書を書いていない"]


def build_html():
    photo = img("src/assets/img/daihyo.jpg")
    rrows = "".join(
        f"<tr><th>{a:,}万円</th>" + "".join(f"<td>{round(retire_net(a*10000, y, True)[0]/10000):,}</td>" for y in (15, 20, 25, 30)) + "</tr>"
        for a in (2000, 3000, 5000, 8000, 10000))
    srows = "".join(f"<tr><th>{a:,}万円</th><td>{round(souzoku(a, True, 2)[1]):,}</td><td>{round(souzoku(a, False, 2)[1]):,}</td></tr>"
                    for a in (10000, 20000, 30000, 50000))
    total = len(SHACHO) + len(HOKEN) + len(STAFF) + len(SOZOKU)
    return f"""<!doctype html><html lang="ja"><head><meta charset="utf-8"><style>
@font-face {{ font-family: J; src: url("file://{FONT}"); }}
@page {{ size: A4; margin: 0; }}
* {{ box-sizing: border-box; }}
body {{ margin: 0; font-family: J, sans-serif; color: #1f2a37; font-size: 11.5pt; line-height: 1.7; }}
.page {{ width: 210mm; height: 297mm; padding: 16mm 16mm 14mm; position: relative; page-break-after: always; overflow: hidden; }}
.page:last-child {{ page-break-after: auto; }}
h1 {{ font-size: 30pt; line-height: 1.35; margin: 0; color: #fff; }}
h2 {{ font-size: 16pt; color: #0d4a87; border-left: 6px solid #0d4a87; padding-left: 10px; margin: 0 0 8px; }}
h3 {{ font-size: 12pt; margin: 14px 0 6px; color: #0d4a87; }}
.cover {{ background: linear-gradient(160deg, #1d6bb8, #072a4f); color: #fff; display: flex; flex-direction: column; justify-content: space-between; }}
.cover .eyebrow {{ color: #ffd27a; font-size: 13pt; letter-spacing: .08em; }}
.cover .sub {{ font-size: 14pt; margin-top: 12px; }}
.cover .mark {{ background: #ffe07a; color: #1f2a37; padding: 0 8px; border-radius: 4px; }}
.cover .rep {{ display: flex; gap: 16px; align-items: center; background: rgba(255,255,255,.1); padding: 14px; border-radius: 12px; }}
.cover .rep img {{ width: 110px; height: 138px; object-fit: cover; border-radius: 10px; border: 3px solid #fff; }}
.cover .list {{ font-size: 12.5pt; background: rgba(255,255,255,.08); border-radius: 12px; padding: 14px 18px; }}
.bar {{ position: absolute; left: 0; right: 0; bottom: 0; height: 8px; background: #e2682c; }}
.ck {{ list-style: none; padding: 0; margin: 0; }}
.ck li {{ display: flex; gap: 10px; padding: 6px 4px; border-bottom: 1px dashed #c9d6e6; }}
.box {{ flex: none; width: 15px; height: 15px; border: 2px solid #0d4a87; border-radius: 3px; margin-top: 5px; }}
table {{ border-collapse: collapse; width: 100%; font-size: 10.5pt; margin-top: 6px; }}
th, td {{ border: 1px solid #c9d6e6; padding: 4px 8px; text-align: center; }}
thead th {{ background: #0d4a87; color: #fff; }}
tbody th {{ background: #eef4fb; }}
.note {{ font-size: 8.5pt; color: #5b6b7d; margin-top: 6px; }}
.tip {{ background: #fff8e6; border: 1px solid #f1d58a; border-radius: 8px; padding: 8px 12px; margin-top: 10px; font-size: 10.5pt; }}
.score td {{ text-align: left; }}
.score th {{ width: 30%; }}
.cta {{ display: flex; gap: 14px; margin-top: 12px; }}
.cta div {{ flex: 1; border: 2px solid #0d4a87; border-radius: 12px; padding: 12px; text-align: center; font-size: 10.5pt; }}
.cta img {{ width: 110px; height: 110px; }}
.cta b {{ display: block; font-size: 12.5pt; color: #0d4a87; }}
.foot {{ position: absolute; bottom: 12mm; left: 16mm; right: 16mm; font-size: 8.5pt; color: #5b6b7d; display: flex; justify-content: space-between; }}
.steps {{ display: flex; gap: 8px; margin-top: 6px; }}
.steps div {{ flex: 1; background: #eef4fb; border-radius: 8px; padding: 8px; font-size: 10pt; }}
.steps b {{ display: block; color: #0d4a87; }}
</style></head><body>

<section class="page cover">
  <div>
    <p class="eyebrow">中小企業の社長のための無料チェックシート</p>
    <h1>社長のお金<br>見直しチェックシート</h1>
    <p class="sub">退職金・法人保険・従業員の退職金・相続を<br><span class="mark">15分で点検</span>できます。</p>
  </div>
  <div class="list">
    <p style="margin:0 0 4px"><b>このシートで分かること</b></p>
    1. 社長の退職金の準備は足りているか（{len(SHACHO)}項目）<br>
    2. 会社の保険は今の目的に合っているか（{len(HOKEN)}項目）<br>
    3. 従業員の退職金制度に抜けはないか（{len(STAFF)}項目）<br>
    4. 相続・事業承継の準備は始まっているか（{len(SOZOKU)}項目）<br>
    付録：退職金の手取り早見表・相続税の早見表
  </div>
  <div class="rep">
    <img src="{photo}" alt="">
    <div><b style="font-size:14pt">株式会社DSK 代表取締役　五十嵐 大輔</b><br>
    独立系ファイナンシャルプランナー。AFP、相続診断士、がんファイナンスアドバイザー、証券外務員二種。25歳で起業し資金繰りと財務に悩んだ経験から、社長と同じ目線でご提案します。2012年設立、3,000名以上のご相談実績。</div>
  </div>
  <div class="bar"></div>
</section>

<section class="page">
  <h2>使い方</h2>
  <p>当てはまる項目の□にチェックを入れてください。チェックが多いテーマほど、早めに見直す価値があります。最後のページで合計を数えます。</p>
  <h2 style="margin-top:14px">1. 社長ご自身の退職金</h2>
  {checks(SHACHO)}
  <h3>参考：役員退職金の手取り早見表（単位：万円）</h3>
  <table><thead><tr><th>退職金 ＼ 在任年数</th><th>15年</th><th>20年</th><th>25年</th><th>30年</th></tr></thead><tbody>{rrows}</tbody></table>
  <p class="note">所得税（復興特別所得税を含む）と住民税を引いた手取りの概算。ほかに退職金を受け取っていない場合。出典：国税庁 タックスアンサー No.1420・No.2260。</p>
  <div class="tip"><b>ポイント</b>　退職金は、ほかの所得と分けて計算し、控除後の額をさらに2分の1にするため、同じ額を給与で受け取るより税負担が軽くなります。役員退職金の目安は「最終報酬月額 × 在任年数 × 功績倍率」です。</div>
  <div class="foot"><span>社長のお金 見直しチェックシート</span><span>株式会社DSK</span></div>
</section>

<section class="page">
  <h2>2. 会社の保険（法人保険）</h2>
  {checks(HOKEN)}
  <h3>知っておきたい：2019年の税務ルール変更</h3>
  <table><thead><tr><th>最高解約返戻率</th><th>はじめの一定期間の処理</th></tr></thead><tbody>
  <tr><th>50%以下</th><td>原則、支払った保険料を経費に</td></tr>
  <tr><th>50%超〜70%以下</th><td>40%を資産に計上し、残りを経費に</td></tr>
  <tr><th>70%超〜85%以下</th><td>60%を資産に計上し、残りを経費に</td></tr>
  <tr><th>85%超</th><td>さらに多くを資産に計上</td></tr></tbody></table>
  <p class="note">2019年7月8日以後に契約した定期保険・第三分野保険が対象。出典：国税庁 タックスアンサー No.5364・No.5364-2。</p>
  <div class="tip"><b>用意するもの</b>　保険証券、解約返戻金の推移表（保険会社に頼むと出してもらえます）、直近の決算書。<br><b>注意</b>　合っていないと分かっても、すぐ解約しないでください。解約返戻金は会社の利益になり、入り直すと保険料が上がることがあります。</div>
  <div class="foot"><span>社長のお金 見直しチェックシート</span><span>株式会社DSK</span></div>
</section>

<section class="page">
  <h2>3. 従業員の退職金・福利厚生</h2>
  {checks(STAFF)}
  <div class="tip"><b>中退共の新規加入助成</b>　初めて加入すると、掛金月額の2分の1（1人あたり上限5,000円）を、加入後4か月目から1年間、国が助成します。出典：厚生労働省。</div>
  <h2 style="margin-top:16px">4. 相続・事業承継</h2>
  {checks(SOZOKU)}
  <h3>参考：家族が納める相続税の目安（子ども2人・単位：万円）</h3>
  <table><thead><tr><th>財産の合計</th><th>配偶者あり</th><th>配偶者なし</th></tr></thead><tbody>{srows}</tbody></table>
  <p class="note">配偶者ありは、配偶者が法定相続分を受け取り配偶者の税額軽減を使った場合。自社株・不動産の評価や特例は含みません。出典：国税庁 タックスアンサー No.4152・No.4155・No.4158。</p>
  <div class="foot"><span>社長のお金 見直しチェックシート</span><span>株式会社DSK</span></div>
</section>

<section class="page">
  <h2>結果を数える</h2>
  <p>チェックの合計：　　　　／ {total}項目</p>
  <table class="score"><tbody>
  <tr><th>0〜4個</th><td>よく準備できています。制度は変わるため、数年に一度の見直しがおすすめです。</td></tr>
  <tr><th>5〜10個</th><td>一度、点検しておくと安心です。チェックの多いテーマから始めましょう。</td></tr>
  <tr><th>11個以上</th><td>早めのご相談をおすすめします。対策は、時間があるほど選べる方法が増えます。</td></tr>
  </tbody></table>
  <h3>無料相談の流れ（オンライン60分・全国対応）</h3>
  <div class="steps">
    <div><b>1. 予約</b>サイトかLINEから</div>
    <div><b>2. ヒアリング</b>このシートを見ながら</div>
    <div><b>3. 整理</b>優先順位と数字を一覧に</div>
    <div><b>4. ご提案</b>納得した案だけ実行</div>
  </div>
  <p style="margin-top:10px">強引な勧誘はしません。診断だけのご相談や、顧問税理士の方の同席も歓迎です。2回目以降は1時間22,000円（税込）です。</p>
  <div class="cta">
    <div><img src="{qr(SITE + 'yoyaku.html')}" alt=""><b>無料相談を予約する</b>{SITE}yoyaku.html</div>
    <div><img src="{qr(LINE)}" alt=""><b>LINEで気軽に質問</b>友だち追加だけでもOK</div>
    <div><img src="{qr(SITE)}" alt=""><b>計算ツール・コラム</b>退職金・相続税の試算</div>
  </div>
  <p class="note" style="margin-top:14px">このシートは一般的な情報をまとめたもので、個別の税務判断を行うものではありません。税務の扱いは顧問税理士にご確認ください。内容は2026年9月時点のものです。<br>株式会社DSK　〒104-0031 東京都中央区京橋2-7-8 2F　{SITE}</p>
  <div class="bar"></div>
</section>
</body></html>"""


if __name__ == "__main__":
    out = ROOT / "src/assets/dl"; out.mkdir(parents=True, exist_ok=True)
    html = Path("/tmp/claude-0/checksheet.html"); html.write_text(build_html(), encoding="utf-8")
    js = f"""const {{chromium}}=require('playwright');(async()=>{{const b=await chromium.launch({{executablePath:'/opt/pw-browsers/chromium'}});
const p=await b.newPage();await p.goto('file://{html}');await p.waitForTimeout(500);
await p.pdf({{path:'{out}/shacho-checksheet.pdf',format:'A4',printBackground:true,preferCSSPageSize:true}});await b.close();}})();"""
    npm_root = subprocess.run(["npm", "root", "-g"], capture_output=True, text=True).stdout.strip()
    subprocess.run(["node", "-e", js], check=True, env={"NODE_PATH": npm_root, "PATH": "/usr/bin:/usr/local/bin:/bin"})
    print(out / "shacho-checksheet.pdf")
