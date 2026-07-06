# MapAI v1.0

CSVに記載された施設一覧を読み込み、住所から緯度・経度を取得して、OpenStreetMap上にピンを表示するPythonツールです。

画像生成AIではなく、OpenStreetMapと実際の座標データを使用します。

## セットアップ方法

```bash
cd MapGenerator
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 実行方法

```bash
python run.py
```

実行すると次の処理を行います。

1. `data/omiya_high_school_tennis_mapai_with_tuition.csv` を読み込みます。
2. 緯度・経度が空の行だけ、住所から座標を取得します。
3. 取得した緯度・経度をCSVへ保存します。
4. `output/school_map.html` を作成します。
5. 住所から座標を取得できなかった行は `output/error_log.csv` に出力します。

2回目以降は、CSVに緯度・経度が入っている行は再取得しません。

住所検索は `geopy` を使用します。初期設定ではNominatimを試し、見つからない場合は日本住所に強いArcGISへフォールバックします。地図表示にはOpenStreetMapを使用します。

## Webアプリとして使う

Streamlit版を用意しています。

```bash
streamlit run streamlit_app.py
```

ブラウザで次のことができます。

- CSVアップロード
- サンプルCSVでの地図作成
- 住所から緯度・経度を補完
- 地図HTMLのダウンロード
- 座標入りCSVのダウンロード
- Excelのダウンロード
- 取得できなかった住所の一覧表示

## 無料公開する

Streamlit Community Cloudを使うと、無料でWebアプリとして公開できます。

1. このフォルダの中身をGitHubリポジトリに置きます。
2. Streamlit Community CloudでGitHubリポジトリを選びます。
3. Main file pathに `streamlit_app.py` を指定します。
4. Deployを押すと公開URLが発行されます。

`MapAI/v1.0` のような親フォルダごとGitHubに置く場合は、Main file pathに `v1.0/streamlit_app.py` のように指定してください。

大量の住所を一度に処理すると、住所検索サービス側の制限に当たることがあります。公開版では、まず緯度・経度入りCSVを使う運用にすると安定します。

## CSVフォーマット

標準の列は次のとおりです。

| 列名 | 内容 |
| --- | --- |
| 学校名 | 地図に表示する名称 |
| 区分 | 公立・私立など |
| 偏差値 | ポップアップに表示する値 |
| 住所 | ジオコーディングに使用する住所 |
| 緯度 | 取得済みの緯度。空なら自動取得 |
| 経度 | 取得済みの経度。空なら自動取得 |
| メモ | 任意のメモ |

同梱CSVのように `表示名` や `正式名称` がある場合も、そのまま施設名として使用できます。

## ピンの色

| 区分 | 色 |
| --- | --- |
| 公立 | 青 |
| 私立 | 赤 |
| その他 | 緑 |

## 他の施設マップへの流用

設定は `src/config.py` にまとめています。

店舗、病院、営業先などに使う場合は、CSVを差し替えたうえで、必要に応じて次の項目を変更してください。

- `INPUT_CSV`
- `NAME_COLUMNS`
- `CATEGORY_COLUMN`
- `VALUE_COLUMN`
- `ADDRESS_COLUMN`
- `LATITUDE_COLUMN`
- `LONGITUDE_COLUMN`
- `CATEGORY_COLORS`

施設名、区分、住所、緯度、経度の列を合わせれば、学校以外のCSVでも同じ仕組みで地図を作れます。

同梱サンプルCSVは、大宮駅周辺から通いやすい高校候補を、部活動、目安学費、自転車時間つきでまとめたものです。
