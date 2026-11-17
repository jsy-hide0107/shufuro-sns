# shufuro-sns

シュフロ SNS 運用の自動化用リポジトリ。

- `reel/` — 縦型ショート動画テンプレート（Python + Pillow + ffmpeg）
  - `make_reel_v4.py` — 「今日の穴場ホワイト3社」企業カード型（ロゴ・平均年収・選考・新卒採用）
  - `fetch_logo.py` — 企業公式サイトからロゴ取得
- `media/` — 投稿用の完成動画（Metricool が raw URL から取得）
- `handover.md` — 運用の引き継ぎ資料

依存: `pip install pillow numpy cairosvg` / ffmpeg / Noto Sans CJK
