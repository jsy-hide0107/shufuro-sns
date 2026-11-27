"""나레이션판 회차 빌더 (2026-11-27)
TikTok에서 나레이션이 들어간 NTT편이 좋아요 최다 → 기업 3사 템플릿(make_reel_v4)에 나레이션을 얹는 버전.
화면 구간(훅 / 카드1~3 / 마지막 표)의 길이를 나레이션 길이에 맞춰 늘린다.
구간 안에서는 템플릿 애니메이션을 1:1로 재생하고, 끝나면 마지막 프레임에서 멈춘다.

사용: python3 make_ep_narr.py episodes/ep06_chiiki2.py <lines_dir> [SPEED] [PITCH]
  lines_dir 에 00.wav(훅) 01~03.wav(카드) 04.wav(표) — Qwen3-TTS 로 생성
출력: ../media/<OUT>_n_ig.mp4 (나레이션+BGM+효과음, TikTok/IG 공용), _n_ig_cover.png
"""
import os, sys, subprocess, wave
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_reel_v2 as base
import make_reel_v4 as v4
from make_ep import load_episode

PAD_IN, PAD_OUT = 0.25, 0.35

def prep(src, dst, speed, pitch):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-af",
                    f"asetrate=24000*{pitch},aresample=24000,atempo={speed / pitch:.4f},"
                    "silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
                    "loudnorm=I=-14:TP=-1.5:LRA=7", "-ar", str(base.SR), "-ac", "1", dst], check=True)
    with wave.open(dst) as w:
        return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768

def main(ep_path, lines, speed=1.25, pitch=1.04):
    cfg = load_episode(ep_path)
    n = len(v4.COMPANIES)
    # 원래 템플릿의 구간 (시작, 길이)
    orig = [(0.0, v4.T_CARDS)] + [(v4.T_CARDS + k * v4.CARD, v4.CARD) for k in range(n)] + [(v4.T_TABLE, v4.T_END - v4.T_TABLE)]
    voices = []
    for i in range(n + 2):
        voices.append(prep(f"{lines}/{i:02d}.wav", f"/tmp/narr_{i:02d}.wav", speed, pitch))
    segs = []; t = 0.0
    for i, a in enumerate(voices):
        d = max(orig[i][1] * 0.6, PAD_IN + len(a) / base.SR + PAD_OUT)
        segs.append((t, d)); t += d
    end = t + 0.6
    def fwd(tt):
        for (ns, nd), (os_, od) in zip(segs, orig):
            if tt < ns + nd: return os_ + min(tt - ns, od - 0.04)
        return orig[-1][0] + orig[-1][1] - 0.04
    out = os.path.join(HERE, "..", "media", cfg["OUT"] + "_n")
    frames = os.path.join(HERE, "frames_ep"); os.makedirs(frames, exist_ok=True)
    for f in os.listdir(frames): os.remove(os.path.join(frames, f))
    for i in range(int(end * v4.FPS)):
        v4.render(fwd(i / v4.FPS)).save(f"{frames}/f{i:04d}.png")
    v4.render(cfg.get("COVER_T", 1.9)).convert("RGB").save(out + "_ig_cover.png")
    # 소리: BGM(나레이션 중 덕킹) + 효과음(작게) + 나레이션
    total = int((end + 1) * base.SR)
    vo = np.zeros(total, np.float32); fx = np.zeros(total, np.float32)
    for (ns, nd), a in zip(segs, voices):
        o = int((ns + PAD_IN) * base.SR); vo[o:o + len(a)] += a
    for tt, kind in v4.sfx_events():
        for (ns, nd), (os_, od) in zip(segs, orig):
            if os_ <= tt < os_ + od:
                nt = ns + (tt - os_)
                if nt < ns + nd:
                    s = base.sfx(kind); o = int(nt * base.SR); e = min(total, o + len(s)); fx[o:e] += s[:e - o]
                break
    bg = base.bgm(total / base.SR)[:total]
    bg = np.pad(bg, (0, total - len(bg)))
    bg = bg / max(1e-6, np.abs(bg).max())
    k = int(0.3 * base.SR)
    act = np.convolve((np.abs(vo) > 0.02).astype(np.float32), np.ones(k) / k, "same")
    duck = 1 - 0.6 * np.clip(act * 3, 0, 1)
    fxn = fx / max(1e-6, np.abs(fx).max())
    mix = vo * 1.0 + bg * 0.22 * duck + fxn * 0.18
    fade = int(0.6 * base.SR); mix[-fade:] *= np.linspace(1, 0, fade)
    mix = np.clip(mix / max(1.0, np.abs(mix).max() / 0.95), -1, 1)
    wav = "/tmp/narr_mix.wav"
    with wave.open(wav, "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(base.SR); w.writeframes((mix * 32767).astype(np.int16).tobytes())
    subprocess.run(["ffmpeg", "-y", "-framerate", str(v4.FPS), "-i", f"{frames}/f%04d.png", "-i", wav,
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
                    "-af", "loudnorm=I=-14:TP=-1.0:LRA=9", "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
                    "-shortest", "-movflags", "+faststart", out + "_ig.mp4"], check=True, capture_output=True)
    print("done", out, f"{end:.1f}s", [round(d, 1) for _, d in segs])

if __name__ == "__main__":
    a = sys.argv
    main(a[1], a[2], float(a[3]) if len(a) > 3 else 1.25, float(a[4]) if len(a) > 4 else 1.04)
