"""
シュフロ 실사 사진 릴스 렌더러 (ProductBaton 무신사 편 = 티이유식 레이아웃을 베이스로)
- 위 ~55%: 실사 사진(Pexels 등) — 컷마다 펀치인 → 느린 줌, 아래로 어두운 그라데이션
- 가운데: 라벨 → 헤드라인 2줄([ ] = 노랑 키워드) → 노란 밑줄 / 번호 카드 단계 공개
- 아래: 노래방식 자막(회색→흰색)
- 고정: 출처(사진 오른쪽 아래), 브랜드(맨 아래)
- 소리: 나레이션 + 로파이 BGM(나레이션 중 덕킹, 들리게) + 휙/띵/쿵
사용: python make_photo.py episodes/ep07_es_rush.py /tmp/ep7
work 에 lines/NN.wav, photos/<pexels id>.jpg 필요
"""
import sys, os, subprocess, importlib.util, wave, re
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
# ---- 색 테마 (에피소드에서 THEME = "dark" | "navy" | "light" 로 고름, 기본 dark) ----
# WHITE = 본문 글자색(라이트 테마에선 진한 남색), YEL = 강조색
THEMES = {
    "dark":  dict(BG=(13, 13, 17), YEL=(255, 206, 64), WHITE=(255, 255, 255), GRAY=(138, 138, 148), DIM=(88, 88, 98),
                  OFF=(200, 200, 208), RULE=(48, 48, 56), UNLIT=(92, 92, 102), SRCC=(170, 170, 180), BRANDC=(120, 120, 130),
                  CARD=(28, 28, 36), BTNTXT=(13, 13, 17), GRADE=(1.0, 0.0, 1.0, 0.0), TOP=0.55),
    "navy":  dict(BG=(18, 32, 64), YEL=(255, 210, 80), WHITE=(255, 255, 255), GRAY=(160, 176, 205), DIM=(100, 118, 155),
                  OFF=(210, 220, 238), RULE=(48, 66, 104), UNLIT=(110, 128, 165), SRCC=(200, 210, 228), BRANDC=(150, 166, 198),
                  CARD=(30, 48, 88), BTNTXT=(18, 32, 64), GRADE=(1.08, 0.05, 1.15, 0.06), TOP=0.8),
    "light": dict(BG=(247, 245, 240), YEL=(255, 106, 61), WHITE=(24, 28, 40), GRAY=(110, 112, 122), DIM=(170, 170, 178),
                  OFF=(90, 92, 104), RULE=(222, 220, 214), UNLIT=(196, 196, 202), SRCC=(120, 120, 128), BRANDC=(140, 140, 150),
                  CARD=(255, 255, 255), BTNTXT=(255, 255, 255), GRADE=(1.1, 0.06, 1.15, 0.08), TOP=0.95),
    "yellow": dict(BG=(255, 214, 72), YEL=(28, 78, 216), WHITE=(22, 22, 30), GRAY=(96, 80, 30), DIM=(180, 150, 60),
                  OFF=(70, 60, 30), RULE=(236, 190, 50), UNLIT=(196, 160, 60), SRCC=(110, 90, 40), BRANDC=(120, 100, 40),
                  CARD=(255, 236, 160), BTNTXT=(255, 255, 255), GRADE=(1.08, 0.06, 1.15, 0.06), TOP=0.95),
    "sky":   dict(BG=(156, 214, 250), YEL=(236, 72, 40), WHITE=(14, 30, 64), GRAY=(50, 80, 120), DIM=(110, 150, 190),
                  OFF=(40, 60, 100), RULE=(130, 190, 236), UNLIT=(100, 150, 196), SRCC=(40, 70, 110), BRANDC=(60, 90, 130),
                  CARD=(214, 238, 254), BTNTXT=(255, 255, 255), GRADE=(1.08, 0.02, 1.12, 0.06), TOP=0.95),
    "green": dict(BG=(22, 96, 66), YEL=(255, 220, 80), WHITE=(255, 255, 255), GRAY=(170, 210, 190), DIM=(90, 140, 115),
                  OFF=(210, 235, 222), RULE=(50, 124, 92), UNLIT=(104, 156, 130), SRCC=(200, 228, 214), BRANDC=(150, 196, 172),
                  CARD=(34, 116, 82), BTNTXT=(22, 96, 66), GRADE=(1.08, 0.05, 1.12, 0.06), TOP=0.8),
    "white": dict(BG=(255, 255, 255), WHITE=(20, 22, 30), GRAY=(120, 122, 132), DIM=(190, 190, 196), OFF=(80, 82, 94), RULE=(232, 232, 236), UNLIT=(200, 200, 206), SRCC=(130, 130, 140), BRANDC=(150, 150, 160), CARD=(244, 245, 248), BTNTXT=(255, 255, 255), GRADE=(1.06, 0.04, 1.12, 0.06), TOP=1.0, YEL=(226, 44, 44), EMPH='color'),
    "white_marker": dict(BG=(255, 255, 255), WHITE=(20, 22, 30), GRAY=(120, 122, 132), DIM=(190, 190, 196), OFF=(80, 82, 94), RULE=(232, 232, 236), UNLIT=(200, 200, 206), SRCC=(130, 130, 140), BRANDC=(150, 150, 160), CARD=(244, 245, 248), BTNTXT=(255, 255, 255), GRADE=(1.06, 0.04, 1.12, 0.06), TOP=1.0, YEL=(20, 22, 30), MARK=(255, 222, 70), EMPH='marker'),
    "white_big": dict(BG=(255, 255, 255), WHITE=(20, 22, 30), GRAY=(120, 122, 132), DIM=(190, 190, 196), OFF=(80, 82, 94), RULE=(232, 232, 236), UNLIT=(200, 200, 206), SRCC=(130, 130, 140), BRANDC=(150, 150, 160), CARD=(244, 245, 248), BTNTXT=(255, 255, 255), GRADE=(1.06, 0.04, 1.12, 0.06), TOP=1.0, YEL=(28, 92, 232), EMPH='big'),
}
def apply_theme(name):
    global TOPSH
    globals().update(dict(EMPH="color", MARK=(255, 222, 70)))  # 강조 방식: color / marker(형광펜) / big(크게)
    globals().update(THEMES[name])
    TOPSH = np.clip(TOP + ys / 0.12 * (1 - TOP), 0, 1).astype(np.float32)
def grade(a):
    """사진 색감 보정: (밝기, 따뜻함, 채도, 섀도 리프트)"""
    br, warm, sat, lift = GRADE
    if (br, warm, sat, lift) == (1.0, 0.0, 1.0, 0.0): return a
    a = a / 255.0
    a = lift + (1 - lift) * a                     # 검은 부분을 살짝 들어 올려 답답함 제거
    a = a * br
    a = a * np.array([1 + warm, 1 + warm * 0.3, 1 - warm], np.float32)
    g = a.mean(axis=2, keepdims=True); a = g + (a - g) * sat
    return np.clip(a, 0, 1) * 255.0
BG = (13, 13, 17)
FB = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
FM = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
_fc = {}
def F(size, black=True):
    k = (size, black)
    if k not in _fc: _fc[k] = ImageFont.truetype(FB if black else FM, size, index=0)
    return _fc[k]

def load_ep(p):
    s = importlib.util.spec_from_file_location("ep", p); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m

def ease(x): x = min(1, max(0, x)); return 1 - (1 - x) ** 3
def back(x):
    x = min(1, max(0, x)); c = 1.7; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2

PH = 1150  # 사진 영역 높이
_ph = {}
def photo(work, pid):
    if pid not in _ph:
        im = Image.open(f"{work}/photos/{pid}.jpg").convert("RGB")
        s = max(W * 1.2 / im.width, PH * 1.2 / im.height)
        _ph[pid] = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
    return _ph[pid]

ys = np.linspace(0, 1, PH)[:, None, None]
FADE = np.clip(1 - np.clip((ys - 0.62) / 0.38, 0, 1) ** 1.4, 0, 1).astype(np.float32)
TOPSH = np.clip(0.55 + ys / 0.12 * 0.45, 0, 1).astype(np.float32)
apply_theme("dark")
def draw_photo(cv, work, pid, tl, style=0, dur=6.0):
    """움직임은 컷마다 바꿈(0 줌인 / 1 줌아웃 / 2 좌→우 / 3 우→좌). 펀치인 없음, 천천히."""
    big = photo(work, pid)
    p = min(1.0, max(0.0, tl / max(dur, 1.0)))
    p = p * p * (3 - 2 * p)
    z, dx = 1.0, 0.0
    if style % 4 == 0: z = 1.0 + 0.07 * p
    elif style % 4 == 1: z = 1.07 - 0.07 * p
    elif style % 4 == 2: z, dx = 1.06, -0.04 + 0.08 * p
    else: z, dx = 1.06, 0.04 - 0.08 * p
    f = min(big.width / (W * 1.2), big.height / (PH * 1.2))
    cw, ch = W * 1.2 / z * f, PH * 1.2 / z * f
    l = (big.width - cw) / 2 + dx * big.width; t = (big.height - ch) * 0.42
    l = min(max(0, l), big.width - cw); t = min(max(0, t), big.height - ch)
    crop = big.crop((int(l), int(t), int(l + cw), int(t + ch))).resize((W, PH), Image.BILINEAR)
    a = grade(np.asarray(crop, np.float32)) * FADE * TOPSH + np.array(BG, np.float32) * (1 - FADE)
    cv.paste(Image.fromarray(a.astype(np.uint8)), (0, 0))

def tw(f, s): return f.getlength(s)
def parse(s):  # "[kw]" 강조
    out = []
    for part in re.split(r"(\[[^\]]+\])", s):
        if part: out.append((part.strip("[]"), part.startswith("[")))
    return out

def headline(d, label, l1, l2, tl, slam=False):
    d.text((70, 1190), label, font=F(30, False), fill=GRAY, anchor="ls")
    kb = 1.2 if EMPH == "big" else 1.0
    for k, line in enumerate((l1, l2)):
        p = ease((tl - k * 0.08) / 0.3)
        if p <= 0: continue
        size = 92
        parts = parse(line)
        def width(sz): return sum(tw(F(int(sz * (kb if h else 1))), s) for s, h in parts)
        while width(size) > W - 140: size -= 4
        x = 70; y = 1298 + k * 118 + (1 - p) * 30
        for s, hl in parts:
            f = F(int(size * kb)) if hl else F(size)
            if hl and slam and k == 1:
                sc = back(tl / 0.35); f = F(max(10, int(size * kb * (0.6 + 0.4 * sc))))
            if hl and EMPH == "marker":
                mw = tw(f, s) * ease((tl - 0.15 - k * 0.08) / 0.35)
                if mw > 1: d.rectangle((x - 6, y - size * 0.42, x - 6 + mw + 12, y + 10), fill=MARK)
                d.text((x, y), s, font=f, fill=WHITE, anchor="ls")
            else:
                d.text((x, y), s, font=f, fill=YEL if hl else WHITE, anchor="ls")
            x += tw(f, s)
    if EMPH != "marker":
        uw = 90 * ease((tl - 0.2) / 0.3)
        if uw > 1: d.rectangle((70, 1460, 70 + uw, 1466), fill=YEL)

def cards(d, items, active, tl):
    y0 = 1080
    for i, (num, title, sub) in enumerate(items):
        y = y0 + i * 122
        on = i == active; done = i < active
        d.text((70, y + 52), num, font=F(30, False), fill=YEL if on else DIM, anchor="ls")
        if i > active:
            d.text((140, y + 56), "・ ・ ・", font=F(44), fill=DIM, anchor="ls")
        else:
            p = ease(tl / 0.3) if on else 1
            d.text((140 + (1 - p) * 40, y + 58), title, font=F(54 if on else 46), fill=YEL if on else OFF, anchor="ls")
            d.text((W - 70, y + 50), sub, font=F(28, False), fill=YEL if on else GRAY, anchor="rs")
        d.line((70, y + 92, W - 70, y + 92), fill=RULE, width=2)

def wrap(text, n=14):
    out, cur = [], ""
    for i, ch in enumerate(text):
        cur += ch; nxt = text[i + 1] if i + 1 < len(text) else ""
        if (len(cur) >= n and ch in "、。，！？ 」" or len(cur) >= n + 3) and nxt not in "、。！？」）ー":
            out.append(cur); cur = ""
    if cur:
        if out and len(cur) <= 2: out[-1] += cur
        else: out.append(cur)
    return out

def karaoke(d, text, prog):
    f = F(54); lines = wrap(text); lit = int(len(text) * prog + 0.5); k = 0
    y0 = 1610 - (len(lines) - 1) * 40
    for li, line in enumerate(lines):
        x = (W - tw(f, line)) / 2; y = y0 + li * 80
        for ch in line:
            d.text((x, y), ch, font=f, fill=WHITE if k < lit else UNLIT, anchor="lm"); x += tw(f, ch); k += 1

def fixed(d, source, brand):
    d.text((W - 40, PH - 22), source, font=F(22, False), fill=SRCC, anchor="rs")
    d.text((W // 2, 1860), brand, font=F(30, False), fill=BRANDC, anchor="mm")

END = ("28卒の", "今週やること", "毎週まとめてます")
def end_card(d, tl):
    p = ease(tl / 0.4); a, b, c = END
    d.text((W // 2, 640 + (1 - p) * 40), a, font=F(70, False), fill=GRAY, anchor="mm")
    d.text((W // 2, 780 + (1 - p) * 40), b, font=F(120), fill=YEL, anchor="mm")
    d.text((W // 2, 930), c, font=F(64), fill=WHITE, anchor="mm")
    if tl > 0.6:
        d.rounded_rectangle((250, 1110, W - 250, 1230), 60, fill=YEL)
        d.text((W // 2, 1170), "フォローする", font=F(56), fill=BTNTXT, anchor="mm")
    d.text((W // 2, 1330), "@shufuro_acos", font=F(42, False), fill=GRAY, anchor="mm")

def summary_table(d, rows, title, note, tl):
    if EMPH == "marker": d.rectangle((W // 2 - tw(F(64), title) / 2 - 8, 304, W // 2 + tw(F(64), title) / 2 + 8, 336), fill=MARK)
    d.text((W // 2, 300), title, font=F(64), fill=YEL, anchor="mm")
    d.text((W // 2, 380), "スクショ推奨", font=F(34, False), fill=GRAY, anchor="mm")
    y0 = 460
    for i, r in enumerate(rows):
        p = ease((tl - i * 0.15) / 0.35)
        if p <= 0: continue
        y = y0 + i * 300 + (1 - p) * 30
        d.rounded_rectangle((60, y, W - 60, y + 270), 28, fill=CARD)
        d.text((100, y + 40), r[0], font=F(30, False), fill=YEL, anchor="ls")
        d.text((100, y + 110), r[1], font=F(60), fill=WHITE, anchor="ls")
        for k, (lab, val) in enumerate(r[2]):
            x = 100 + k * 300
            d.text((x, y + 175), lab, font=F(26, False), fill=GRAY, anchor="ls")
            if k == 0 and EMPH == "marker":
                d.rectangle((x - 4, y + 205, x + tw(F(50), val) + 4, y + 242), fill=MARK)
            d.text((x, y + 235), val, font=F(50), fill=(WHITE if EMPH == "marker" else YEL) if k == 0 else WHITE, anchor="ls")
    d.text((W // 2, 1420), note, font=F(26, False), fill=GRAY, anchor="mm")

def wav(p):
    with wave.open(p) as w: return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768

# ---------- 소리 ----------
def tone(f, dur, SR, decay=6.0, vol=0.2):
    t = np.arange(int(dur * SR)) / SR; y = np.sin(2 * np.pi * f * t) * np.exp(-t * decay)
    a = int(0.004 * SR); y[:a] *= np.linspace(0, 1, a); return (y * vol).astype(np.float32)

def sfx(kind, SR):
    rng = np.random.default_rng(3)
    if kind == "whoosh":
        n = int(0.32 * SR); x = rng.standard_normal(n)
        x = np.convolve(x, np.ones(18) / 18, "same") * np.sin(np.linspace(0, np.pi, n)) ** 2
        return (x * 0.5).astype(np.float32)
    if kind == "ding": return tone(1568, 0.5, SR, 7, 0.16) + tone(2349, 0.5, SR, 9, 0.08)
    if kind == "impact":
        t = np.arange(int(0.45 * SR)) / SR
        y = np.sin(2 * np.pi * (90 - 50 * t) * t) * np.exp(-t * 9) * 0.6
        y[:int(0.02 * SR)] += rng.standard_normal(int(0.02 * SR)) * 0.15
        return y.astype(np.float32)
    if kind == "pop": return tone(880, 0.12, SR, 30, 0.18) + tone(1320, 0.12, SR, 30, 0.1)
    return np.zeros(1, np.float32)

def lofi(n, SR, bpm=88):
    """로파이 비트: 킥·스네어·하이햇·부드러운 코드·베이스 (자체 합성, 저작권 없음)"""
    beat = 60 / bpm; y = np.zeros(n, np.float32); rng = np.random.default_rng(5)
    chords = [(261.6, 329.6, 392.0, 493.9), (220.0, 261.6, 329.6, 392.0), (174.6, 220.0, 261.6, 329.6), (196.0, 246.9, 293.7, 349.2)]
    bass = [65.4, 55.0, 43.7, 49.0]
    def add(sig, at):
        o = int(at * SR)
        if o >= n: return
        e = min(n, o + len(sig)); y[o:e] += sig[:e - o]
    bars = int(n / SR / (beat * 4)) + 1
    for b in range(bars):
        t0 = b * beat * 4; c = chords[b % 4]
        tt = np.arange(int(beat * 4 * SR)) / SR
        pad = sum(np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(4 * np.pi * f * tt) for f in c) / 4
        pad *= (1 - np.exp(-tt * 8)) * np.exp(-tt * 0.35) * 0.16
        add(pad.astype(np.float32), t0)
        for k in range(4):  # 베이스·킥·스네어
            bt = t0 + k * beat
            if k in (0, 2):
                tk = np.arange(int(0.3 * SR)) / SR
                add((np.sin(2 * np.pi * (110 * np.exp(-tk * 18) + 45) * tk) * np.exp(-tk * 9) * 0.55).astype(np.float32), bt)
                tb = np.arange(int(beat * 1.8 * SR)) / SR
                add((np.sin(2 * np.pi * bass[b % 4] * tb) * np.exp(-tb * 1.5) * 0.35).astype(np.float32), bt)
            else:
                ns = int(0.18 * SR); s = rng.standard_normal(ns) * np.exp(-np.arange(ns) / SR * 22) * 0.22
                add(np.convolve(s, [0.5, 0.5], "same").astype(np.float32), bt)
            for h in (0, 0.5):  # 하이햇
                nh = int(0.05 * SR); hh = np.diff(rng.standard_normal(nh + 1)) * np.exp(-np.arange(nh) / SR * 70) * (0.07 if h else 0.1)
                add(hh.astype(np.float32), bt + h * beat + (0.02 if h else 0))
    return y / max(1e-6, np.abs(y).max()) * 0.9

# ---------- 메인 ----------
def main(ep_path, work):
    ep = load_ep(ep_path)
    global END
    END = getattr(ep, "END", END)
    apply_theme(getattr(ep, "THEME", "dark"))
    os.makedirs(f"{work}/fast", exist_ok=True)
    tl = []; t = 0.15
    for L in ep.LINES:
        src, dst = f"{work}/lines/{L['id']}.wav", f"{work}/fast/{L['id']}.wav"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-af",
                        f"asetrate=24000*{ep.PITCH},aresample=24000,atempo={ep.SPEED / ep.PITCH:.4f},"
                        "silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
                        "loudnorm=I=-14:TP=-1.5:LRA=7", "-ar", "44100", "-ac", "1", dst], check=True)
        a = wav(dst); d = len(a) / 44100
        tl.append(dict(L=L, st=t, du=d)); t += d + ep.GAP
    total = t + getattr(ep, 'TAIL', 1.4)
    # 자막 조각 타이밍(글자 수 비례)
    for e in tl:
        caps = e["L"]["caps"] or [""]; w = [max(1, len(c)) for c in caps]; cum = np.cumsum([0] + w) / sum(w)
        e["cap_t"] = [e["st"] + e["du"] * c for c in cum[:-1]]
    nfr = int(total * FPS)
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p", f"{work}/video.mp4"], stdin=subprocess.PIPE)
    for fi in range(nfr):
        tt = fi / FPS
        cur = tl[0]
        for e in tl:
            if tt >= e["st"] - 0.05: cur = e
        L = cur["L"]; lt = tt - cur["st"]
        cv = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(cv)
        bj = 0
        if L.get("beats"):
            bj = max([i for i, c0 in enumerate(cur["cap_t"]) if tt >= c0 - 0.05] or [0])
            B = L["beats"][min(bj, len(L["beats"]) - 1)]
            blt = tt - cur["cap_t"][bj]
        if L["img"] == "END" or tt > tl[-1]["st"] + tl[-1]["du"] + 0.3:
            end_card(d, tt - (tl[-1]["st"] + tl[-1]["du"] + 0.3) if L["img"] != "END" else lt)
        elif L["img"] == "TABLE":
            summary_table(d, ep.TABLE, ep.TABLE_TITLE, ep.TABLE_NOTE, lt)
        elif L.get("beats"):
            draw_photo(cv, work, ep.PHOTOS[B["img"]], blt, bj, 3.0); d = ImageDraw.Draw(cv)
            headline(d, B["label"], *B["head"], blt)
            fixed(d, ep.SOURCE, ep.BRAND)
        else:
            # 같은 사진이 이어지면 줌 이어감, 카드 묶음은 묶음 시작 기준
            draw_photo(cv, work, ep.PHOTOS[L["img"]], lt, tl.index(cur), cur["du"] + ep.GAP); d = ImageDraw.Draw(cv)
            if "cards" in L:
                cards(d, ep.CARDS, L["cards"] - 1, lt)
            elif "head" in L:
                headline(d, L["label"], *L["head"], lt, slam=bool(L.get("slam")))
            fixed(d, ep.SOURCE, ep.BRAND)
        # 자막
        caps = L["caps"] if tt <= tl[-1]["st"] + tl[-1]["du"] + 0.3 else []
        if caps:
            j = max([i for i, c0 in enumerate(cur["cap_t"]) if tt >= c0 - 0.05] or [0])
            nxt = cur["cap_t"][j + 1] if j + 1 < len(caps) else cur["st"] + cur["du"]
            prog = (tt - cur["cap_t"][j]) / max(0.2, nxt - cur["cap_t"][j])
            karaoke(d, caps[j], min(1, max(0, prog)))
        ff.stdin.write(cv.tobytes())
    ff.stdin.close(); ff.wait()
    # 소리
    SR = 44100; n = int(total * SR) + SR
    vo = np.zeros(n, np.float32); fx = np.zeros(n, np.float32)
    def put(buf, sig, at):
        o = max(0, int(at * SR)); e = min(n, o + len(sig)); buf[o:e] += sig[:e - o]
    for k, e in enumerate(tl):
        put(vo, wav(f"{work}/fast/{e['L']['id']}.wav"), e["st"])
        if k > 0 and e["L"].get("sec"): put(fx, sfx("whoosh", SR) * 0.5, e["st"] - 0.14)
        if "ding" in e["L"]: put(fx, sfx("ding", SR), e["st"] + 0.05)
        if e["L"].get("slam"): put(fx, sfx("impact", SR), e["cap_t"][list(e["L"]["slam"])[0]])
        if "cards" in e["L"]: put(fx, sfx("pop", SR), e["st"])
        for c0 in e["cap_t"][1:] if e["L"].get("beats") else []: put(fx, sfx("whoosh", SR) * 0.6, c0 - 0.1)
        if e["L"]["img"] == "TABLE": put(fx, sfx("ding", SR), e["st"] + 0.1)
    env = np.convolve((np.abs(vo) > 0.02).astype(np.float32), np.ones(int(0.25 * SR)) / int(0.25 * SR), "same")
    duck = 1 - 0.55 * np.clip(env * 3, 0, 1)
    bg = lofi(n, SR) * 0.30 * duck
    fade = np.ones(n, np.float32); fl = int(1.2 * SR); fade[-fl:] = np.linspace(1, 0, fl)
    mix = (vo * 1.0 + fx * 0.8 + bg) * fade
    mix = np.clip(mix / max(1.0, np.abs(mix).max() / 0.95), -1, 1)
    with wave.open(f"{work}/audio.wav", "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype(np.int16).tobytes())
    out = f"{work}/{ep.OUT}.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{work}/video.mp4", "-i", f"{work}/audio.wav", "-c:v", "copy",
                    "-af", "loudnorm=I=-14:TP=-1.0:LRA=9", "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-shortest", out], check=True)
    print("OUT", out, round(total, 1), "s")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
