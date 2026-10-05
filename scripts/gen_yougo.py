"""用語集ページ src/yougo.body.html を作る。用語を足すときは TERMS に追記して実行する。"""
import json, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE_URL = "https://rabbit03-03.github.io/fp-site/"

# (グループID, グループ名, [(用語, よみ, 説明, くわしい記事)])
TERMS = [
    ("shacho", "社長の退職金", [
        ("役員退職金", "やくいんたいしょくきん", "社長や役員が退任するときに会社が払う退職金。「相当と認められる金額」を超える部分は会社の経費になりません。", "column/yakuin-taishokukin-souba.html"),
        ("功績倍率法", "こうせきばいりつほう", "役員退職金の金額の決め方の1つ。「最終報酬月額 × 在任年数 × 功績倍率」で計算し、中小企業の規程でよく使われます。", "column/yakuin-taishokukin-souba.html"),
        ("役員退職金規程", "やくいんたいしょくきんきてい", "役員退職金の計算方法や支給の手続きを決めておく社内のルール。金額の根拠を説明しやすくなります。", "column/yakuin-taishokukin-kitei.html"),
        ("退職所得控除", "たいしょくしょとくこうじょ", "退職金から差し引ける金額。勤続20年までは1年40万円（最低80万円）、20年を超えた分は1年70万円で増えます。", "column/taishoku-shotoku-koujo.html"),
        ("退職所得の2分の1課税", "たいしょくしょとくのにぶんのいちかぜい", "退職金から退職所得控除を引いた残りの2分の1に税金がかかるしくみ。役員の在任が5年以下だと使えない場合があります。", "column/houjin-nisa.html"),
        ("分掌変更", "ぶんしょうへんこう", "社長から会長になるなど、役員の仕事の内容が大きく変わること。実際に退職したのと同じといえる場合に、退職金を払える可能性があります。", "column/bunsho-henkou-taishokukin.html"),
        ("法人NISA", "ほうじんにーさ", "当社の呼び名で、国のNISA制度とは別物です。会社の利益の一部を法人保険で積み立て、社長の退職金の財源にする考え方を指します。", "column/houjin-nisa.html"),
    ]),
    ("staff", "従業員の退職金・福利厚生", [
        ("中退共", "ちゅうたいきょう", "中小企業退職金共済。会社が掛金を払い、従業員の退職時に機構から本人へ退職金が支払われます。掛金は全額が経費です。", "column/chutaikyo-josei.html"),
        ("企業型DC", "きぎょうがたでぃーしー", "企業型確定拠出年金。会社が掛金を出し、従業員が自分で運用して老後に受け取る制度です。", "column/kigyougata-dc.html"),
        ("iDeCo", "いでこ", "個人型確定拠出年金。社長個人が掛金を出し、掛金の全額が所得控除になります。", "column/ideco-kigyougata-dc.html"),
        ("ハーフタックスプラン", "はーふたっくすぷらん", "養老保険の福利厚生プランの通称。決められた契約の形なら、保険料の2分の1が損金、2分の1が資産計上になります。", "column/half-tax-plan.html"),
        ("普遍的加入", "ふへんてきかにゅう", "福利厚生の保険に、原則として従業員全員を加入させること。役員や一部の社員だけだと、損金になるはずの分が給与として扱われます。", "column/half-tax-plan.html"),
    ]),
    ("hoken", "法人保険", [
        ("損金", "そんきん", "法人税の計算で経費として差し引ける金額。損金が増えると、その年の法人税が減ります。", "column/kessan-mae-setsuzei.html"),
        ("解約返戻金", "かいやくへんれいきん", "保険を途中で解約したときに戻ってくるお金。法人契約なら会社に入ります。", "column/hoken-tsumitatekin.html"),
        ("解約返戻率", "かいやくへんれいりつ", "払った保険料の合計に対して、解約時に戻るお金の割合。2019年の通達改正で、返戻率が高い保険は経費にできる割合が制限されました。", "column/houjin-nisa.html"),
        ("保険積立金", "ほけんつみたてきん", "法人保険の保険料のうち、経費にならず資産として決算書に載る部分。解約時は返戻金との差額がその期の益金または損金になります。", "column/hoken-tsumitatekin.html"),
        ("事業保障", "じぎょうほしょう", "社長に万一のことがあったときに、借入金の返済や運転資金を会社が確保できるように備えること。", "column/jigyou-hoshou.html"),
        ("契約者・被保険者・受取人", "けいやくしゃ・ひほけんしゃ・うけとりにん", "保険料を払う人・保険の対象になる人・保険金を受け取る人。この組み合わせで、かかる税金の種類が変わります。", "column/hoken-uketorinin.html"),
    ]),
    ("souzoku", "相続・事業承継", [
        ("相続税の基礎控除", "そうぞくぜいのきそこうじょ", "相続財産から差し引ける金額で、「3,000万円＋600万円×法定相続人の数」。財産がこれ以下なら相続税はかかりません。", "column/souzokuzei-kiso-koujo.html"),
        ("生命保険の非課税枠", "せいめいほけんのひかぜいわく", "相続人が受け取った死亡保険金のうち「500万円×法定相続人の数」までは相続税がかかりません。", "column/seimeihoken-souzoku.html"),
        ("弔慰金", "ちょういきん", "社長が亡くなったときに会社が遺族に払うお見舞いのお金。業務外の死亡なら普通給与の半年分、業務上なら3年分までが弔慰金として扱われます。", "column/shibou-taishokukin-choiikin.html"),
        ("類似業種比準方式", "るいじぎょうしゅひじゅんほうしき", "自社株の評価方法の1つ。同じ業種の上場会社の株価をもとに、配当・利益・純資産の3つを比べて計算します。", "column/jisha-kabu-hyouka.html"),
        ("純資産価額方式", "じゅんしさんかがくほうしき", "自社株の評価方法の1つ。会社の財産と負債を相続税の評価に置き直し、財産から負債などを引いて計算します。", "column/jisha-kabu-hyouka.html"),
        ("事業承継税制（特例措置）", "じぎょうしょうけいぜいせい", "後継者が自社株を受け継ぐときの贈与税・相続税の全額が猶予される制度。提出期限や要件があります。", "column/jigyou-shoukei-zeisei.html"),
    ]),
    ("keiei", "経営のお金", [
        ("定期同額給与", "ていきどうがくきゅうよ", "毎月など一定の期間ごとに同じ額を払う役員報酬。改定は原則として事業年度の開始から3か月以内です。", "column/yakuin-housyu.html"),
        ("小規模企業共済", "しょうきぼきぎょうきょうさい", "社長個人の退職金を準備する共済。掛金は所得控除になり、受け取り方は一括・分割・併用から選べます。", "column/shoukibo-kyousai-uketori.html"),
        ("経営セーフティ共済", "けいえいせーふてぃきょうさい", "取引先の倒産に備える共済。法人の掛金は損金になり、解約手当金は40か月以上で掛金の全額が戻ります。", "column/safety-kyousai-kaiyaku.html"),
        ("役員貸付金", "やくいんかしつけきん", "会社が社長にお金を貸している状態。決算書に残ると、銀行の評価や認定利息の扱いで不利になることがあります。", "column/yakuin-kashitsukekin.html"),
        ("経営者保証", "けいえいしゃほしょう", "会社の借入金を社長個人が保証すること。経営者保証ガイドラインの3要件を満たすと、保証なしの融資や解除を相談できます。", "column/keiei-hoshou-hazusu.html"),
    ]),
]


def main():
    nav = "".join(f'<a href="#{g}">{name}</a>' for g, name, _ in TERMS)
    secs, ld = [], []
    for g, name, terms in TERMS:
        items = "".join(
            f'<div class="term" id="{g}-{i}"><dt>{t}<small>{y}</small></dt><dd>{d}'
            f' <a href="{{{{root}}}}{href}">くわしく読む</a></dd></div>'
            for i, (t, y, d, href) in enumerate(terms))
        secs.append(f'    <section class="hub" id="{g}"><h2>{name}</h2><dl class="glossary">{items}</dl></section>')
        ld += [{"@type": "DefinedTerm", "name": t, "description": d, "url": SITE_URL + href} for t, y, d, href in terms]
    n = sum(len(x[2]) for x in TERMS)
    data = {"@context": "https://schema.org", "@type": "DefinedTermSet", "name": "社長のお金の用語集", "hasDefinedTerm": ld}
    body = f"""<!--
title: 社長のお金の用語集｜退職金・法人保険・相続の言葉をやさしく解説｜株式会社DSK
description: 役員退職金、功績倍率、退職所得控除、中退共、解約返戻率、相続税の基礎控除など、社長のお金の相談でよく出てくる用語{n}語を、1〜2文でやさしく解説します。
-->
<main>
  <div class="article">
    <p class="crumbs"><a href="{{{{root}}}}index.html">トップ</a> ／ <a href="{{{{root}}}}column/index.html">コラム</a> ／ 用語集</p>
    <h1>社長のお金の用語集</h1>
    <p>退職金・保険・相続のご相談でよく出てくる言葉を、短く説明しています。くわしい内容は、各用語のリンク先のコラムでご覧ください。</p>
    <nav class="hub-nav" aria-label="分類">{nav}</nav>
{chr(10).join(secs)}
    <p class="note">税金の扱いは一般的な内容です。個別の判断は顧問税理士にご確認ください。</p>
    {{{{line_cta}}}}
  </div>
</main>
<script type="application/ld+json">{json.dumps(data, ensure_ascii=False)}</script>
"""
    (ROOT / "src/yougo.body.html").write_text(body, encoding="utf-8")
    print(n, "terms")


if __name__ == "__main__":
    main()
