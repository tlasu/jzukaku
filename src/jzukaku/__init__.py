"""
jzukaku - 国土基本図図郭コード計算ライブラリ

平面直角座標系（JGD2011）を基準とした図郭コードの計算を行います。
標準地域メッシュ（緯度経度ベース）とは異なる体系です。

使用例::

    from jzukaku import latlon_to_zukaku, xy_to_zukaku, ZukakuInfo

    # 緯度経度から図郭コードを取得（系番号は自動推定）
    info = latlon_to_zukaku(35.681236, 139.767125, level=500)

    # 系番号を指定する場合
    info = latlon_to_zukaku(35.681236, 139.767125, zone=9, level=5000)

    # 平面直角座標から図郭コードを取得
    info = xy_to_zukaku(10000.0, 20000.0, zone=9, level=500)
"""

from .constants import (
    JGD2011_ORIGINS,
    LEVEL_500,
    LEVEL_1000,
    LEVEL_2500,
    LEVEL_5000,
    LEVEL_50000,
    SUPPORTED_LEVELS,
)
from .jprcs import JGD2011_EPSG, get_zone_for_location, latlon_to_jprcs
from .zukaku import ZukakuInfo, bbox_to_zukaku, latlon_to_zukaku, xy_to_zukaku

__all__ = [
    "ZukakuInfo",
    "JGD2011_ORIGINS",
    "LEVEL_500",
    "LEVEL_1000",
    "LEVEL_2500",
    "LEVEL_5000",
    "LEVEL_50000",
    "SUPPORTED_LEVELS",
    "JGD2011_EPSG",
    "latlon_to_jprcs",
    "get_zone_for_location",
    "xy_to_zukaku",
    "latlon_to_zukaku",
    "bbox_to_zukaku",
]

__version__ = "0.1.0"
