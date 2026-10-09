"""コラムの30秒ショート動画（縦1080×1920）を作り、コラムに埋め込む。

使い方:
  python3 scripts/gen_short.py video-src/<日付>-<slug>.json [--voice self|female|none] [--rec 録音ファイル]

  --voice self   : 代表本人の声。--rec に「3行を3秒ずつあけて読んだ録音」を渡す。
                   最後の2場面（代表紹介・予約）は video-src/voice/fixed_*.wav を使い回す。
  --voice female : 女性の合成音声（Open JTalk + HTS Voice "Mei"、CC BY 3.0 のため最後の画面に表記）。
  --voice none   : 音なし。

台本（JSON）の形:
  {"slug": "shacho-nenkin-mikomi", "date": "2026-10-09",
   "title": "30秒でわかる：…", "description": "…",
   "scenes": [  # 3つ。type は hook / stat / list
     {"type": "hook", "tag": "社長へ質問", "html": "ねんきん定期便、<br><em>開けて</em><br>いますか？", "say": "読み上げ文（ひらがな可）"},
     {"type": "stat", "head": "年金だけだと<br>毎月", "num": 42434, "prefix": "−", "unit": "円の赤字", "src": "出典", "say": "…"},
     {"type": "list", "head": "社長には<br><em>埋める手段</em>が多い", "items": [["役員退職金", "会社から受け取る"]], "say": "…"}
   ]}
必要なもの: open_jtalk（apt の open-jtalk, open-jtalk-mecab-naist-jdic）、pip の imageio-ffmpeg、Playwright（/opt/pw-browsers/chromium）。
"""
import argparse, array, html, json, os, pathlib, re, shutil, subprocess, sys, tempfile, wave

ROOT = pathlib.Path(__file__).resolve().parent.parent
VS = ROOT / "video-src"
SR = 48000
SITE = "https://rabbit03-03.github.io/fp-site/"
DIC = "/var/lib/mecab/dic/open-jtalk/naist-jdic"
PROFILE_SAY = {"self": None, "female": "独立系FP、いがらしだいすけがご相談をお受けします。じゅうにもんの無料診断で、あなたの備えをチェックできます。"}
CTA_SAY = "初回のオンライン相談は無料です。プロフィールのリンクから、ご予約ください。"


def ffmpeg():
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def read_wav(p):
    w = wave.open(str(p))
    x = array.array("h", w.readframes(w.getnframes()))
    if w.getnchannels() != 1 or w.getframerate() != SR:
        raise SystemExit(f"{p}: 48kHz モノラルにしてください")
    return x


def to_wav(src, dst):
    subprocess.run([ffmpeg(), "-loglevel", "error", "-y", "-i", str(src), "-ac", "1", "-ar", str(SR), str(dst)], check=True)


def tts(text, voice, dst):
    v = VS / "voice/mei_normal.htsvoice"
    raw = str(dst) + ".raw.wav"
    subprocess.run(["open_jtalk", "-x", DIC, "-m", str(v), "-r", "1.1", "-ow", raw], input=text.encode(), check=True)
    to_wav(raw, dst)
    os.remove(raw)


def split_recording(rec, n, tmp):
    """録音を n 行に分ける。行と行の間の長い無音（上位 n-1 個）で区切る。"""
    w = pathlib.Path(tmp) / "rec.wav"
    to_wav(rec, w)
    x = read_wav(w)
    win = int(0.05 * SR)
    loud = []
    for i in range(0, len(x), win):
        seg = x[i:i + win]
        loud.append(max(abs(v) for v in seg) > 900 if seg else False)
    # 音のある区間
    runs, start = [], None
    for i, l in enumerate(loud + [False]):
        if l and start is None: start = i
        if not l and start is not None:
            runs.append([start, i]); start = None
    runs = [r for r in runs if r[1] - r[0] >= 3]  # 0.15秒未満の雑音は捨てる
    if len(runs) < n:
        raise SystemExit(f"録音から {n} 行を見つけられませんでした（見つかった音の区間 {len(runs)}）")
    gaps = sorted(range(len(runs) - 1), key=lambda i: runs[i + 1][0] - runs[i][1], reverse=True)[:n - 1]
    cuts = sorted(gaps)
    lines, b = [], 0
    for c in cuts + [len(runs) - 1]:
        lines.append((runs[b][0], runs[c][1])); b = c + 1
    outs = []
    for k, (a, e) in enumerate(lines):
        p = pathlib.Path(tmp) / f"line{k}.wav"
        o = wave.open(str(p), "w"); o.setnchannels(1); o.setsampwidth(2); o.setframerate(SR)
        o.writeframes(x[max(0, a * win - int(0.1 * SR)):e * win + int(0.15 * SR)].tobytes()); o.close()
        outs.append(p)
    return outs


def dur(p):
    w = wave.open(str(p)); return w.getnframes() / w.getframerate()


def scene_html(i, sc):
    t = sc["type"]
    if t == "hook":
        return f'<div class="s" id="s{i}"><span class="tag">{sc.get("tag", "社長へ質問")}</span><h1>{sc["html"]}</h1></div>'
    if t == "stat":
        src = f'<div class="src">{sc["src"]}</div>' if sc.get("src") else ""
        return (f'<div class="s" id="s{i}"><h2>{sc["head"]}</h2><div class="big"><span class="pre">{sc.get("prefix", "")}</span>'
                f'<span class="num" data-n="{sc["num"]}">0</span></div><div class="unit">{sc["unit"]}</div>{src}</div>')
    if t == "list":
        lis = "".join(f'<li class="it">{a}<small>{b}</small></li>' for a, b in sc["items"])
        return f'<div class="s" id="s{i}"><h2>{sc["head"]}</h2><ul>{lis}</ul></div>'
    raise SystemExit(f"不明な場面: {t}")


CSS = """*{box-sizing:border-box;margin:0}
html,body{width:1080px;height:1920px;overflow:hidden;font-family:'Noto Sans JP',sans-serif;background:#0b2545;color:#fff}
.s{position:absolute;inset:0;padding:160px 90px;display:flex;flex-direction:column;justify-content:center;opacity:0}
.tag{display:inline-block;background:#f28c28;color:#fff;font-weight:900;font-size:44px;padding:10px 30px;border-radius:40px;align-self:flex-start;margin-bottom:50px}
h1{font-size:104px;font-weight:900;line-height:1.3}
h2{font-size:80px;font-weight:900;line-height:1.35;margin-bottom:60px}
em{font-style:normal;color:#ffc857}
.big{font-size:180px;font-weight:900;color:#ffc857;letter-spacing:-4px;line-height:1.1}
.unit{font-size:68px;font-weight:900}
.src{position:absolute;bottom:150px;left:90px;right:90px;font-size:32px;color:#b8c7dd;line-height:1.5}
ul{list-style:none;padding:0}
li{font-size:62px;font-weight:900;background:rgba(255,255,255,.1);border-left:14px solid #f28c28;padding:28px 40px;margin-bottom:32px;border-radius:12px;opacity:0}
li small{display:block;font-size:38px;font-weight:500;color:#cfe0f5;margin-top:6px}
.photo{width:640px;height:800px;object-fit:cover;border-radius:24px;border:8px solid #fff;margin-bottom:50px}
.btn{background:#f28c28;font-weight:900;text-align:center;border-radius:80px}
.name{text-align:center;font-size:44px;color:#e6edf5}
.prog{position:absolute;top:0;left:0;height:14px;background:#f28c28}
.logo{position:absolute;top:70px;left:90px;font-size:36px;font-weight:700;color:#b8c7dd}
.phone{width:480px;height:960px;border:18px solid #111;border-radius:70px;overflow:hidden;background:#fff;box-shadow:0 30px 80px rgba(0,0,0,.5)}
.phone img{width:100%;display:block}
.credit{position:absolute;bottom:60px;left:0;right:0;font-size:24px;color:#8fa3bf;text-align:center}"""

JS = """const ease=x=>1-Math.pow(1-Math.min(Math.max(x,0),1),3);
function render(t){
 document.getElementById('prog').style.width=(t/T*100)+'%';
 D.forEach(([a,b,st,d],i)=>{const el=document.getElementById('s'+(i+1));
  const fi=ease((t-a)/0.4), fo=i==D.length-1?1:1-ease((t-(b-0.3))/0.3);
  el.style.opacity=(t<a||t>b)?0:Math.min(fi,fo);
  el.style.transform=`translateY(${(1-fi)*60}px)`;
  el.querySelectorAll('.num').forEach(n=>{const k=ease((t-st-d*0.45)/1.8);n.textContent=Math.round(+n.dataset.n*k).toLocaleString();});
  const its=el.querySelectorAll('.it');its.forEach((li,j)=>{const at=st+d*(0.25+0.6*j/Math.max(its.length,1));const k=ease((t-at)/0.5);li.style.opacity=k;li.style.transform=`translateX(${(1-k)*-80}px)`;});
  const ph=el.querySelector('.photo');if(ph)ph.style.transform=`scale(${1+0.04*Math.min(Math.max((t-st)/8,0),1)})`;
  const pn=el.querySelector('.phone');if(pn){const q=ease((t-st-0.3)/0.6);pn.style.transform=`translateY(${(1-q)*200}px)`;pn.style.opacity=q;}
 });
}"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec"); ap.add_argument("--voice", default="self", choices=["self", "female", "none"]); ap.add_argument("--rec")
    a = ap.parse_args()
    spec = json.loads(pathlib.Path(a.spec).read_text())
    name = f'{spec["date"]}-{spec["slug"]}'
    sc = spec["scenes"]
    tmp = tempfile.mkdtemp()
    # 1. 声
    lines = []
    if a.voice == "self":
        if not a.rec: raise SystemExit("--voice self には --rec（録音ファイル）が必要です")
        lines = split_recording(a.rec, len(sc), tmp) + [VS / "voice/fixed_profile.wav", VS / "voice/fixed_cta.wav"]
    elif a.voice == "female":
        for k, s in enumerate(sc):
            p = pathlib.Path(tmp) / f"line{k}.wav"; tts(s["say"], a.voice, p); lines.append(p)
        for k, t in enumerate([PROFILE_SAY["female"], CTA_SAY]):
            p = pathlib.Path(tmp) / f"fix{k}.wav"; tts(t, a.voice, p); lines.append(p)
    ds = [dur(p) for p in lines] if lines else [3.0, 6.0, 6.0, 5.0, 5.0]
    # 2. 場面の時刻
    t, D = 0.35, []
    for k, d in enumerate(ds):
        D.append([0 if k == 0 else round(t - 0.4, 2), 0, round(t, 2), round(d, 2)])
        t += d + 0.55
    T = round(t + 0.8, 2)
    for k in range(len(D)):
        D[k][1] = round(D[k + 1][0], 2) if k + 1 < len(D) else T
    # 3. 音声をつなぐ
    narr = None
    if lines:
        buf = array.array("h", [0] * int(T * SR))
        for (s0, _, st, _), p in zip(D, lines):
            x = read_wav(p); o = int(st * SR)
            buf[o:o + len(x)] = x[:max(0, len(buf) - o)]
        raw = pathlib.Path(tmp) / "narr_raw.wav"
        o = wave.open(str(raw), "w"); o.setnchannels(1); o.setsampwidth(2); o.setframerate(SR); o.writeframes(buf.tobytes()); o.close()
        narr = pathlib.Path(tmp) / "narr.wav"
        af = "highpass=f=80,afftdn=nf=-30,loudnorm=I=-16:TP=-1.5" if a.voice == "self" else "loudnorm=I=-16:TP=-1.5"
        subprocess.run([ffmpeg(), "-loglevel", "error", "-y", "-i", str(raw), "-af", af, "-ar", str(SR), str(narr)], check=True)
    # 4. 画面
    n = len(sc)
    credit = '<div class="credit">音声合成：HTS Voice “Mei”（名古屋工業大学, CC BY 3.0）</div>' if a.voice == "female" else ""
    body = "".join(scene_html(i + 1, s) for i, s in enumerate(sc))
    body += (f'<div class="s" id="s{n+1}" style="align-items:center;text-align:center"><img class="photo" src="photo.jpg">'
             '<div style="font-size:72px;font-weight:900">五十嵐 大輔</div><div class="name" style="margin-top:14px">独立系FP（AFP）／株式会社DSK 代表</div>'
             '<h2 style="margin:50px 0 0;font-size:74px">あなたの備え、<em>12問</em>の<br>無料診断でチェック</h2></div>')
    body += (f'<div class="s" id="s{n+2}" style="align-items:center;text-align:center;padding-top:120px"><h2 style="margin-bottom:40px;font-size:70px">初回のオンライン相談は<br><em>無料</em>です</h2>'
             '<div class="phone"><img src="yoyaku.png"></div><div class="btn" style="margin-top:50px;font-size:56px;padding:30px 50px">ご予約は<br>プロフィールのリンクから</div>'
             f'{credit}</div>')
    page = (f'<!doctype html><html><head><meta charset="utf-8"><link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@500;700;900&display=block" rel="stylesheet">'
            f'<style>{CSS}</style></head><body><div class="prog" id="prog"></div><div class="logo">株式会社DSK｜社長のお金の話</div>{body}'
            f'<script>const D={json.dumps(D)};const T={T};{JS}</script></body></html>')
    shutil.copy(ROOT / "src/assets/img/daihyo.jpg", pathlib.Path(tmp) / "photo.jpg")
    shutil.copy(VS / "yoyaku.png", pathlib.Path(tmp) / "yoyaku.png")
    hp = pathlib.Path(tmp) / "v.html"; hp.write_text(page)
    silent = pathlib.Path(tmp) / "silent.mp4"
    env = dict(os.environ, FF=ffmpeg())
    env["NODE_PATH"] = subprocess.run(["npm", "root", "-g"], capture_output=True, text=True).stdout.strip()
    subprocess.run(["node", str(ROOT / "scripts/rec_video.js"), str(hp), str(silent), str(T)], check=True, env=env)
    out = ROOT / f"src/assets/dl/{name}.mp4"
    if narr:
        subprocess.run([ffmpeg(), "-loglevel", "error", "-y", "-i", str(silent), "-i", str(narr), "-c:v", "copy", "-c:a", "aac", "-b:a", "160k",
                        "-ar", str(SR), "-shortest", "-movflags", "+faststart", str(out)], check=True)
    else:
        shutil.copy(silent, out)
    poster = ROOT / f"src/assets/img/video/{name}.jpg"
    poster.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([ffmpeg(), "-loglevel", "error", "-y", "-ss", "2.5", "-i", str(out), "-frames:v", "1", "-vf", "scale=540:960", "-q:v", "4", str(poster)], check=True)
    # 5. コラムに埋め込む（既にあれば差し替え）
    col = ROOT / f'src/column/{spec["slug"]}.body.html'
    s = col.read_text()
    s = re.sub(r'\n    <figure class="short-video">.*?</script>\n\n?', "\n", s, flags=re.S)
    who = "代表 五十嵐の声でお話ししています" if a.voice == "self" else ("音声は合成音声です" if a.voice == "female" else "音なし")
    ld = {"@context": "https://schema.org", "@type": "VideoObject", "name": spec["title"], "description": spec["description"],
          "thumbnailUrl": f"{SITE}assets/img/video/{name}.jpg", "contentUrl": f"{SITE}assets/dl/{name}.mp4",
          "uploadDate": f'{spec["date"]}T09:00:00+09:00', "duration": f"PT{round(T)}S"}
    fig = ('\n    <figure class="short-video">\n'
           f'      <video controls playsinline preload="none" poster="{{{{root}}}}assets/img/video/{name}.jpg" src="{{{{root}}}}assets/dl/{name}.mp4"></video>\n'
           f'      <figcaption>{html.escape(spec["title"])}（{who}）</figcaption>\n    </figure>\n'
           f'    <script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>\n')
    m = re.search(r'<div class="callout">.*?</div>\n', s, flags=re.S)
    if not m: raise SystemExit("要点ボックスが見つかりません")
    s = s[:m.end()] + fig + s[m.end():].lstrip("\n").join(["\n", ""])
    col.write_text(s)
    print(f"OK {out.relative_to(ROOT)} {T}秒")
    shutil.rmtree(tmp)


if __name__ == "__main__":
    main()
