"""退職金・相続税の早見表ページ（src/tool/*-hayami.body.html）を作る。
税率が変わったらこのファイルを直して python3 scripts/gen_hayami.py を実行する。"""
import math
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent / "src" / "tool"

# 所得税の速算表（課税所得の上限, 税率, 控除額）。復興特別所得税2.1%を加える。
INC = [(1949000, .05, 0), (3299000, .10, 97500), (6949000, .20, 427500), (8999000, .23, 636000),
       (17999000, .33, 1536000), (39999000, .40, 2796000), (math.inf, .45, 4796000)]
# 相続税の速算表（万円）
SOZ = [(1000, .10, 0), (3000, .15, 50), (5000, .20, 200), (10000, .30, 700), (20000, .40, 1700),
       (30000, .45, 2700), (60000, .50, 4200), (math.inf, .55, 7200)]


def retire_net(amount, years, officer):
    ded = max(800000, 400000 * years) if years <= 20 else 8000000 + 700000 * (years - 20)
    over = max(0, amount - ded)
    if years <= 5 and officer:
        taxable = over
    elif years <= 5 and over > 3000000:
        taxable = 1500000 + (over - 3000000)
    else:
        taxable = over / 2
    taxable = math.floor(taxable / 1000) * 1000
    inc = next(math.floor(max(0, taxable * r - c) * 1.021) for lim, r, c in INC if taxable <= lim)
    res = math.floor(taxable * .04 / 100) * 100 + math.floor(taxable * .06 / 100) * 100
    return amount - inc - res, inc + res


def souzoku(assets, spouse, kids):
    n = kids + (1 if spouse else 0)
    base = max(0, assets - (3000 + 600 * n))
    shares = ([.5] + [.5 / kids] * kids) if spouse else [1 / kids] * kids
    total = sum(next(max(0, math.floor(base * s * 10) / 10 * r - c) for lim, r, c in SOZ if math.floor(base * s * 10) / 10 <= lim) for s in shares)
    total = math.floor(total * 100) / 100
    return total, (total / 2 if spouse else total)


def man(yen):
    return f"{round(yen / 10000):,}"


FOOT = """
    <div class="inline-cta">
      <p>{cta}</p>
      <div class="btn-row"><a class="btn" href="{{{{root}}}}yoyaku.html">無料相談を予約する</a><a class="btn ghost" href="{{{{root}}}}{tool}">自分の数字で計算する</a></div>
    </div>

    {{{{line_cta}}}}
"""


def retire_page():
    amounts = [1000, 2000, 3000, 4000, 5000, 6000, 8000, 10000]
    years = [10, 15, 20, 25, 30, 35]
    rows = []
    for a in amounts:
        cells = []
        for y in years:
            net, tax = retire_net(a * 10000, y, True)
            cells.append(f'<td class="n">{man(net)}<small>税 {man(tax)}</small></td>')
        rows.append(f'<tr><th scope="row">{a:,}万円</th>{"".join(cells)}</tr>')
    head = "".join(f'<th scope="col">{y}年</th>' for y in years)
    ex_net, ex_tax = retire_net(50000000, 25, True)
    return f"""<!--
title: 退職金の手取り早見表（役員退職金・金額×勤続年数）｜株式会社DSK
list: 退職金の手取り早見表（金額×勤続年数）
description: 退職金1,000万円から1億円まで、勤続・在任10年から35年の手取り額と税金（所得税・住民税）を一覧表にしました。役員退職金の手取りの目安がひと目で分かります。自分の金額はシミュレーターで計算できます。
-->
<main>
  <div class="article">
    <p class="crumbs"><a href="{{{{root}}}}index.html">トップ</a> ／ 退職金の手取り早見表</p>
    <h1>退職金の手取り早見表</h1>
    <div class="callout">
      <p><strong>この表の要点</strong></p>
      <ul>
        <li>たとえば退職金5,000万円・在任25年なら、手取りは約{man(ex_net)}万円（税金は約{man(ex_tax)}万円）です。</li>
        <li>同じ金額でも、勤続年数が長いほど税金は小さくなります。</li>
        <li>自分の金額と年数は<a href="{{{{root}}}}tool/taishokukin.html">退職金の手取りシミュレーター</a>で計算できます。</li>
      </ul>
    </div>

    <h2>手取り額の一覧（単位：万円）</h2>
    <p>上の数字が手取り、下の小さい数字が税金（所得税＋復興特別所得税＋住民税）です。</p>
    <div class="table-scroll">
      <table class="ledger hayami">
        <thead><tr><th scope="col">退職金 ＼ 年数</th>{head}</tr></thead>
        <tbody>
          {"".join(rows)}
        </tbody>
      </table>
    </div>
    <p class="note">この表は、在任・勤続6年以上で、ほかに退職金を受け取っていない場合の概算です。在任5年以下の役員は、控除後の額を2分の1にする計算が使えないため、税金が大きくなります。</p>
{FOOT.format(cta="この退職金を、会社の利益からどう準備するか。御社の決算書で無料で試算します。", tool="tool/taishokukin.html")}
    <h2>計算のしかた</h2>
    <div class="table-scroll">
      <table class="ledger">
        <tbody>
          <tr><th scope="row">1. 退職所得控除</th><td>20年以下：40万円×年数（最低80万円）／20年超：800万円＋70万円×（年数−20年）</td></tr>
          <tr><th scope="row">2. 課税退職所得</th><td>（退職金 − 控除）× 1/2（千円未満切り捨て）</td></tr>
          <tr><th scope="row">3. 税金</th><td>所得税の速算表で計算し、復興特別所得税2.1%と住民税10%を加える</td></tr>
        </tbody>
      </table>
    </div>
    <p>退職金は、ほかの所得と分けて計算し、さらに2分の1にするため、同じ額を給与で受け取るより税負担が軽くなります。役員退職金の決め方は<a href="{{{{root}}}}column/yakuin-taishokukin-souba.html">役員退職金の相場の記事</a>、準備の方法は<a href="{{{{root}}}}column/houjin-nisa.html">法人NISAの記事</a>をご覧ください。</p>
    <p class="note">出典：国税庁 タックスアンサー <a href="https://www.nta.go.jp/taxes/shiraberu/taxanswer/shotoku/1420.htm" rel="noopener">No.1420 退職金を受け取ったとき（退職所得）</a>・<a href="https://www.nta.go.jp/taxes/shiraberu/taxanswer/shotoku/2260.htm" rel="noopener">No.2260 所得税の税率</a>。実際の税額は税理士にご確認ください。税制は2026年9月時点のものです。</p>
  </div>
</main>
"""


def souzoku_page():
    assets = [5000, 8000, 10000, 15000, 20000, 30000, 50000, 100000]
    rows = []
    for a in assets:
        cells = []
        for spouse, kids in [(True, 1), (True, 2), (True, 3), (False, 1), (False, 2), (False, 3)]:
            total, pay = souzoku(a, spouse, kids)
            cells.append(f'<td class="n">{round(pay):,}</td>')
        rows.append(f'<tr><th scope="row">{a:,}万円</th>{"".join(cells)}</tr>')
    ex_total, ex_pay = souzoku(20000, True, 2)
    return f"""<!--
title: 相続税の早見表（財産額×家族構成）｜配偶者・子どもの人数別｜株式会社DSK
list: 相続税の早見表（財産額×家族構成）
description: 財産5,000万円から10億円まで、配偶者の有無と子どもの人数別に、家族が納める相続税の目安を一覧表にしました。配偶者の税額軽減を使った場合の目安です。自分の数字は相続税かんたん試算で計算できます。
-->
<main>
  <div class="article">
    <p class="crumbs"><a href="{{{{root}}}}index.html">トップ</a> ／ 相続税の早見表</p>
    <h1>相続税の早見表</h1>
    <div class="callout">
      <p><strong>この表の要点</strong></p>
      <ul>
        <li>たとえば財産2億円・配偶者と子ども2人なら、家族が納める相続税の目安は約{round(ex_pay):,}万円です。</li>
        <li>配偶者がいない場合は、同じ財産でも相続税が大きく増えます。</li>
        <li>生命保険金や死亡退職金を含めた計算は<a href="{{{{root}}}}tool/souzokuzei.html">相続税かんたん試算</a>でできます。</li>
      </ul>
    </div>

    <h2>家族が納める相続税の目安（単位：万円）</h2>
    <div class="table-scroll">
      <table class="ledger hayami">
        <thead>
          <tr><th scope="col" rowspan="2">財産の合計</th><th scope="col" colspan="3">配偶者あり</th><th scope="col" colspan="3">配偶者なし</th></tr>
          <tr><th scope="col">子1人</th><th scope="col">子2人</th><th scope="col">子3人</th><th scope="col">子1人</th><th scope="col">子2人</th><th scope="col">子3人</th></tr>
        </thead>
        <tbody>
          {"".join(rows)}
        </tbody>
      </table>
    </div>
    <p class="note">配偶者ありは、配偶者が法定相続分（2分の1）を受け取り、配偶者の税額軽減を使った場合の、家族全体の納税額です。配偶者の次の相続（二次相続）でかかる税金は含みません。財産は借入などの債務を引いた額で、自社株・不動産の評価、小規模宅地等の特例、生前贈与の加算は含みません。</p>
{FOOT.format(cta="自社株の評価や、生命保険・退職金を使った納税資金の準備まで、無料で一緒に試算します。", tool="tool/souzokuzei.html")}
    <h2>計算のしかた</h2>
    <div class="table-scroll">
      <table class="ledger">
        <tbody>
          <tr><th scope="row">1. 基礎控除</th><td>3,000万円 ＋ 600万円 × 法定相続人の数</td></tr>
          <tr><th scope="row">2. 法定相続分で分ける</th><td>配偶者と子：配偶者2分の1、子は残りを人数で等分</td></tr>
          <tr><th scope="row">3. 税率をかけて合計</th><td>1人ずつ速算表で計算し、合計が相続税の総額</td></tr>
        </tbody>
      </table>
    </div>
    <p>相続税の準備は、自社株の評価と納税資金がポイントです。<a href="{{{{root}}}}column/jisha-kabu-hyouka.html">自社株の評価の記事</a>と<a href="{{{{root}}}}column/seimeihoken-souzoku.html">生命保険を使った相続対策の記事</a>もあわせてご覧ください。</p>
    <p class="note">出典：国税庁 タックスアンサー <a href="https://www.nta.go.jp/taxes/shiraberu/taxanswer/sozoku/4152.htm" rel="noopener">No.4152</a>・<a href="https://www.nta.go.jp/taxes/shiraberu/taxanswer/sozoku/4155.htm" rel="noopener">No.4155</a>・<a href="https://www.nta.go.jp/taxes/shiraberu/taxanswer/sozoku/4158.htm" rel="noopener">No.4158</a>。実際の税額は税理士にご確認ください。税制は2026年9月時点のものです。</p>
  </div>
</main>
"""


if __name__ == "__main__":
    (SRC / "taishokukin-hayami.body.html").write_text(retire_page(), encoding="utf-8")
    (SRC / "souzokuzei-hayami.body.html").write_text(souzoku_page(), encoding="utf-8")
    print("ok")
