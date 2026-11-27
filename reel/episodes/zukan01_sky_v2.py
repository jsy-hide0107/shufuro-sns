# シュフロ企業図鑑 #01 Sky v2 (2026-11-27 21:30) — 뽕수행님 피드백: 1.9배속, 취준생이 궁금한 것(초임·휴일) 먼저, 구간 공백 최소화, 훅 강화
# 훅 레퍼런스: @takuto_syukatsu AGC편(10.4만 재생) — 첫 2초에 혜택 숫자 2개, 회사명은 끝에 공개, 말 사이 공백 없음
# 출처: research/zukan01_sky_sources.md / 대본 reel/research/zukan01_v2_narration_script.py
THEME = "marker_lavender"
OUT = "20261128_zukan01_sky_v3"
SOURCE = "出典：ワンキャリア・Sky採用ページ ｜ 写真：Wikimedia Commons／Pexels"
BRAND = "シュフロ企業図鑑 #01 ｜ @shufuro_acos"
SPEED = 1.9
PITCH = 1.04
GAP = 0.05
TAIL = 1.6
LINES = [
 dict(id="00", img="typing", caps=["初任給 月31万円", "年間休日 124日"],
      head=("初任給 月[31万円]", "年間休日[124日]"), label="大卒・2026年4月入社／2025年度実績"),
 dict(id="01", img="team", caps=["今回は、28卒にいま一番選ばれている", "あのIT企業"],
      head=("28卒にいま選ばれてる", "[あのIT企業]"), label="シュフロ企業図鑑 #01"),
 dict(id="02", img="team2", caps=["決算賞与は、29年連続"],
      head=("決算賞与", "[29年連続]"), label="業績に応じて支給"),
 dict(id="03", img="calendar", caps=["残業は月16時間くらい", "バースデー休暇もあり"],
      head=("残業 月[16時間]", "バースデー休暇あり"), label="2025年度実績"),
 dict(id="04", img="students", caps=["ワンキャリア28卒ランキング", "IT・通信で2位、前年から10ランクアップ"],
      head=("28卒 IT・通信", "人気[2位]"), label="ワンキャリア 28卒（春期速報）"),
 dict(id="05", img="classroom", caps=["つくっているのは会社のパソコンを守るソフトと", "学校の授業で使うソフト"],
      head=("つくっているのは", "[会社と学校]のソフト"), label="SKYSEA Client View ／ SKYMENU"),
 dict(id="06", img="control", caps=["しかも上場していないのに", "定着率は90%超え"],
      head=("非上場なのに", "定着率[90%超え]"), label="過去5年以上"),
 dict(id="07", img="hq", caps=["この会社は、Sky"],
      head=("この会社は", "[Sky]"), label="東京本社：JR品川イーストビル", slam={0: "Sky"}),
 dict(id="08", img="TABLE", caps=["28卒向けイベントは1月31日まで", "次に調べてほしい会社はコメントで！"]),
]
TABLE_TITLE = "シュフロ企業図鑑 #01 Sky"
TABLE_NOTE = "ワンキャリア（2026年7月）・Sky採用ページ・キャリタス就活（2026年11月時点）"
TABLE = [
 ("待遇", "初任給 月31万円", [("決算賞与", "29年連続"), ("年間休日", "124日"), ("残業", "月16h")]),
 ("人気", "28卒 IT・通信 2位", [("前年から", "10ランク↑"), ("定着率", "90%超"), ("上場", "なし")]),
 ("28卒", "1DAYイベント受付中", [("締切", "1/31"), ("事業", "PC管理"), ("", "教育ソフト")]),
]
PHOTOS = {"hq": "hq", "students": 8368061, "classroom": 33846282, "typing": 8872743, "calendar": 6170652,
          "team": 7652178, "team2": 7652040, "control": 30481728}
CARDS = []
END = ("次に図鑑にしてほしい会社", "コメントで", "多かった会社から作ります")
