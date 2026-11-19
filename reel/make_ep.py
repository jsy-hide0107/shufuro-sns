"""슈프로 회차 빌더 (2026-11-19)
make_reel_v4.py 템플릿을 그대로 쓰고, episodes/<회차>.py 의 설정만 바꿔서
IG용(효과음만, _sfx.mp4)과 TikTok용(BGM+효과음, _ig.mp4) 두 버전 + 커버 PNG를 한 번에 만든다.

사용: python3 make_ep.py episodes/ep02_kyuseicho.py
출력: ../media/<OUT>_ig.mp4, ../media/<OUT>_ig_sfx.mp4, ../media/<OUT>_ig_cover.png
(파일명 규칙은 1화 20261117_kakure3_* 와 동일)
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

def main(ep_path):
    cfg = load_episode(ep_path)
    out = os.path.join(HERE, "..", "media", cfg["OUT"])
    frames = os.path.join(HERE, "frames_ep")
    os.makedirs(frames, exist_ok=True)
    for f in os.listdir(frames): os.remove(os.path.join(frames, f))
    for i in range(int(v4.T_END * v4.FPS)):
        v4.render(i / v4.FPS).save(f"{frames}/f{i:04d}.png")
    v4.render(cfg.get("COVER_T", 1.9)).convert("RGB").save(out + "_ig_cover.png")
    base.SFX_EVENTS[:] = v4.sfx_events()
    # TikTok용: BGM + 효과음
    base.build_audio(v4.T_END, "audio_bgm.wav")
    mux(frames, "audio_bgm.wav", out + "_ig.mp4")
    # IG용: 효과음만 (BGM은 IG 라이브러리 음원을 Metricool에서 붙인다)
    orig_bgm = base.bgm
    base.bgm = lambda total: np.zeros(int(total * base.SR))
    base.build_audio(v4.T_END, "audio_sfx.wav")
    base.bgm = orig_bgm
    mux(frames, "audio_sfx.wav", out + "_ig_sfx.mp4")
    for f in ("audio_bgm.wav", "audio_sfx.wav"): os.remove(f)
    print("done", out, f"{v4.T_END:.1f}s")

if __name__ == "__main__":
    main(sys.argv[1])
