# 5화: NTT 그룹편 (3단 정보 레이아웃, 나레이션 = 본인 목소리 복제 / Qwen3-TTS 0.6B)
OUT = "20261127_ntt_group"
SOURCE = "出典：NTT発表・各社採用ページ・マイナビ/リクナビ・OpenWork・外資就活ドットコム・就活の教科書"
LOGO = "シュフロ"
SPEED = 1.3
GAP = 0.12

TABLES = {
    "big": dict(
        title="① 大手5社",
        cols=["会社", "初任給(大卒)", "残業/月", "勤務地"],
        widths=[330, 230, 150, 290],
        rows=[
            ["NTTデータ", "30.0万円", "29.1h", "首都圏中心"],
            ["NTT東日本", "34.0万円※", "22.9h", "東日本17都道県"],
            ["NTT西日本", "29.5万円〜", "—", "西日本＋東京"],
            ["NTTドコモ", "30万円〜※2", "23.6h＊", "全国の支社"],
            ["NTTドコモビジネス", "30万円〜※2", "25.4h＊", "本社：大手町"],
        ],
        note="※一律手当4.02万円込み　※2 NTT発表「主要会社は大卒標準30万円以上」　＊OpenWork社員クチコミ平均　—：公開データなし",
    ),
    "sub": dict(
        title="② 知る人ぞ知る子会社5社",
        cols=["会社", "初任給(大卒)", "残業/月", "ひとこと"],
        widths=[400, 200, 140, 260],
        rows=[
            ["NTTアドバンステクノロジ", "25.3万円", "15.9h", "NTT研究所と連携"],
            ["ドコモ・テクノロジ", "23.7万円〜", "—", "転勤なし"],
            ["NTTデータカスタマサービス", "24.5万円", "22.8h", "有給18.1日"],
            ["ドコモビジネスエンジニアリング", "—", "17.2h", "平均勤続18.7年"],
            ["NTTテクノクロス", "—", "—", "平均勤続18年"],
        ],
        note="初任給：アドバンステクノロジ2027年予定・カスタマサービス2025年実績　—：公開データなし",
    ),
    "region": dict(
        title="③ 地域で働ける3社",
        cols=["会社", "エリア", "ポイント"],
        widths=[360, 160, 480],
        rows=[
            ["NTTデータ九州", "九州", "残業21.9h・年休120日以上"],
            ["NTTデータ関西", "大阪", "平均勤続12.9年"],
            ["NTTデータ北陸", "北陸", "東京・富山・石川・福井"],
        ],
        note="出典：各社採用ページ（リクナビ・マイナビ掲載）",
    ),
}

FLOWS = {
    "big": dict(
        title="選考フロー（就職偏差値が高い順）",
        sub="※偏差値は就活の教科書の非公式な目安",
        rows=[
            dict(name="NTTドコモ", score="偏差値65", steps=["ES", "SPI", "AI面接", "面接", "面接"]),
            dict(name="NTTデータ", score="偏差値63", steps=["ES", "SPI", "面接", "GD/ジョブ", "最終"]),
            dict(name="NTTドコモビジネス", score="偏差値61", steps=["体験記が少なく省略"]),
            dict(name="NTT東日本", score="偏差値60", steps=["ES", "Webテスト", "面接（複数回）"]),
            dict(name="NTT西日本", score="偏差値59", steps=["ES", "玉手箱", "GD", "面接", "面接"]),
        ],
        note="選考：外資就活ドットコム27卒体験記・NTT東日本募集要項　インターン優遇で一部免除あり",
    ),
}

SHOTS = [
    dict(id="01", scene="intro", kind="headline", label="NTTグループ", l1="初任給も残業も", l2="会社ごとに違う", kw="違う",
         sub="NTTグループ、名前は同じでも初任給も残業もけっこう違うんです。", sfx="notify"),
    dict(id="02", scene="intro", kind="cards", title="今日の順番", items=["大手 5社", "知る人ぞ知る子会社 5社", "地域の会社 3社"], step=True,
         sub="今日は大手5社、子会社5社、地域の会社3社の順番で紹介します。", sfx="click"),
    dict(id="03", scene="big", kind="table", table="big", sub="まずは、大手5社から見ていきます。", sfx="whoosh"),
    dict(id="04", scene="big", kind="table", table="big", hl_col=1,
         sub="2026年入社から、主要会社の初任給は大卒で月30万円以上に。", sfx="register"),
    dict(id="05", scene="big", kind="table", table="big", hl_rows=[0, 1], hl_col=2,
         sub="残業はNTT東日本が月22.9時間、NTTデータが29.1時間。", sfx="click"),
    dict(id="06", scene="big", kind="flow", flow="big", sub="選考の流れは会社ごとにけっこう違います。就職偏差値が高い順に並べました。", sfx="whoosh"),
    dict(id="06b", scene="big", kind="flow", flow="big", hl_rows=[0], sub="いちばん上のドコモは、AI面接もふくめて面接が3回。", sfx="click"),
    dict(id="06c", scene="big", kind="flow", flow="big", hl_rows=[4], sub="西日本は、玉手箱のあとにグループディスカッションがあります。", sfx="click"),
    dict(id="07", scene="sub", kind="table", table="sub", sub="次は、名前は地味でも働きやすい子会社5社。", sfx="whoosh"),
    dict(id="08", scene="sub", kind="table", table="sub", hl_rows=[0],
         sub="NTTアドバンステクノロジは、残業が月15.9時間。", sfx="click"),
    dict(id="09", scene="sub", kind="table", table="sub", hl_rows=[1],
         sub="ドコモ・テクノロジは転勤なしで、勤務地は東京と神奈川だけ。", sfx="click"),
    dict(id="10", scene="region", kind="table", table="region", sub="最後は、地元で働ける地域の会社3社。", sfx="whoosh"),
    dict(id="11", scene="region", kind="table", table="region", hl_rows=[0],
         sub="NTTデータ九州は、年間休日が120日以上。", sfx="click"),
    dict(id="12", scene="cta", kind="headline", label="保存してあとで見返そう", l1="選考の管理は", l2="シュフロで", kw="シュフロ",
         sub="気になる会社は保存して、選考の管理はシュフロでどうぞ。", sfx="notify"),
]
