"""회사 공식 사이트에서 로고 후보를 찾아 내려받는다.
사용법: python3 fetch_logo.py <사명> <공식사이트URL> [출력폴더]
우선순위: <img>의 src/alt/class에 logo 포함 → apple-touch-icon → og:image
SVG는 cairosvg로 PNG 변환. 결과는 logos/<사명>.png
"""
import io, os, re, sys, urllib.request
from urllib.parse import urljoin
from PIL import Image

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "ja"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read(), r.headers.get("Content-Type", "")

def candidates(html, base):
    out = []
    for m in re.finditer(r"<img\b[^>]*>", html, re.I):
        tag = m.group(0)
        src = re.search(r'src=["\']([^"\']+)', tag, re.I)
        if src and re.search(r"logo", tag, re.I):
            out.append(urljoin(base, src.group(1)))
    for pat in [r'<link[^>]+rel=["\']apple-touch-icon[^"\']*["\'][^>]*href=["\']([^"\']+)',
                r'<link[^>]+href=["\']([^"\']+)["\'][^>]*rel=["\']apple-touch-icon',
                r'<meta[^>]+property=["\']og:image["\'][^>]*content=["\']([^"\']+)']:
        for m in re.finditer(pat, html, re.I):
            out.append(urljoin(base, m.group(1)))
    seen, uniq = set(), []
    for u in out:
        if u not in seen:
            seen.add(u); uniq.append(u)
    return uniq

def to_png(data, ctype, url):
    if "svg" in ctype or url.lower().split("?")[0].endswith(".svg"):
        import cairosvg
        data = cairosvg.svg2png(bytestring=data, output_width=600)
    img = Image.open(io.BytesIO(data)).convert("RGBA")
    bbox = img.getbbox()
    return img.crop(bbox) if bbox else img

def main(name, site, outdir="logos"):
    os.makedirs(outdir, exist_ok=True)
    html, _ = get(site)
    html = html.decode("utf-8", "ignore")
    cands = candidates(html, site)
    print("candidates:", cands[:6])
    for u in cands:
        try:
            data, ctype = get(u)
            img = to_png(data, ctype, u)
            if img.width < 40 or img.height < 20:
                continue
            path = os.path.join(outdir, f"{name}.png")
            img.save(path)
            print("saved", path, img.size, "from", u)
            return path
        except Exception as e:
            print("skip", u, e)
    print("no logo found for", name)

if __name__ == "__main__":
    main(*sys.argv[1:])
