# jzukaku

国土基本図図郭コード計算ライブラリ。
緯度経度から平面直角座標系（JGD2011）を基準とした図郭コードの算出を行います。
図郭コードは、標準地域メッシュ（緯度経度ベース）とは異なる体系です。

## 図郭コード構成

| レベル | 桁数 | 区画サイズ |
|--------|------|------------|
| 50000 | 4桁（系2桁+区画名2文字） | 30km×40km |
| 5000  | 6桁（+図葉2桁）         | 3km×4km   |
| 2500  | 7桁（+分割1桁 1–4）     | 1.5km×2km |
| 1000  | 8桁（+分割 数字+英字）  | 600m×800m |
| 500   | 8桁（+分割 00–99）      | 300m×400m |

参考: [国土基本図の図郭と図郭コード](https://club.informatix.co.jp/?p=1293)

## インストール

```bash
pip install jzukaku
```

開発用（uv を使う場合）:

```bash
uv sync --extra dev
```

## 使い方

### ライブラリとして

```python
from jzukaku import latlon_to_zukaku, xy_to_zukaku, ZukakuInfo

# 緯度経度から図郭コード（系番号は自動推定）
info = latlon_to_zukaku(35.681236, 139.767125, level=500)
print(info.code)   # 例: 09EB4203
print(info.x_min, info.x_max, info.y_min, info.y_max)

# 系番号を指定
info = latlon_to_zukaku(35.681236, 139.767125, zone=9, level=5000)

# 平面直角座標から
info = xy_to_zukaku(10000.0, 20000.0, zone=9, level=500)
```

### 平面直角座標への変換

```python
from jzukaku import latlon_to_jprcs, get_zone_for_location

zone = get_zone_for_location(35.68, 139.77)  # 緯度経度から系番号推定
x, y = latlon_to_jprcs(35.681236, 139.767125, zone)
```

### CLI

```bash
# uv で実行（uv sync 後）
uv run jzukaku
# または
uv run python main.py
```

## 対応レベル

`50000`, `5000`, `2500`, `1000`, `500`。定数は `jzukaku.LEVEL_50000` などで参照できます。

## 開発

```bash
uv sync --extra dev
uv run pytest
uv run ruff check src/
```

## ライセンス

MIT License
