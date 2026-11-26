"""
3단 정보 레이아웃 렌더러 (1080x1920)
- 위 55%: 장면 이미지(아래로 검정 그라데이션, 천천히 줌)
- 가운데: 라벨 → 헤드라인 2줄(키워드 노랑) → 노란 밑줄 / 번호 카드 / 표(캡처용)
- 아래: 노래방식 자막(회색→흰색)
- 고정: 출처(왼쪽 위 작게), 로고(맨 아래 가운데)
사용: python make_info3.py episodes/ep05_ntt.py <work_dir>
work_dir 에 lines/NN.wav(나레이션), scenes/*.png 가 있어야 함
"""
import sys, os, math, subprocess, importlib.util, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
YEL = (255, 210, 60); WHITE = (255, 255, 255); GRAY = (120, 120, 128); DIM = (70, 70, 78)
FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
FONT_B = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
_fc = {}
def F(size, bold=False):
    k = (size, bold)
    if k not in _fc:
        _fc[k] = ImageFont.truetype(FONT_B if bold else FONT, size, index=0)
    return _fc[k]

def load_ep(path):
    spec = importlib.util.spec_from_file_location("ep", path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

_scene_cache = {}
def scene_img(work, name, h):
    k = (name, h)
    if k not in _scene_cache:
        im = Image.open(os.path.join(work, "scenes", name + ".png")).convert("RGB")
        r = W / im.width; im = im.resize((W, int(im.height * r)))
        if im.height < h:
            im = im.resize((int(W * h / im.height), h)); im = im.crop(((im.width - W) // 2, 0, (im.width - W) // 2 + W, h))
        else:
            im = im.crop((0, 0, W, h))
        _scene_cache[k] = im
    return _scene_cache[k]

THEMES = {"intro": ((30, 95, 205), (8, 30, 80)), "big": ((25, 105, 200), (8, 35, 85)),
          "sub": ((20, 140, 140), (6, 50, 56)), "region": ((215, 110, 35), (80, 35, 10)), "cta": ((60, 60, 90), (15, 15, 30))}
_bg = {}
def theme_bg(name):
    if name not in _bg:
        c1, c2 = THEMES.get(name, ((30, 30, 40), (0, 0, 0)))
        g = np.linspace(0, 1, H)[:, None]
        arr = (np.array(c1)[None, :] * (1 - g) + np.array(c2)[None, :] * g)
        _bg[name] = Image.fromarray(np.repeat(arr[:, None, :], W, axis=1).astype(np.uint8))
    return _bg[name]

def media(canvas, work, name, h, t_local):
    from PIL import ImageEnhance
    base = scene_img(work, name, h)
    base = ImageEnhance.Brightness(base).enhance(1.45)
    z = 1.0 + 0.04 * min(t_local / 6.0, 1.0)
    im = base.resize((int(W * z), int(h * z)))
    im = im.crop(((im.width - W) // 2, (im.height - h) // 2, (im.width - W) // 2 + W, (im.height - h) // 2 + h))
    fade = Image.new("L", (W, h), 255); d = ImageDraw.Draw(fade)
    fl = int(h * 0.45)
    for y in range(h - fl, h):
        d.line([(0, y), (W, y)], fill=int(255 * (1 - (y - (h - fl)) / fl) ** 1.6))
    canvas.paste(im, (0, 0), fade)

def tw(d, s, f):
    b = d.textbbox((0, 0), s, font=f); return b[2] - b[0]

def headline(d, y, label, l1, l2, kw, t_local):
    a = min(1, t_local / 0.25)
    d.text((W // 2, y), label, font=F(40, True), fill=tuple(int(c * a) for c in (220, 228, 245)), anchor="mm")
    y1 = y + 100
    for i, line in enumerate((l1, l2)):
        f = F(92)
        # 키워드는 노랑
        parts = [(line, WHITE)]
        if kw and kw in line:
            a_, b_ = line.split(kw, 1); parts = [(a_, WHITE), (kw, YEL), (b_, WHITE)]
        total = sum(tw(d, p, f) for p, _ in parts); x = (W - total) // 2
        for p, col in parts:
            d.text((x, y1 + i * 120), p, font=f, fill=col, anchor="lm"); x += tw(d, p, f)
    uw = int(520 * min(1, max(0, (t_local - 0.2) / 0.4)))
    d.rectangle([W // 2 - uw // 2, y1 + 205, W // 2 + uw // 2, y1 + 215], fill=YEL)

def cards(d, y, title, items, active):
    d.text((W // 2, y), title, font=F(40, True), fill=(220, 228, 245), anchor="mm")
    for i, it in enumerate(items):
        yy = y + 70 + i * 128; on = i == active; done = i < active
        box = [90, yy, W - 90, yy + 108]
        d.rounded_rectangle(box, radius=22, fill=(255, 241, 180) if on else (255, 255, 255, 40), outline=YEL if on else (200, 210, 230), width=4 if on else 2)
        d.text((150, yy + 54), f"{i+1:02d}", font=F(52), fill=(220, 140, 0) if (on or done) else (150, 158, 178), anchor="lm")
        d.text((260, yy + 54), it, font=F(48, True), fill=(30, 30, 40) if (on or done) else (110, 118, 140), anchor="lm")

LOGO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logos_ntt")
_lg = {}
def logo_for(name, maxw, maxh):
    k = (name, maxw, maxh)
    if k not in _lg:
        p = os.path.join(LOGO_DIR, name + ".png")
        if os.path.exists(p):
            im = Image.open(p).convert("RGBA"); im.thumbnail((maxw, maxh)); _lg[k] = im
        else:
            _lg[k] = None
    return _lg[k]

CANVAS = {}
def table(d, y, title, cols, rows, widths, hl_rows, hl_col, note):
    d.text((60, y), title, font=F(44), fill=YEL, anchor="lm")
    y += 55; rh = 118; x0 = 40
    xs = [x0]
    for w_ in widths: xs.append(xs[-1] + w_)
    d.rectangle([x0, y, xs[-1], y + 60], fill=(15, 25, 50))
    for j, c in enumerate(cols):
        d.text(((xs[j] + xs[j + 1]) // 2, y + 30), c, font=F(30, True), fill=YEL if hl_col == j else (200, 210, 230), anchor="mm")
    y += 60
    for i, r in enumerate(rows):
        yy = y + i * rh; on = i in hl_rows
        d.rectangle([x0, yy + 3, xs[-1], yy + rh - 3], fill=(255, 241, 180) if on else (255, 255, 255))
        if on: d.rectangle([x0, yy + 3, x0 + 10, yy + rh - 3], fill=(240, 170, 0))
        for j, c in enumerate(r):
            if j == 0:
                lg = logo_for(c, widths[0] - 40, 40)
                if lg is not None:
                    CANVAS["cv"].paste(lg, (xs[0] + 24, yy + 14), lg)
                    f = F(26, True)
                    while tw(d, c, f) > widths[0] - 36 and f.size > 16: f = F(f.size - 2, True)
                    d.text((xs[0] + 24, yy + rh - 28), c, font=f, fill=(40, 40, 50), anchor="lm")
                else:
                    f = F(36)
                    while tw(d, c, f) > widths[0] - 36 and f.size > 18: f = F(f.size - 2)
                    d.text((xs[0] + 24, yy + rh // 2), c, font=f, fill=(20, 40, 90), anchor="lm")
                continue
            f = F(38, True)
            while tw(d, c, f) > widths[j] - 18 and f.size > 20: f = F(f.size - 2, True)
            col = (200, 30, 40) if (hl_col == j and c not in ("—", "-")) else (30, 30, 40)
            if c in ("—", "-"): col = (170, 170, 178)
            d.text(((xs[j] + xs[j + 1]) // 2, yy + rh // 2), c, font=f, fill=col, anchor="mm")
    ny = y + len(rows) * rh + 34
    for part in note.split("　"):
        if part: d.text((60, ny), part, font=F(26, True), fill=(230, 235, 245), anchor="lm"); ny += 38

def flow(d, y, fl, hl_rows, t_local):
    d.text((60, y), fl["title"], font=F(44), fill=YEL, anchor="lm")
    d.text((60, y + 46), fl["sub"], font=F(24, True), fill=(220, 228, 245), anchor="lm")
    y += 84; rh = 162
    for i, r in enumerate(fl["rows"]):
        app = min(1, max(0, (t_local - i * 0.12) / 0.25))   # 위에서부터 순서대로 등장
        if app <= 0: continue
        yy = y + i * rh; on = i in hl_rows
        x0 = int(40 - (1 - app) * 60)
        d.rounded_rectangle([x0, yy + 6, x0 + 1000, yy + rh - 6], radius=18, fill=(255, 241, 180) if on else (255, 255, 255))
        d.ellipse([x0 + 18, yy + 26, x0 + 78, yy + 86], fill=(230, 160, 0) if i == 0 else (40, 60, 110))
        d.text((x0 + 48, yy + 56), str(i + 1), font=F(36), fill=WHITE, anchor="mm")
        lg = logo_for(r["name"], 230, 36)
        if lg is not None:
            CANVAS["cv"].paste(lg, (x0 + 96, yy + 22), lg)
            d.text((x0 + 96, yy + 78), r["name"], font=F(24, True), fill=(40, 40, 50), anchor="lm")
        else:
            d.text((x0 + 96, yy + 52), r["name"], font=F(36), fill=(20, 40, 90), anchor="lm")
        d.text((x0 + 990, yy + 52), r["score"], font=F(30, True), fill=(200, 30, 40), anchor="rm")
        # 선고 단계 칩
        cx = x0 + 96; cy = yy + 122; f = F(24, True)
        for k, st in enumerate(r["steps"]):
            w_ = tw(d, st, f) + 26
            if cx + w_ > x0 + 990: break
            col = (255, 225, 120) if ("GD" in st or "AI" in st) else (232, 238, 250)
            d.rounded_rectangle([cx, cy - 18, cx + w_, cy + 18], radius=16, fill=col)
            d.text((cx + w_ // 2, cy), st, font=f, fill=(30, 30, 40), anchor="mm"); cx += w_
            if k < len(r["steps"]) - 1:
                d.text((cx + 12, cy), "›", font=F(28, True), fill=(120, 120, 135), anchor="mm"); cx += 24
    ny = y + len(fl["rows"]) * rh + 20
    for part in fl["note"].split("　"):
        if part: d.text((60, ny), part, font=F(24, True), fill=(230, 235, 245), anchor="lm"); ny += 34

def wrap(text, n):
    out, cur = [], ""
    for i, ch in enumerate(text):
        cur += ch
        nxt = text[i + 1] if i + 1 < len(text) else ""
        if (len(cur) >= n and ch in "、。，！？ " or len(cur) >= n + 4) and nxt not in "、。！？」）":
            out.append(cur); cur = ""
    if cur:
        if out and len(cur) <= 2: out[-1] += cur
        else: out.append(cur)
    return out

def karaoke(d, text, prog):
    lines = wrap(text, 15); f = F(50, True)
    n = len(text); lit = int(n * prog); k = 0
    y0 = 1640 - (len(lines) - 1) * 36
    for li, line in enumerate(lines):
        total = tw(d, line, f); x = (W - total) // 2; y = y0 + li * 72
        for ch in line:
            d.text((x, y), ch, font=f, fill=WHITE if k < lit else (160, 170, 190), anchor="lm", stroke_width=3, stroke_fill=(0, 0, 0))
            x += tw(d, ch, f); k += 1

def fixed(d, source, logo):
    f = F(22, True)
    while tw(d, source, f) > W - 72 and f.size > 14: f = F(f.size - 1, True)
    d.text((36, 40), source, font=f, fill=(200, 205, 220), anchor="lm")
    d.text((W // 2, 1868), logo, font=F(40), fill=YEL, anchor="mm")

def wav_len(p):
    with wave.open(p) as w: return w.getnframes() / w.getframerate()

def main(ep_path, work):
    ep = load_ep(ep_path)
    SPEED = getattr(ep, "SPEED", 1.15); GAP = getattr(ep, "GAP", 0.25); PITCH = getattr(ep, "PITCH", 1.0)
    os.makedirs(os.path.join(work, "fast"), exist_ok=True)
    # 1) 나레이션 1.15배 + 타이밍
    timeline = []; t = 0.4
    for sh in ep.SHOTS:
        src = os.path.join(work, "lines", sh["id"] + ".wav"); dst = os.path.join(work, "fast", sh["id"] + ".wav")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-af", f"asetrate=24000*{PITCH},aresample=24000,atempo={SPEED / PITCH:.4f},loudnorm=I=-14:TP=-1.5:LRA=7,silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse", "-ar", "44100", "-ac", "1", dst], check=True)
        dur = wav_len(dst); timeline.append((t, dur, sh)); t += dur + GAP
    total = t + 0.6
    # 2) 프레임
    fd = os.path.join(work, "frames"); os.makedirs(fd, exist_ok=True)
    nfr = int(total * FPS)
    for fi in range(nfr):
        tt = fi / FPS
        cur = timeline[0]
        for st, du, sh in timeline:
            if tt >= st - 0.001: cur = (st, du, sh)
        st, du, sh = cur
        prog = min(1, max(0, (tt - st) / du)); tl = tt - st
        cv = theme_bg(sh["scene"]).copy(); d = ImageDraw.Draw(cv)
        kind = sh["kind"]
        mh = 1056 if kind in ("headline", "cards") else 500
        # 같은 장면이 이어지면 줌을 이어감
        sc_start = min(s for s, _, x in timeline if x["scene"] == sh["scene"])
        media(cv, work, sh["scene"], mh, tt - sc_start); d = ImageDraw.Draw(cv)
        if kind == "headline":
            headline(d, 1110, sh["label"], sh["l1"], sh["l2"], sh.get("kw"), tl)
        elif kind == "cards":
            act = min(len(sh["items"]) - 1, int(prog * len(sh["items"]) * 1.05)) if sh.get("step") else sh.get("active", 0)
            cards(d, 1010, sh["title"], sh["items"], act)
        elif kind == "table":
            tb = ep.TABLES[sh["table"]]; CANVAS["cv"] = cv
            table(d, 470, tb["title"], tb["cols"], tb["rows"], tb["widths"], sh.get("hl_rows", []), sh.get("hl_col"), tb["note"])
        elif kind == "flow":
            CANVAS["cv"] = cv
            fst = min(s_ for s_, _, x in timeline if x.get("flow") == sh["flow"])
            flow(d, 470, ep.FLOWS[sh["flow"]], sh.get("hl_rows", []), tt - fst)
        karaoke(d, sh["sub"], prog)
        fixed(d, ep.SOURCE, ep.LOGO)
        cv.save(os.path.join(fd, f"f{fi:05d}.png"))
    # 3) 오디오: 나레이션 + 효과음 + 작은 BGM
    SR = 44100; mix = np.zeros(int(total * SR) + SR, dtype=np.float32)
    for st, du, sh in timeline:
        with wave.open(os.path.join(work, "fast", sh["id"] + ".wav")) as w:
            a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
        o = int(st * SR); mix[o:o + len(a)] += a * 1.0
        if sh.get("sfx"):
            s = sfx(sh["sfx"], SR); o2 = max(0, int((st - 0.12) * SR)); mix[o2:o2 + len(s)] += s
    mix += bgm(len(mix), SR) * 0.035
    mix = np.clip(mix / max(1.0, np.abs(mix).max() / 0.95), -1, 1)
    ap = os.path.join(work, "audio.wav")
    with wave.open(ap, "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype(np.int16).tobytes())
    out = os.path.join(work, ep.OUT + ".mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", os.path.join(fd, "f%05d.png"), "-i", ap,
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-af", "loudnorm=I=-14:TP=-1.0:LRA=9", "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-shortest", out], check=True)
    print("OUT", out, round(total, 1), "s")
    return out, timeline

def env(n, a, r, SR):
    e = np.ones(n, dtype=np.float32); na = int(a * SR); nr = int(r * SR)
    if na: e[:na] = np.linspace(0, 1, na)
    if nr: e[-nr:] = np.linspace(1, 0, nr)
    return e

def pluck(freqs, dur, SR, vol):
    n = int(dur * SR); tt = np.arange(n) / SR
    y = sum(np.sin(2 * np.pi * f * tt) * np.exp(-tt * 9) for f in freqs) / len(freqs)
    a = int(0.004 * SR); y[:a] *= np.linspace(0, 1, a)
    return (y * vol).astype(np.float32)

def sfx(kind, SR):
    rng = np.random.default_rng(1)
    if kind in ("click", "register"):   # 부드러운 '띵' (강조)
        return pluck((1568, 2349), 0.35, SR, 0.16)
    if kind == "whoosh":                 # 섹션 전환: 올라가는 두 음
        return np.concatenate([pluck((784, 1175), 0.12, SR, 0.13), pluck((1047, 1568), 0.3, SR, 0.14)])
    if kind == "click":
        n = int(0.04 * SR); return (rng.standard_normal(n) * env(n, 0.001, 0.03, SR) * 0.25).astype(np.float32)
    if kind == "notify":
        out = []
        for f_, d_ in ((1318, 0.09), (1760, 0.16)):
            n = int(d_ * SR); tt = np.arange(n) / SR; out.append(np.sin(2 * np.pi * f_ * tt) * env(n, 0.005, d_ * 0.7, SR) * 0.18)
        return np.concatenate(out).astype(np.float32)
    if kind == "whoosh":
        n = int(0.35 * SR); x = rng.standard_normal(n); k = np.exp(-np.linspace(4, 0.5, n))
        y = np.convolve(x, np.ones(30) / 30, "same") * np.sin(np.linspace(0, np.pi, n)) * 0.22
        return y.astype(np.float32)
    if kind == "register":
        n = int(0.5 * SR); tt = np.arange(n) / SR
        y = sum(np.sin(2 * np.pi * f_ * tt) * np.exp(-tt * 7) for f_ in (2093, 2637, 3136)) * 0.08
        c = rng.standard_normal(int(0.03 * SR)) * 0.15; y[:len(c)] += c
        return y.astype(np.float32)
    return np.zeros(1, dtype=np.float32)

def bgm(n, SR):
    tt = np.arange(n) / SR; bpm = 96; beat = 60 / bpm
    chords = [(220, 277, 330), (196, 247, 294), (175, 220, 262), (196, 247, 294)]
    y = np.zeros(n, dtype=np.float32)
    for i in range(int(n / SR / (beat * 4)) + 1):
        f3 = chords[i % 4]; o = int(i * beat * 4 * SR); m = int(beat * 4 * SR); seg = tt[:m]
        tone = sum(np.sin(2 * np.pi * f * seg) for f in f3) / 3 * np.exp(-seg * 0.6)
        e = min(n, o + m); y[o:e] += tone[:e - o].astype(np.float32)
    return y

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
