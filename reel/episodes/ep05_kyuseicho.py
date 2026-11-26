# 5화: 목요일 테마 「急成長企業」 (2026-11-26 게시) — 훅 숫자 종류 시험: 휴일(年間休日)
# 출처 (2026-11-26 확인)
#  ビジネスエンジニアリング(B-EN-G, 4828)
#   - 売上 20,776→24,442百万円(+17.6%, 2026年3月期 決算短信) https://www2.jpx.co.jp/disc/48280/081220260624579163_tse-acedjpsm-48280-20260626348280-ixbrl.htm
#   - 平均年間給与 9,149千円・580名・40.3歳・勤続11.1年 (有報 2026年3月期 提出会社) https://disclosure2dl.edinet-fsa.go.jp/searchdocument/pdf/S100YD7D.pdf
#   - 28卒: マイナビ2028 仕事体験(応募締切 2027/2/9) https://job.mynavi.jp/28/pc/search/corp71686/is.html
#   - 年間休日124日・独身寮(月3.5万円自己負担・4年間)・持株会奨励金10%・選考(説明会→ES→適性検査→面接3回) — マイナビ2027 募集要項(27卒条件) https://job.mynavi.jp/27/pc/search/corp71686/employment.html
#  HENNGE(4475)
#   - 売上 10,924→12,782百万円(+17.0%, 2026年9月期 決算短信) https://www2.jpx.co.jp/disc/44750/081220261102562428_tse-acedjpsm-44750-20261105344750-ixbrl.htm
#   - 平均年間給与 8,478千円・378人・35.3歳 (有報 2025年9月期 提出会社 / 2026年9月期有報は12/18提出予定) https://disclosure2dl.edinet-fsa.go.jp/searchdocument/pdf/S100XCC9.pdf
#   - 28卒: 公式「【28卒】ビジネス総合職」 https://recruit.hennge.com/new-graduates/apply/?gh_jid=8166531 / https://recruit.hennge.com/new-graduates-page/
#   - 年間休日120日以上・英語手当 月1万〜11万円・持株会奨励金35%・選考(書類→録画面接→面接3回) — 同求人票・https://recruit.hennge.com/workstyle/
#  JMDC(4483)
#   - 売上収益 41,722→50,462百万円(+20.9%, 2026年3月期 決算短信 IFRS) https://www2.jpx.co.jp/disc/44830/081220260501516567_tse-acedifsm-44830-20260508344830-ixbrl.htm
#   - 平均年間給与 8,227,757円・499人・39.4歳 (有報 2026年3月期 提出会社) https://disclosure2dl.edinet-fsa.go.jp/searchdocument/pdf/S100YJCA.pdf
#   - 28卒: 公式 HRMOS「ビジネス総合職（28卒）」 https://hrmos.co/pages/jmdc/jobs/nw-00028 / 説明会(28卒) https://hrmos.co/pages/jmdc/jobs/nw-00027
#   - 1週間休暇制度(最大9連休)・健康年齢インセンティブ・通勤手当上限15万円/月 — 同 nw-00028 / 年間休日日数・初任給は未確認(非公開)
#   - 選考: 外資就活 2028卒 早期本選考 https://gaishishukatsu.com/recruiting_info/view/14110 (書類→AI面接→面接)
OUT = "20261126_kyuseicho3"
SERIES = "今日の急成長企業3社"
THEME = "伸びてるのに、ちゃんと休める"
SOURCE = "出典：有価証券報告書／決算短信／各社採用ページ"
IND_COL = {"製造業向けIT": (0, 140, 220), "クラウド認証": (230, 60, 90), "医療データ": (40, 180, 120)}

# name, industry, what, stats x4, feature, flow, hire
COMPANIES = [
    ("ビジネスエンジニアリング", "製造業向けIT", "工場の業務システム「mcframe」を自社開発",
     [("平均年収", "914.9万円"), ("売上の伸び", "+17.6%"), ("年間休日", "124日"), ("従業員", "580人")],
     "独身寮は自己負担 月3.5万円で4年間", ["ES・適性検査", "面接3回"], "28卒 受付中"),
    ("HENNGE", "クラウド認証", "会社のクラウドへのログインを守る「HENNGE One」",
     [("平均年収", "847.8万円"), ("売上の伸び", "+17.0%"), ("年間休日", "120日以上"), ("従業員", "378人")],
     "英語手当 月1万〜11万円・持株会奨励金35%", ["書類・録画面接", "面接3回"], "28卒 受付中"),
    ("JMDC", "医療データ", "医療ビッグデータで健保や製薬会社を支える",
     [("平均年収", "822.8万円"), ("売上の伸び", "+20.9%"), ("連休制度", "最大9連休"), ("従業員", "499人")],
     "年1回の1週間休暇・健康年齢でポイント", ["書類", "AI面接・面接"], "28卒 受付中"),
]

from make_reel_v2 import WHITE, YEL, RED
HOOK = [("3社とも売上+17%以上", 80, WHITE), ("年間休日124日", 116, YEL), ("伸びてるのに休める", 92, WHITE), ("BtoB企業を3つ紹介", 84, RED)]
