"""シュフロ 就活秘書カルーセル renderer (1080x1350, IG 4:5)
usage: python make_carousel.py  -> carousel/c01_december/slide_01..07.png
"""
from PIL import Image, ImageDraw, ImageFont
import os
W, H = 1080, 1350
BG = (250, 247, 240); INK = (30, 40, 66); SUB = (110, 118, 135)
MINT = (120, 222, 196); CORAL = (255, 122, 92); CARD = (255, 255, 255)
BLACK = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
REG = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
BOLD = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
def F(path, size):
    if not os.path.exists(path): path = BLACK
    return ImageFont.truetype(path, size, index=0)  # index0 = JP
OUT = os.path.join(os.path.dirname(__file__), "c01_december")
TOTAL = 7

def chrome(d, n):
    # 左上ラベル / 右上ページ / 28卒バッジ / 下部ハンドル
    d.rounded_rectangle((60, 60, 470, 122), 31, fill=INK)
    d.text((88, 70), "シュフロ｜就活秘書メモ", font=F(BOLD, 32), fill=BG)
    d.rounded_rectangle((490, 60, 610, 122), 31, outline=INK, width=4)
    d.text((512, 70), "28卒", font=F(BLACK, 32), fill=INK)
    d.text((W-60, 72), f"{n}/{TOTAL}", font=F(BOLD, 34), fill=SUB, anchor="ra")
    d.text((W//2, H-70), "@shufuro_acos", font=F(BOLD, 30), fill=SUB, anchor="ms")
    if n < TOTAL:
        d.text((W-60, H-70), "スワイプ →", font=F(BOLD, 30), fill=CORAL, anchor="rs")

def hl_text(d, xy, parts, font, anchor_center=False):
    """parts: [(text, highlight_bool)]  マーカー風（下半分にミント帯）"""
    x, y = xy
    total = sum(d.textlength(t, font=font) for t, _ in parts)
    if anchor_center: x = (W - total) / 2
    asc, desc = font.getmetrics()
    for t, h in parts:
        w = d.textlength(t, font=font)
        if h:
            d.rectangle((x-6, y + asc*0.55, x + w + 6, y + asc + desc*0.35), fill=MINT)
        x += w
    x = xy[0] if not anchor_center else (W - total) / 2
    for t, h in parts:
        d.text((x, y), t, font=font, fill=INK); x += d.textlength(t, font=font)
    return asc + desc

def new(n):
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im); chrome(d, n); return im, d

def card(d, box):
    x0, y0, x1, y1 = box
    d.rounded_rectangle((x0+8, y0+10, x1+8, y1+10), 36, fill=(232, 228, 218))
    d.rounded_rectangle(box, 36, fill=CARD)

def body(d, x, y, lines, size=44, gap=22, color=INK, font=REG):
    f = F(font, size)
    for ln in lines:
        d.text((x, y), ln, font=f, fill=color); y += size + gap
    return y

def save(im, n):
    os.makedirs(OUT, exist_ok=True); im.save(f"{OUT}/slide_{n:02d}.png")

# 1 cover
im, d = new(1)
d.text((W//2, 300), "【保存版】", font=F(BLACK, 56), fill=CORAL, anchor="ma")
hl_text(d, (0, 420), [("28卒、", False), ("12月", True), ("に", False)], F(BLACK, 120), True)
hl_text(d, (0, 580), [("やること", False)], F(BLACK, 120), True)
hl_text(d, (0, 760), [("3つ", True), ("だけ。", False)], F(BLACK, 170), True)
d.text((W//2, 1040), "やること多すぎて手が止まってる人へ", font=F(BOLD, 44), fill=SUB, anchor="ma")
save(im, 1)

# 2-4 to-dos
todos = [
 ("①", [("冬インターンの", False)], [("締切", True), ("を1か所に", False)],
  ["ナビ、メール、企業HP…", "締切がバラバラだと見落としがち。", "まずは“書き出すだけ”でOK。"],
  "書く項目：企業名／締切日／提出物"),
 ("②", [("Webテストを", False)], [("1回だけ", True), ("解く", False)],
  ["SPI、玉手箱など、形式は企業ごとに違う。", "1回解くだけで“自分の苦手”が見える。"],
  "まずは1回、時間を測ってやってみる"),
 ("③", [("ガクチカを", False)], [("1分", True), ("で話せるように", False)],
  ["ESを書く前に、口で話せるか確認。", "話せたら、書くのは意外とラク。"],
  "順番：結論→きっかけ→行動→結果→学び"),
]
for i, (num, l1, l2, lines, tip) in enumerate(todos):
    n = i + 2; im, d = new(n)
    d.ellipse((W//2-75, 230, W//2+75, 380), fill=INK)
    d.text((W//2, 305), num, font=F(BLACK, 90), fill=BG, anchor="mm")
    hl_text(d, (0, 440), l1, F(BLACK, 84), True)
    hl_text(d, (0, 560), l2, F(BLACK, 84), True)
    ch = 100 + len(lines)*68
    top = 760 + (3-len(lines))*34   # 行数が少ない時は中央寄せ
    card(d, (90, top, W-90, top+ch))
    body(d, 140, top+50, lines, size=42, gap=26)
    ty = top + ch + 50
    d.rounded_rectangle((90, ty, W-90, ty+90), 45, fill=INK)
    d.text((W//2, ty+45), tip, font=F(BOLD, 38), fill=BG, anchor="mm")
    save(im, n)

# 5 not everything
im, d = new(5)
hl_text(d, (0, 380), [("全部じゃなくて", False)], F(BLACK, 96), True)
hl_text(d, (0, 510), [("大丈夫。", True)], F(BLACK, 130), True)
body(d, 0, 0, [])
for k, t in enumerate(["今週はひとつだけ。", "できたら、次へ。", "それで十分前に進んでる。"]):
    d.text((W//2, 800 + k*90), t, font=F(BOLD, 52), fill=INK if k < 2 else SUB, anchor="ma")
save(im, 5)

# 6 checklist
im, d = new(6)
hl_text(d, (0, 220), [("12月", True), ("チェックリスト", False)], F(BLACK, 84), True)
d.text((W//2, 345), "スクショして使ってね", font=F(BOLD, 40), fill=CORAL, anchor="ma")
card(d, (90, 440, W-90, 1160))
items = ["冬インターンの締切を書き出した", "気になる企業を5社メモした", "Webテストを1回解いた",
         "ガクチカを1分で話してみた", "来週やることを1つ決めた"]
for k, t in enumerate(items):
    y = 500 + k*128
    d.rounded_rectangle((140, y, 200, y+60), 12, outline=INK, width=5)
    d.text((235, y+2), t, font=F(BOLD, 46), fill=INK)
save(im, 6)

# 7 follow
im, d = new(7)
d.text((W//2, 300), "シュフロは", font=F(BOLD, 52), fill=SUB, anchor="ma")
hl_text(d, (0, 390), [("28卒の", False), ("就活秘書", True)], F(BLACK, 110), True)
for k, t in enumerate(["毎週「今週やること」を", "まとめてお届けします。"]):
    d.text((W//2, 620 + k*80), t, font=F(BOLD, 52), fill=INK, anchor="ma")
d.rounded_rectangle((160, 860, W-160, 980), 60, fill=CORAL)
d.text((W//2, 920), "フォローして見逃さない", font=F(BLACK, 54), fill=(255,255,255), anchor="mm")
d.text((W//2, 1050), "今の悩み、コメントで教えてね", font=F(BOLD, 44), fill=INK, anchor="ma")
save(im, 7)
print("done", OUT)
