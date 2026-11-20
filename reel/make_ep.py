"""슈프로 회차 빌더 (2026-11-19)
make_reel_v4.py 템플릿을 그대로 쓰고, episodes/<회차>.py 의 설정만 바꿔서
IG용(효과음만, _sfx.mp4)과 TikTok용(BGM+효과음, _ig.mp4) 두 버전 + 커버 PNG를 한 번에 만든다.

사용: python3 make_ep.py episodes/ep02_kyuseicho.py [--short]
출력: ../media/<OUT>_ig.mp4, ../media/<OUT>_ig_sfx.mp4, ../media/<OUT>_ig_cover.png
      --short 이면 <OUT>_s_ig.mp4 / _s_ig_sfx.mp4 / _s_ig_cover.png (약 15초 압축판)
(파일명 규칙은 1화 20261117_kakure3_* 와 동일)

--short (2026-11-20 추가): 1~2화 분석에서 평균 시청 4.6~8초/26초였기 때문에 만든 압축판.
템플릿 화면은 그대로 두고 시간축만 줄인다. 훅 1.5초 → 카드 3.5초 x3 → 마지막 표 3.5초 = 15.5초.
"""
import os, sys, subprocess, runpy
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_reel_v2 as base
import make_reel_v4 as v4

def load_episode(path):
    cfg = runpy.run_path(path)
    for key in ("SERIES", "THEME", "SOURCE", "COMPANIES", "HOOK"):
        if key in cfg:
            setattr(v4, key, cfg[key])
    v4.IND_COL.update(cfg.get("IND_COL", {}))
    v4.T_TABLE = v4.T_CARDS + v4.CARD * len(v4.COMPANIES)
    v4.T_END = v4.T_TABLE + 5.0
    return cfg

def mux(frames, wav, out):
    subprocess.run(["ffmpeg", "-y", "-framerate", str(v4.FPS), "-i", f"{frames}/f%04d.png", "-i", wav,
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out],
                   check=True, capture_output=True)

SHORT = (1.5, 3.5, 3.5)  # 훅, 카드 1장, 마지막 표 (초)

def make_timemap(short):
    """새 영상 시각 -> 원래 템플릿 시각. short=None 이면 그대로."""
    n = len(v4.COMPANIES)
    if not short:
        return (lambda t: t), v4.T_END, (lambda t: t)
    H, C, TB = short
    end = H + C * n + TB
    def fwd(t):  # new -> orig
        if t < H: return t * (v4.T_CARDS / H)
        if t < H + C * n:
            k = int((t - H) // C); loc = t - H - k * C
            return v4.T_CARDS + k * v4.CARD + loc * (v4.CARD / C)
        return v4.T_TABLE + (t - H - C * n)
    def inv(t):  # orig -> new (효과음 위치용)
        if t < v4.T_CARDS: return t * (H / v4.T_CARDS)
        if t < v4.T_TABLE:
            k = int((t - v4.T_CARDS) // v4.CARD); loc = t - v4.T_CARDS - k * v4.CARD
            return H + k * C + loc * (C / v4.CARD)
        return H + C * n + (t - v4.T_TABLE)
    return fwd, end, inv

def main(ep_path, short=False):
    cfg = load_episode(ep_path)
    fwd, end, inv = make_timemap(SHORT if short else None)
    suffix = "_s" if short else ""
    out = os.path.join(HERE, "..", "media", cfg["OUT"] + suffix)
    frames = os.path.join(HERE, "frames_ep")
    os.makedirs(frames, exist_ok=True)
    for f in os.listdir(frames): os.remove(os.path.join(frames, f))
    for i in range(int(end * v4.FPS)):
        v4.render(fwd(i / v4.FPS)).save(f"{frames}/f{i:04d}.png")
    v4.render(cfg.get("COVER_T", 1.9)).convert("RGB").save(out + "_ig_cover.png")
    base.SFX_EVENTS[:] = [(inv(t), name) for t, name in v4.sfx_events() if inv(t) < end]
    # TikTok용: BGM + 효과음
    base.build_audio(end, "audio_bgm.wav")
    mux(frames, "audio_bgm.wav", out + "_ig.mp4")
    # IG용: 효과음만 (BGM은 IG 라이브러리 음원을 Metricool에서 붙인다)
    orig_bgm = base.bgm
    base.bgm = lambda total: np.zeros(int(total * base.SR))
    base.build_audio(end, "audio_sfx.wav")
    base.bgm = orig_bgm
    mux(frames, "audio_sfx.wav", out + "_ig_sfx.mp4")
    for f in ("audio_bgm.wav", "audio_sfx.wav"): os.remove(f)
    print("done", out, f"{end:.1f}s")

if __name__ == "__main__":
    main(sys.argv[1], short="--short" in sys.argv[2:])
