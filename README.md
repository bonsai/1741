# 1741 — 自治体通信簿

全国自治体を共通コードで管理し、分野別・総合ランキングを作るためのデータ基盤です。

## 最初に作るデータ

- `data/municipality_sites_candidates.jsonl`: J-LIS「全国自治体マップ検索」から収集する公式サイト候補
- `data/municipalities.jsonl`: 自治体コードを主キーにした確定マスター（候補URLとの照合後に生成）
- `sources/sources.jsonl`: データソース台帳

## Colabで公式サイト候補を収集

`notebooks/01_collect_official_sites.py` をGoogle Colabにアップロードして実行します。J-LISの47都道府県ページを巡回し、自治体名・公式サイトURL・出典ページをJSONLに出力します。

**注意:** J-LISの全国自治体マップ検索は自治体公式サイトへのリンク集ですが、掲載ページの更新日が古い場合があります。収集結果は「候補」として扱い、現行URL確認・自治体コード照合を経て確定マスターに反映します。政令指定都市の行政区は市の下位ページとして掲載されるため、自治体本体とは別レコードに混ぜないようにします。東京都の特別区は自治体として扱います。

## JSONL方針

- 1行1レコード、UTF-8
- 主キーは全国地方公共団体コード（6桁コードを文字列として保持）
- URLは確認できない場合 `null`。推測で補完しない
- `source_url`、`retrieved_at`、`verification_status` を記録
- 未確認・未収録を「存在しない」と解釈しない

## 主要な参照元

- e-Stat 市区町村名・コード: https://www.e-stat.go.jp/municipalities/cities
- J-LIS 全国自治体マップ検索: https://www.j-lis.go.jp/spd/map-search/cms_1069.html
- 総務省 全国地方公共団体コード: https://www.soumu.go.jp/denshijiti/code.html

## Scope

初期対象は基礎自治体。政令指定都市の行政区、郡、支庁、一部事務組合は別の階層・データセットで管理します。東京23特別区は対象に含めます。
