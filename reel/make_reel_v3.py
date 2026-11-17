"""슈프로 Reel v3: 「今日の穴場ホワイト3社」 기업 카드형 (매일 시리즈 템플릿)
v2의 스타일·오디오 엔진을 재사용하고, 회사마다 '어떤 회사인지 + 수치 4개 + 특징'을 보여준다.
COMPANIES만 바꾸면 매일 새 편을 만들 수 있다. 수치는 반드시 공식 출처(PR시트·有報)에서.
"""
import os, sys, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_reel_v2 as base
from make_reel_v2 import (W, H, FPS, RED, YEL, BLUE, NAVY, WHITE, BLACK, F, outlined, fit_size, pop,
                          background, paste_scaled, layer)
from PIL import ImageDraw

SERIES = "今日の穴場ホワイト3社"
THEME = "ユースエール認定（厚労省）"
SOURCE = "出典：東京労働局 ユースエールPRシート／有価証券報告書"
IND_COL = {"エネルギー": (255, 140, 0), "IT・セキュリティ": (0, 170, 255), "メーカー": (40, 200, 120)}

# name, industry, what(1행), stats[(label, value)]x4, feature
COMPANIES = [
    ("苫東石油備蓄", "エネルギー", "国家石油備蓄基地の運転・管理",
     [("有給", "18.7日"), ("残業/月", "2.3h"), ("平均勤続", "13.6年"), ("グループ", "JERA")],
     "日本のエネルギー安定供給を支える国の事業"),
    ("サイバーディフェンス研究所", "IT・セキュリティ", "ハッキング診断・フォレンジック・サイバー演習",
     [("有給", "16.6日"), ("残業/月", "12.9h"), ("親会社", "NEC"), ("勤務地", "御茶ノ水")],
     "官公庁・警察などの機関からも依頼"),
    ("アバールデータ", "メーカー", "半導体製造装置向けの電子機器",
     [("有給", "14.6日"), ("残業/月", "9.3h"), ("平均年収", "735万円"), ("男性育休", "92.3%")],
     "東証スタンダード上場・平均勤続16.3年"),
]

T_HOOK, T_CARDS = 0.0, 3.0
CARD = 6.0
T_TABLE = T_CARDS + CARD * len(COMPANIES)
T_END = T_TABLE + 5.0

def top_bar(d):
    d.rectangle((0, 230, W, 420), fill=RED)
    d.rectangle((0, 420, W, 432), fill=YEL)
    outlined(d, (W / 2, 290), THEME, 52, WHITE, sw=5)
    outlined(d, (W / 2, 368), SERIES, 80, YEL, sw=8)

def footer(d, y=None):
    y = y or H - 430
    outlined(d, (W / 2, y), SOURCE, 28, WHITE, sw=3)
    outlined(d, (W / 2, y + 50), "@shufuro_acos", 40, YEL, sw=4)

def scene_hook(t):
    img = background(t, "burst"); d = ImageDraw.Draw(img); top_bar(d)
    for txt, y, sz, col, st in [("知名度ゼロ、でも", 640, 80, WHITE, 0.05),
                                 ("有給18.7日", 800, 130, YEL, 0.5),
                                 ("残業 月2.3時間", 960, 100, WHITE, 1.0),
                                 ("の会社を3つ紹介", 1130, 84, RED, 1.6)]:
        L, ld = layer()
        outlined(ld, (W / 2, y), txt, sz, col, stroke=WHITE if col == RED else BLACK, sw=10)
        paste_scaled(img, L, pop(t, st))
    footer(ImageDraw.Draw(img))
    return img

def monogram(ld, cx, cy, name, ind):
    col = IND_COL.get(ind, BLUE)
    ld.ellipse((cx - 95, cy - 95, cx + 95, cy + 95), fill=col, outline=WHITE, width=8)
    ld.text((cx, cy), name[0], font=F(110), fill=WHITE, anchor="mm", stroke_width=5, stroke_fill=BLACK)

def scene_card(t, k):
    name, ind, what, stats, feat = COMPANIES[k]
    st = T_CARDS + k * CARD
    img = background(t, "stripe"); d = ImageDraw.Draw(img); top_bar(d)
    outlined(d, (W / 2, 490), f"{k+1}社目 / {len(COMPANIES)}", 44, WHITE, sw=5)
    # 헤더: 모노그램 + 업종 태그 + 사명
    L, ld = layer()
    monogram(ld, 190, 650, name, ind)
    col = IND_COL.get(ind, BLUE)
    tw = ld.textlength(ind, font=F(40))
    ld.rounded_rectangle((320, 560, 320 + tw + 50, 625), 32, fill=col, outline=BLACK, width=4)
    ld.text((345, 592), ind, font=F(40), fill=WHITE, anchor="lm", stroke_width=3, stroke_fill=BLACK)
    ns = fit_size(ld, name, 84, W - 360)
    outlined(ld, (320, 700), name, ns, WHITE, sw=9, anchor="lm")
    paste_scaled(img, L, pop(t, st))
    # どんな会社？
    L, ld = layer()
    ld.rounded_rectangle((60, 790, W - 60, 900), 22, fill=WHITE, outline=BLACK, width=6)
    ld.text((100, 845), "どんな会社？", font=F(36), fill=RED, anchor="lm")
    ws = fit_size(ld, what, 44, W - 420)
    ld.text((340, 845), what, font=F(ws), fill=NAVY, anchor="lm")
    paste_scaled(img, L, pop(t, st + 0.5))
    # 수치 4칸
    for i, (lab, val) in enumerate(stats):
        L, ld = layer()
        cx = W / 2 + (-245 if i % 2 == 0 else 245)
        cy = 1030 + (i // 2) * 215
        hl = YEL if i == 0 or "年収" in lab else WHITE
        ld.rounded_rectangle((cx - 225, cy - 95, cx + 225, cy + 95), 26, fill=(0, 0, 0, 180), outline=hl, width=6)
        ld.text((cx, cy - 50), lab, font=F(42), fill=WHITE, anchor="mm")
        vs = fit_size(ld, val, 92, 400)
        outlined(ld, (cx, cy + 30), val, vs, hl, sw=7)
        paste_scaled(img, L, pop(t, st + 1.0 + i * 0.35))
    # 특징
    L, ld = layer()
    fs = fit_size(ld, "★ " + feat, 50, W - 140)
    ld.rounded_rectangle((60, 1370, W - 60, 1470), 50, fill=RED, outline=YEL, width=6)
    ld.text((W / 2, 1420), "★ " + feat, font=F(fs), fill=WHITE, anchor="mm", stroke_width=3, stroke_fill=BLACK)
    paste_scaled(img, L, pop(t, st + 2.6))
    footer(ImageDraw.Draw(img), y=1540)
    return img

def scene_table(t):
    img = background(t, "stripe"); d = ImageDraw.Draw(img); top_bar(d)
    L, ld = layer()
    x0, x1, y = 50, W - 50, 480
    rows = len(COMPANIES)
    rh = 230
    ld.rounded_rectangle((x0, y, x1, y + 110 + rows * rh), 24, fill=WHITE, outline=BLACK, width=8)
    ld.rectangle((x0 + 8, y + 8, x1 - 8, y + 100), fill=NAVY)
    ld.text((W / 2, y + 54), "まとめ（スクショ推奨）", font=F(44), fill=YEL, anchor="mm")
    for i, (name, ind, what, stats, feat) in enumerate(COMPANIES):
        ry = y + 110 + i * rh
        if i % 2 == 0:
            ld.rectangle((x0 + 8, ry, x1 - 8, ry + rh - 6), fill=(240, 243, 255))
        col = IND_COL.get(ind, BLUE)
        ld.rounded_rectangle((x0 + 30, ry + 22, x0 + 30 + ld.textlength(ind, font=F(30)) + 30, ry + 66), 22, fill=col)
        ld.text((x0 + 45, ry + 44), ind, font=F(30), fill=WHITE, anchor="lm")
        ns = fit_size(ld, name, 52, 900)
        ld.text((x0 + 30, ry + 110), name, font=F(ns), fill=NAVY, anchor="lm")
        line = "　".join(f"{a} {b}" for a, b in stats)
        ls = fit_size(ld, line, 36, 920)
        ld.text((x0 + 30, ry + 180), line, font=F(ls), fill=RED, anchor="lm")
    paste_scaled(img, L, pop(t, T_TABLE, 0.22))
    L, ld = layer()
    outlined(ld, (W / 2, 1360), "明日も3社紹介します", 60, YEL, sw=7)
    paste_scaled(img, L, pop(t, T_TABLE + 1.0))
    footer(ImageDraw.Draw(img), y=1470)
    return img

def render(t):
    if t < T_CARDS: return scene_hook(t)
    if t < T_TABLE: return scene_card(t, min(len(COMPANIES) - 1, int((t - T_CARDS) / CARD)))
    return scene_table(t)

def sfx_events():
    ev = [(0.05, "pop"), (0.5, "hit"), (1.0, "pop"), (1.6, "hit")]
    for k in range(len(COMPANIES)):
        st = T_CARDS + k * CARD
        ev += [(st, "whoosh"), (st + 0.02, "hit"), (st + 0.5, "pop")]
        ev += [(st + 1.0 + i * 0.35, "pop") for i in range(4)] + [(st + 2.6, "chime")]
    ev += [(T_TABLE, "whoosh"), (T_TABLE + 0.05, "fanfare"), (T_TABLE + 1.0, "chime")]
    return ev

def main(out="reel_v3.mp4", frames="frames3"):
    os.makedirs(frames, exist_ok=True)
    for f in os.listdir(frames): os.remove(os.path.join(frames, f))
    for i in range(int(T_END * FPS)):
        render(i / FPS).save(f"{frames}/f{i:04d}.png")
    render(1.9).save(out.replace(".mp4", "_cover.png"))
    base.SFX_EVENTS[:] = sfx_events()
    base.build_audio(T_END, "audio_v3.wav")
    subprocess.run(["ffmpeg", "-y", "-framerate", str(FPS), "-i", f"{frames}/f%04d.png", "-i", "audio_v3.wav",
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out],
                   check=True, capture_output=True)
    print("done", out)

if __name__ == "__main__":
    main()
