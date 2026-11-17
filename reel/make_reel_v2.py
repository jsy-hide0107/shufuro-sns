"""슈프로 Reel v2: 国が認めた穴場ホワイト企業（ユースエール）— 일본 취활 계정풍 하이텐션 편집
- 상단 고정 타이틀 바, 굵은 외곽선 텔롭, 노랑/빨강 강조, 집중선, 팝인 애니메이션
- 자체 합성 BGM + 효과음(저작권 문제 없음)
- 마지막에 기업 비교표(스크린샷용)
데이터 출처: 東京労働局 ユースエール認定企業 PRシート（2026年10月時点 掲載分）
"""
import os, math, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
RED = (230, 30, 45)
YEL = (255, 222, 0)
BLUE = (61, 90, 254)
NAVY = (18, 22, 60)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
FB = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
FONT_CACHE = {}

def F(size):
    if size not in FONT_CACHE:
        FONT_CACHE[size] = ImageFont.truetype(FB, size, index=0)
    return FONT_CACHE[size]

# 데이터 (PRシート 기재값)
COMPANIES = [  # 有給が多い順
    ("苫東石油備蓄", "国家石油備蓄基地の運営（JERAグループ）", 18.7, 2.3),
    ("サイバーディフェンス研究所", "情報セキュリティ診断・教育", 16.6, 12.9),
    ("アバールデータ", "半導体装置向け電子機器（東証スタンダード）", 14.6, 9.3),
    ("FFRIセキュリティ", "サイバーセキュリティ研究・開発", 13.1, 16.3),
    ("Nature Architects", "メタマテリアル×設計のディープテック", 11.8, 16.2),
]

# ---------- 그리기 유틸 ----------
def outlined(d, xy, text, size, fill, stroke=BLACK, sw=None, anchor="mm"):
    sw = sw if sw is not None else max(4, size // 9)
    d.text(xy, text, font=F(size), fill=fill, stroke_width=sw, stroke_fill=stroke, anchor=anchor)

def fit_size(d, text, size, maxw):
    while d.textlength(text, font=F(size)) > maxw and size > 18:
        size -= 4
    return size

def pop(t, start, dur=0.18):
    """0→1.15→1 오버슈트 스케일"""
    x = (t - start) / dur
    if x <= 0: return 0.0
    if x >= 1.6: return 1.0
    if x < 1: return 1.15 * (1 - (1 - x) ** 3)
    return 1.15 - 0.15 * (x - 1) / 0.6

def background(t, mode):
    img = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(img)
    if mode == "burst":  # 집중선
        cx, cy = W / 2, H / 2 + 40
        rot = t * 0.6
        for i in range(48):
            a0 = rot + i * 2 * math.pi / 48
            a1 = a0 + 0.045
            r = 2000
            col = (36, 44, 110) if i % 2 else (24, 30, 80)
            d.polygon([(cx, cy), (cx + r * math.cos(a0), cy + r * math.sin(a0)), (cx + r * math.cos(a1), cy + r * math.sin(a1))], fill=col)
    else:  # 사선 스트라이프 스크롤
        off = int(t * 120) % 120
        for x in range(-H, W + H, 120):
            d.polygon([(x + off, 0), (x + off + 50, 0), (x + off + 50 - H, H), (x + off - H, H)], fill=(26, 32, 84))
    return img

def top_bar(d):
    d.rectangle((0, 230, W, 420), fill=RED)
    d.rectangle((0, 420, W, 432), fill=YEL)
    outlined(d, (W / 2, 290), "国が認めた", 64, WHITE, sw=6)
    outlined(d, (W / 2, 368), "穴場ホワイト企業", 84, YEL, sw=8)

def footer(d, y=None):
    y = y or H - 430
    outlined(d, (W / 2, y), "出典：東京労働局 ユースエール認定企業PRシート", 30, WHITE, sw=3)
    outlined(d, (W / 2, y + 50), "@shufuro_acos", 40, YEL, sw=4)

def paste_scaled(base, layer, s):
    if s <= 0.05: return
    if abs(s - 1) > 0.01:
        lw, lh = int(W * s), int(H * s)
        layer = layer.resize((lw, lh), Image.BILINEAR)
        base.paste(layer, ((W - lw) // 2, (H - lh) // 2), layer)
    else:
        base.paste(layer, (0, 0), layer)

def layer():
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    return L, ImageDraw.Draw(L)

# ---------- 장면 ----------
# 타임라인(초)
T_HOOK, T_WHAT, T_RANK, T_TABLE, T_END = 0.0, 2.8, 6.0, 18.5, 25.0
RANK_DUR = (T_TABLE - T_RANK) / 5
SFX_EVENTS = []  # (time, kind)

def scene_hook(t):
    img = background(t, "burst"); d = ImageDraw.Draw(img); top_bar(d)
    L, ld = layer()
    s1 = pop(t, 0.05)
    outlined(ld, (W / 2, 720), "残業 月2.3時間", 112, YEL, sw=12)
    paste_scaled(img, L, s1)
    L, ld = layer()
    outlined(ld, (W / 2, 900), "有給 18.7日", 132, WHITE, sw=12)
    paste_scaled(img, L, pop(t, 0.7))
    L, ld = layer()
    outlined(ld, (W / 2, 1110), "の会社、知ってる？", 92, RED, stroke=WHITE, sw=10)
    paste_scaled(img, L, pop(t, 1.4))
    footer(ImageDraw.Draw(img))
    return img

def scene_what(t):
    img = background(t, "stripe"); d = ImageDraw.Draw(img); top_bar(d)
    L, ld = layer()
    outlined(ld, (W / 2, 640), "その正体は…", 76, WHITE, sw=8)
    paste_scaled(img, L, pop(t, T_WHAT))
    L, ld = layer()
    ld.rounded_rectangle((90, 720, W - 90, 880), 30, fill=YEL, outline=BLACK, width=8)
    ld.text((W / 2, 800), "ユースエール認定企業", font=F(92), fill=RED, anchor="mm", stroke_width=4, stroke_fill=WHITE)
    paste_scaled(img, L, pop(t, T_WHAT + 0.5))
    chips = [("有給 10日以上", 1.1), ("残業 20h以下", 1.5), ("新卒離職率 20%以下", 1.9)]
    for i, (txt, dt) in enumerate(chips):
        L, ld = layer()
        y = 980 + i * 120
        ld.rounded_rectangle((170, y - 50, W - 170, y + 50), 50, fill=WHITE, outline=BLACK, width=6)
        ld.text((W / 2, y), "✓ " + txt, font=F(60), fill=NAVY, anchor="mm")
        paste_scaled(img, L, pop(t, T_WHAT + dt))
    L, ld = layer()
    outlined(ld, (W / 2, 1370), "厚労省のお墨付き", 64, YEL, sw=7)
    paste_scaled(img, L, pop(t, T_WHAT + 2.4))
    footer(ImageDraw.Draw(img))
    return img

def scene_rank(t):
    k = min(4, int((t - T_RANK) / RANK_DUR))
    st = T_RANK + k * RANK_DUR
    idx = 4 - k  # 5위부터 1위로
    name, biz, leave, ot = COMPANIES[idx]
    rank = idx + 1
    img = background(t, "burst" if rank == 1 else "stripe"); d = ImageDraw.Draw(img); top_bar(d)
    outlined(d, (W / 2, 490), "東京から5社・有給が多い順", 44, WHITE, sw=5)
    L, ld = layer()
    badge_col = YEL if rank == 1 else WHITE
    ld.ellipse((W / 2 - 120, 560, W / 2 + 120, 800), fill=RED, outline=badge_col, width=10)
    ld.text((W / 2, 660), f"{rank}", font=F(150), fill=badge_col, anchor="mm", stroke_width=6, stroke_fill=BLACK)
    ld.text((W / 2, 760), "位", font=F(44), fill=WHITE, anchor="mm")
    paste_scaled(img, L, pop(t, st))
    L, ld = layer()
    size = fit_size(ld, name, 96, W - 120)
    outlined(ld, (W / 2, 900), name, size, WHITE, sw=10)
    bsize = fit_size(ld, biz, 44, W - 140)
    outlined(ld, (W / 2, 990), biz, bsize, YEL, sw=5)
    paste_scaled(img, L, pop(t, st + 0.25))
    L, ld = layer()
    for j, (lab, val, col) in enumerate([("有給", f"{leave}日", YEL), ("残業/月", f"{ot}h", WHITE)]):
        cx = W / 2 + (-230 if j == 0 else 230)
        ld.rounded_rectangle((cx - 210, 1080, cx + 210, 1330), 28, fill=(0, 0, 0, 170), outline=col, width=6)
        ld.text((cx, 1135), lab, font=F(48), fill=WHITE, anchor="mm")
        outlined(ld, (cx, 1245), val, 104, col, sw=8)
    paste_scaled(img, L, pop(t, st + 0.55))
    footer(ImageDraw.Draw(img))
    return img, (st, rank)

def scene_table(t):
    img = background(t, "stripe"); d = ImageDraw.Draw(img); top_bar(d)
    L, ld = layer()
    x0, x1 = 50, W - 50
    y = 480
    ld.rounded_rectangle((x0, y, x1, y + 950), 24, fill=WHITE, outline=BLACK, width=8)
    ld.rectangle((x0 + 8, y + 8, x1 - 8, y + 100), fill=NAVY)
    ld.text((x0 + 90, y + 54), "順", font=F(40), fill=YEL, anchor="mm")
    ld.text((x0 + 340, y + 54), "企業名", font=F(40), fill=YEL, anchor="mm")
    ld.text((x0 + 700, y + 54), "有給", font=F(40), fill=YEL, anchor="mm")
    ld.text((x0 + 870, y + 54), "残業/月", font=F(40), fill=YEL, anchor="mm")
    for i, (name, biz, leave, ot) in enumerate(COMPANIES):
        ry = y + 110 + i * 166
        if i % 2 == 0:
            ld.rectangle((x0 + 8, ry, x1 - 8, ry + 160), fill=(240, 243, 255))
        ld.text((x0 + 90, ry + 80), f"{i+1}", font=F(64), fill=RED, anchor="mm")
        ns = fit_size(ld, name, 44, 440)
        ld.text((x0 + 340, ry + 58), name, font=F(ns), fill=NAVY, anchor="mm")
        bs = fit_size(ld, biz, 26, 450)
        ld.text((x0 + 340, ry + 115), biz, font=F(bs), fill=(90, 96, 120), anchor="mm")
        ld.text((x0 + 700, ry + 80), f"{leave}日", font=F(48), fill=RED, anchor="mm")
        ld.text((x0 + 870, ry + 80), f"{ot}h", font=F(48), fill=NAVY, anchor="mm")
    paste_scaled(img, L, pop(t, T_TABLE, 0.22))
    L, ld = layer()
    outlined(ld, (W / 2, 1490), "保存して企業研究に使って！", 64, YEL, sw=8)
    paste_scaled(img, L, pop(t, T_TABLE + 1.0))
    footer(ImageDraw.Draw(img), y=1580)
    return img

def render(t):
    if t < T_WHAT: return scene_hook(t)
    if t < T_RANK: return scene_what(t)
    if t < T_TABLE: return scene_rank(t)[0]
    return scene_table(t)

# ---------- 효과음 이벤트 ----------
SFX_EVENTS += [(0.05, "pop"), (0.7, "pop"), (1.4, "hit")]
SFX_EVENTS += [(T_WHAT, "whoosh"), (T_WHAT + 0.5, "hit")] + [(T_WHAT + x, "pop") for x in (1.1, 1.5, 1.9)] + [(T_WHAT + 2.4, "chime")]
for k in range(5):
    st = T_RANK + k * RANK_DUR
    SFX_EVENTS += [(st, "whoosh"), (st + 0.02, "hit" if k < 4 else "fanfare"), (st + 0.55, "pop")]
SFX_EVENTS += [(T_TABLE, "whoosh"), (T_TABLE + 0.05, "fanfare"), (T_TABLE + 1.0, "chime")]

# ---------- 오디오 합성 ----------
SR = 44100

def env(n, a=0.005, r=0.1):
    t = np.arange(n) / SR
    e = np.minimum(1, t / a) * np.exp(-t / r)
    return e

def tone(freq, dur, kind="sq", vol=0.2, r=0.15):
    n = int(dur * SR); t = np.arange(n) / SR
    if kind == "sq": w = np.sign(np.sin(2 * np.pi * freq * t)) * 0.6
    elif kind == "tri": w = 2 / np.pi * np.arcsin(np.sin(2 * np.pi * freq * t))
    else: w = np.sin(2 * np.pi * freq * t)
    return w * env(n, r=r) * vol

def sfx(kind):
    if kind == "pop":
        n = int(0.12 * SR); t = np.arange(n) / SR
        f = 900 * np.exp(-t * 18) + 300
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, r=0.04) * 0.5
    if kind == "hit":
        n = int(0.35 * SR); t = np.arange(n) / SR
        kick = np.sin(2 * np.pi * np.cumsum(160 * np.exp(-t * 20) + 50) / SR) * env(n, r=0.12)
        noise = np.random.RandomState(1).randn(n) * env(n, r=0.05) * 0.3
        return (kick + noise) * 0.6
    if kind == "whoosh":
        n = int(0.3 * SR); t = np.arange(n) / SR
        noise = np.random.RandomState(2).randn(n)
        k = np.ones(40) / 40
        noise = np.convolve(noise, k, mode="same")
        shape = np.sin(np.pi * t / t[-1]) ** 2
        return noise * shape * 0.5
    if kind == "chime":
        return sum(tone(f, 0.6, "sin", 0.18, r=0.25) for f in (1318.5, 1975.5))
    if kind == "fanfare":
        out = np.zeros(int(0.7 * SR))
        for i, f in enumerate((523.25, 659.25, 783.99, 1046.5)):
            s = tone(f, 0.5, "sq", 0.12, r=0.2)
            o = int(i * 0.07 * SR)
            out[o:o + len(s)] += s[: len(out) - o]
        return out
    return np.zeros(1)

def bgm(total):
    n = int(total * SR); out = np.zeros(n)
    bpm = 150; beat = 60 / bpm
    prog = [(261.63, 329.63, 392.0), (220.0, 261.63, 329.63), (174.61, 220.0, 261.63), (196.0, 246.94, 293.66)]
    bass = [130.81, 110.0, 87.31, 98.0]
    nb = int(total / beat) + 1
    for b in range(nb):
        t0 = b * beat; o = int(t0 * SR)
        bar = (b // 4) % 4
        chord = prog[bar]
        parts = []
        # 킥(정박) + 하이햇(반박)
        parts.append((o, sfx("hit") * 0.35))
        hh = np.random.RandomState(b).randn(int(0.04 * SR)) * env(int(0.04 * SR), r=0.01) * 0.08
        parts.append((o + int(beat / 2 * SR), hh))
        parts.append((o, tone(bass[bar], beat * 0.9, "tri", 0.22, r=0.3)))
        # 아르페지오
        for i in range(2):
            f = chord[(b * 2 + i) % 3] * 2
            parts.append((o + int(i * beat / 2 * SR), tone(f, beat / 2, "sq", 0.05, r=0.08)))
        for off, s in parts:
            if off >= n: continue
            e = min(n, off + len(s)); out[off:e] += s[: e - off]
    return out * 0.55

def build_audio(total, path):
    mix = bgm(total)
    for tt, kind in SFX_EVENTS:
        s = sfx(kind); o = int(tt * SR); e = min(len(mix), o + len(s))
        if o < len(mix): mix[o:e] += s[: e - o]
    fade = int(0.6 * SR); mix[-fade:] *= np.linspace(1, 0, fade)
    mix = mix / max(1e-6, np.max(np.abs(mix))) * 0.9
    pcm = (mix * 32767).astype(np.int16)
    with wave.open(path, "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())

if __name__ == "__main__":
    os.makedirs("frames2", exist_ok=True)
    for f in os.listdir("frames2"): os.remove(os.path.join("frames2", f))
    n = int(T_END * FPS)
    for i in range(n):
        render(i / FPS).save(f"frames2/f{i:04d}.png")
    render(1.9).save("cover_v2.png")
    build_audio(T_END, "audio_v2.wav")
    subprocess.run(["ffmpeg", "-y", "-framerate", str(FPS), "-i", "frames2/f%04d.png", "-i", "audio_v2.wav",
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", "reel_youthyell_v2.mp4"],
                   check=True, capture_output=True)
    print("done", n)
