"""
平面直角座標系（JGD2011）変換

緯度経度と平面直角座標（XY）の相互変換、系番号の推定。
座標変換は pyproj を使用し、フォールバック用の純 Python 実装も備える。
"""

import math
from typing import Optional, Tuple

from pyproj import Transformer

from .constants import JGD2011_ORIGINS

# JGD2011 地理座標系
_CRS_JGD2011_GEO = "EPSG:6668"

# JGD2011 平面直角座標系 系番号 → EPSG コード
JGD2011_EPSG = {z: 6668 + z for z in range(1, 20)}

# Transformer のキャッシュ（系番号ごと）
_transformer_cache: dict[int, Transformer] = {}


def _get_transformer(zone: int) -> Transformer:
    """系番号に対応する Transformer を取得（キャッシュ付き）"""
    if zone not in _transformer_cache:
        epsg = JGD2011_EPSG[zone]
        _transformer_cache[zone] = Transformer.from_crs(
            _CRS_JGD2011_GEO, f"EPSG:{epsg}", always_xy=True,
        )
    return _transformer_cache[zone]


def latlon_to_jprcs(
    lat: float,
    lon: float,
    zone: Optional[int] = None,
) -> Tuple[float, float]:
    """
    緯度経度を平面直角座標系のXY座標に変換する（pyproj 使用）。

    Parameters:
        lat: 緯度（度）
        lon: 経度（度）
        zone: 系番号（1-19）。None のとき自動推定。

    Returns:
        (X, Y): X=南北方向（北が正）, Y=東西方向（東が正）単位:メートル
    """
    if zone is None:
        zone = get_zone_for_location(lat, lon)

    if zone not in JGD2011_EPSG:
        raise ValueError(f"無効な系番号: {zone}")

    transformer = _get_transformer(zone)
    # always_xy=True: input (lon, lat), output (easting, northing)
    easting, northing = transformer.transform(lon, lat)
    # 本ライブラリは (X=northing, Y=easting) で返す
    return northing, easting


def _latlon_to_jprcs_pure(lat: float, lon: float, zone: int) -> Tuple[float, float]:
    """
    純 Python による Gauss-Krüger 変換（pyproj 不使用のフォールバック）。

    pyproj が利用できない環境向け。latlon_to_jprcs と同じ結果を返す。
    """
    if zone not in JGD2011_ORIGINS:
        raise ValueError(f"無効な系番号: {zone}")

    lat0, lon0 = JGD2011_ORIGINS[zone]
    a = 6378137.0
    f = 1 / 298.257222101
    n = f / (2 - f)
    n2, n3, n4, n5 = n * n, n * n * n, n * n * n * n, n * n * n * n * n
    e = 2 * math.sqrt(n) / (1 + n)  # first eccentricity

    A0 = 1 + n2 / 4 + n4 / 64
    A_bar = a / (1 + n) * A0
    alpha1 = 1/2*n - 2/3*n2 + 5/16*n3 + 41/180*n4 - 127/288*n5
    alpha2 = 13/48*n2 - 3/5*n3 + 557/1440*n4 + 281/630*n5
    alpha3 = 61/240*n3 - 103/140*n4 + 15061/26880*n5
    alpha4 = 49561/161280*n4 - 179/168*n5
    alpha5 = 34729/80640*n5

    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)
    lat0_rad = math.radians(lat0)
    lon0_rad = math.radians(lon0)
    dlon = lon_rad - lon0_rad

    t = math.sinh(
        math.atanh(math.sin(lat_rad))
        - e * math.atanh(e * math.sin(lat_rad))
    )
    t_bar = math.sqrt(1 + t * t)
    xi = math.atan2(t, math.cos(dlon))
    eta = math.atanh(math.sin(dlon) / t_bar)

    X = A_bar * (xi + alpha1*math.sin(2*xi)*math.cosh(2*eta)
                    + alpha2*math.sin(4*xi)*math.cosh(4*eta)
                    + alpha3*math.sin(6*xi)*math.cosh(6*eta)
                    + alpha4*math.sin(8*xi)*math.cosh(8*eta)
                    + alpha5*math.sin(10*xi)*math.cosh(10*eta))
    Y = A_bar * (eta + alpha1*math.cos(2*xi)*math.sinh(2*eta)
                     + alpha2*math.cos(4*xi)*math.sinh(4*eta)
                     + alpha3*math.cos(6*xi)*math.sinh(6*eta)
                     + alpha4*math.cos(8*xi)*math.sinh(8*eta)
                     + alpha5*math.cos(10*xi)*math.sinh(10*eta))

    # S0: 原点緯度の子午線弧長（等角緯度に変換してから計算）
    t0 = math.sinh(
        math.atanh(math.sin(lat0_rad))
        - e * math.atanh(e * math.sin(lat0_rad))
    )
    xi_0 = math.atan(t0)
    S0 = A_bar * (xi_0 + alpha1*math.sin(2*xi_0)
                       + alpha2*math.sin(4*xi_0)
                       + alpha3*math.sin(6*xi_0)
                       + alpha4*math.sin(8*xi_0)
                       + alpha5*math.sin(10*xi_0))

    m0 = 0.9999
    return (X - S0) * m0, Y * m0


def get_zone_for_location(lat: float, lon: float) -> int:
    """
    緯度経度から最適な系番号を推定
    （簡易版：主要な地域のみ対応）
    """
    if lat > 41.5:
        if lon < 141:
            return 11
        elif lon < 143:
            return 12
        else:
            return 13

    if lat > 38 and 139 < lon < 142:
        return 10

    if 34.5 < lat < 38 and 138 < lon < 141:
        return 9

    if 34.5 < lat < 38 and 137 < lon < 139.5:
        return 8

    if 34.5 < lat < 38 and 136 < lon < 138:
        return 7

    if 33.5 < lat < 36.5 and 134.5 < lon < 137:
        return 6

    if 34 < lat < 36.5 and 132 < lon < 135:
        return 5

    if 32.5 < lat < 34.5 and 132 < lon < 135:
        return 4

    if 33.5 < lat < 35 and 130.5 < lon < 133:
        return 3

    if 31 < lat < 34 and 129.5 < lon < 132:
        return 2

    if 31 < lat < 34 and 128 < lon < 130:
        return 1

    if lat < 28:
        if lon < 125:
            return 16
        elif lon < 129:
            return 15
        else:
            return 17

    return 9
