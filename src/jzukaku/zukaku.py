"""
国土基本図 図郭コード計算

平面直角座標系を基準とした図郭コード体系。
標準地域メッシュ（緯度経度ベース）とは異なる。

図郭コード構成:
- レベル50000: 系番号(2桁) + 区画名(2文字) = 4桁 (30km×40km)
- レベル5000:  上記 + 図葉番号(2桁) = 6桁 (3km×4km)
- レベル2500:  上記 + 分割番号(1桁:1-4) = 7桁 (1.5km×2km)
- レベル1000:  レベル5000 + 分割番号(2桁:数字+英字) = 8桁 (600m×800m)
- レベル500:   レベル5000 + 分割番号(2桁:00-99) = 8桁 (300m×400m)

参考: https://club.informatix.co.jp/?p=1293
"""

import math
from dataclasses import dataclass

from .constants import SUPPORTED_LEVELS
from .jprcs import get_zone_for_location, latlon_to_jprcs


@dataclass
class ZukakuInfo:
    """図郭情報"""

    code: str
    level: int
    zone: int
    x_min: float  # 南端X座標
    x_max: float  # 北端X座標
    y_min: float  # 西端Y座標
    y_max: float  # 東端Y座標

    def __str__(self) -> str:
        return (
            f"図郭コード: {self.code}\n"
            f"レベル: {self.level}\n"
            f"系番号: {self.zone}\n"
            f"X範囲: {self.x_min:.1f} ~ {self.x_max:.1f} m\n"
            f"Y範囲: {self.y_min:.1f} ~ {self.y_max:.1f} m"
        )


def xy_to_zukaku(
    x: float, y: float, zone: int, level: int = 500
) -> ZukakuInfo:
    """
    平面直角座標から図郭コードを計算

    Parameters:
        x: X座標（南北方向、北が正）メートル
        y: Y座標（東西方向、東が正）メートル
        zone: 系番号（1-19）
        level: 地図情報レベル（50000, 5000, 2500, 1000, 500）

    Returns:
        ZukakuInfo: 図郭情報
    """
    if level not in SUPPORTED_LEVELS:
        raise ValueError(
            f"未対応のレベル: {level}. 対応: {SUPPORTED_LEVELS}"
        )

    # 原点から南北それぞれ300km、東西それぞれ160km
    # X: -300,000 ~ +300,000 (600km), Y: -160,000 ~ +160,000 (320km)
    x_offset = x + 300000
    y_offset = y + 160000

    tile_h_50000 = 30000
    tile_w_50000 = 40000

    row_50000 = int((600000 - x_offset) / tile_h_50000)
    col_50000 = int(y_offset / tile_w_50000)

    row_50000 = max(0, min(19, row_50000))
    col_50000 = max(0, min(7, col_50000))

    alpha_row = chr(ord("A") + row_50000)
    alpha_col = chr(ord("A") + col_50000)

    code_50000 = f"{zone:02d}{alpha_row}{alpha_col}"

    x_max_50000 = 300000 - row_50000 * tile_h_50000
    x_min_50000 = x_max_50000 - tile_h_50000
    y_min_50000 = -160000 + col_50000 * tile_w_50000
    y_max_50000 = y_min_50000 + tile_w_50000

    if level == 50000:
        return ZukakuInfo(
            code_50000, level, zone,
            x_min_50000, x_max_50000, y_min_50000, y_max_50000
        )

    tile_h_5000 = 3000
    tile_w_5000 = 4000

    x_in_50000 = x - x_min_50000
    y_in_50000 = y - y_min_50000

    row_5000 = int((tile_h_50000 - x_in_50000) / tile_h_5000)
    col_5000 = int(y_in_50000 / tile_w_5000)

    row_5000 = max(0, min(9, row_5000))
    col_5000 = max(0, min(9, col_5000))

    sheet_num = row_5000 * 10 + col_5000
    code_5000 = f"{code_50000}{sheet_num:02d}"

    x_max_5000 = x_max_50000 - row_5000 * tile_h_5000
    x_min_5000 = x_max_5000 - tile_h_5000
    y_min_5000 = y_min_50000 + col_5000 * tile_w_5000
    y_max_5000 = y_min_5000 + tile_w_5000

    if level == 5000:
        return ZukakuInfo(
            code_5000, level, zone,
            x_min_5000, x_max_5000, y_min_5000, y_max_5000
        )

    tile_h_2500 = 1500
    tile_w_2500 = 2000

    x_in_5000 = x - x_min_5000
    y_in_5000 = y - y_min_5000

    row_2500 = 0 if x_in_5000 >= tile_h_2500 else 1
    col_2500 = 0 if y_in_5000 < tile_w_2500 else 1

    div_2500 = row_2500 * 2 + col_2500 + 1
    code_2500 = f"{code_5000}{div_2500}"

    x_max_2500 = x_max_5000 - row_2500 * tile_h_2500
    x_min_2500 = x_max_2500 - tile_h_2500
    y_min_2500 = y_min_5000 + col_2500 * tile_w_2500
    y_max_2500 = y_min_2500 + tile_w_2500

    if level == 2500:
        return ZukakuInfo(
            code_2500, level, zone,
            x_min_2500, x_max_2500, y_min_2500, y_max_2500
        )

    tile_h_1000 = 600
    tile_w_1000 = 800

    row_1000 = int((tile_h_5000 - x_in_5000) / tile_h_1000)
    col_1000 = int(y_in_5000 / tile_w_1000)

    row_1000 = max(0, min(4, row_1000))
    col_1000 = max(0, min(4, col_1000))

    div_1000 = f"{row_1000}{chr(ord('A') + col_1000)}"
    code_1000 = f"{code_5000}{div_1000}"

    x_max_1000 = x_max_5000 - row_1000 * tile_h_1000
    x_min_1000 = x_max_1000 - tile_h_1000
    y_min_1000 = y_min_5000 + col_1000 * tile_w_1000
    y_max_1000 = y_min_1000 + tile_w_1000

    if level == 1000:
        return ZukakuInfo(
            code_1000, level, zone,
            x_min_1000, x_max_1000, y_min_1000, y_max_1000
        )

    tile_h_500 = 300
    tile_w_500 = 400

    row_500 = int((tile_h_5000 - x_in_5000) / tile_h_500)
    col_500 = int(y_in_5000 / tile_w_500)

    row_500 = max(0, min(9, row_500))
    col_500 = max(0, min(9, col_500))

    div_500 = row_500 * 10 + col_500
    code_500 = f"{code_5000}{div_500:02d}"

    x_max_500 = x_max_5000 - row_500 * tile_h_500
    x_min_500 = x_max_500 - tile_h_500
    y_min_500 = y_min_5000 + col_500 * tile_w_500
    y_max_500 = y_min_500 + tile_w_500

    return ZukakuInfo(
        code_500, level, zone,
        x_min_500, x_max_500, y_min_500, y_max_500
    )


def latlon_to_zukaku(
    lat: float,
    lon: float,
    zone: int | None = None,
    level: int = 500,
) -> ZukakuInfo:
    """
    緯度経度から図郭コードを計算

    Parameters:
        lat: 緯度（度）
        lon: 経度（度）
        zone: 系番号（1-19）。Noneの場合は自動推定
        level: 地図情報レベル（50000, 5000, 2500, 1000, 500）

    Returns:
        ZukakuInfo: 図郭情報
    """
    if zone is None:
        zone = get_zone_for_location(lat, lon)

    x, y = latlon_to_jprcs(lat, lon, zone)
    return xy_to_zukaku(x, y, zone, level)


def bbox_to_zukaku(
    bounds: list[float] | tuple[float, float, float, float],
    zone: int | None = None,
    level: int = 500,
) -> list[str]:
    """
    バウンディングボックス（緯度経度）と重なる図郭コードの一覧を返す。

    Parameters:
        bounds: [lat_min, lon_min, lat_max, lon_max] の4要素
        zone: 系番号（1-19）。Noneの場合はバウンディングボックス中心から自動推定
        level: 地図情報レベル（50000, 5000, 2500, 1000, 500）

    Returns:
        図郭コードのリスト（重複なし、ソート済み）
    """
    if level not in SUPPORTED_LEVELS:
        raise ValueError(
            f"未対応のレベル: {level}. 対応: {SUPPORTED_LEVELS}"
        )

    lat_min, lon_min, lat_max, lon_max = bounds[0], bounds[1], bounds[2], bounds[3]
    if zone is None:
        zone = get_zone_for_location(
            (lat_min + lat_max) / 2, (lon_min + lon_max) / 2
        )

    # 4隅を平面直角座標に変換し、XYの範囲を取得
    corners = [
        (lat_min, lon_min),
        (lat_min, lon_max),
        (lat_max, lon_min),
        (lat_max, lon_max),
    ]
    xs, ys = [], []
    for lat, lon in corners:
        x, y = latlon_to_jprcs(lat, lon, zone)
        xs.append(x)
        ys.append(y)
    x_lo, x_hi = min(xs), max(xs)
    y_lo, y_hi = min(ys), max(ys)

    # レベル50000のタイル範囲
    tile_h_50000 = 30000
    tile_w_50000 = 40000
    r50_min = max(0, math.ceil((300000 - x_hi) / tile_h_50000) - 1)
    r50_max = min(19, math.floor((300000 - x_lo) / tile_h_50000))
    c50_min = max(0, math.ceil((y_lo + 160000) / tile_w_50000) - 1)
    c50_max = min(7, math.floor((y_hi + 160000) / tile_w_50000))

    codes: list[str] = []
    tile_h_5000, tile_w_5000 = 3000, 4000

    for r50 in range(r50_min, r50_max + 1):
        for c50 in range(c50_min, c50_max + 1):
            alpha_row = chr(ord("A") + r50)
            alpha_col = chr(ord("A") + c50)
            code_50000 = f"{zone:02d}{alpha_row}{alpha_col}"
            x_max_50000 = 300000 - r50 * tile_h_50000
            x_min_50000 = x_max_50000 - tile_h_50000
            y_min_50000 = -160000 + c50 * tile_w_50000
            y_max_50000 = y_min_50000 + tile_w_50000

            if level == 50000:
                codes.append(code_50000)
                continue

            # レベル5000のタイル範囲（この50000区画内）
            x_lo_50 = max(x_lo, x_min_50000)
            x_hi_50 = min(x_hi, x_max_50000)
            y_lo_50 = max(y_lo, y_min_50000)
            y_hi_50 = min(y_hi, y_max_50000)
            r5_min = max(0, math.ceil((x_max_50000 - x_hi_50) / tile_h_5000) - 1)
            r5_max = min(9, math.floor((x_max_50000 - x_lo_50) / tile_h_5000))
            c5_min = max(0, math.ceil((y_lo_50 - y_min_50000) / tile_w_5000) - 1)
            c5_max = min(9, math.floor((y_hi_50 - y_min_50000) / tile_w_5000))

            for r5 in range(r5_min, r5_max + 1):
                for c5 in range(c5_min, c5_max + 1):
                    sheet_num = r5 * 10 + c5
                    code_5000 = f"{code_50000}{sheet_num:02d}"
                    x_max_5000 = x_max_50000 - r5 * tile_h_5000
                    x_min_5000 = x_max_5000 - tile_h_5000
                    y_min_5000 = y_min_50000 + c5 * tile_w_5000
                    y_max_5000 = y_min_5000 + tile_w_5000

                    if level == 5000:
                        codes.append(code_5000)
                        continue

                    # レベル2500（2x2分割）
                    tile_h_2500, tile_w_2500 = 1500, 2000
                    x_lo_5 = max(x_lo, x_min_5000)
                    x_hi_5 = min(x_hi, x_max_5000)
                    y_lo_5 = max(y_lo, y_min_5000)
                    y_hi_5 = min(y_hi, y_max_5000)
                    r25_min = max(0, math.ceil((x_max_5000 - x_hi_5) / tile_h_2500) - 1)
                    r25_max = min(1, math.floor((x_max_5000 - x_lo_5) / tile_h_2500))
                    c25_min = max(0, math.ceil((y_lo_5 - y_min_5000) / tile_w_2500) - 1)
                    c25_max = min(1, math.floor((y_hi_5 - y_min_5000) / tile_w_2500))

                    for r25 in range(r25_min, r25_max + 1):
                        for c25 in range(c25_min, c25_max + 1):
                            div_2500 = r25 * 2 + c25 + 1
                            code_2500 = f"{code_5000}{div_2500}"
                            if level == 2500:
                                codes.append(code_2500)
                                continue

                            # レベル1000
                            tile_h_1000, tile_w_1000 = 600, 800
                            x_in_5000_lo = x_lo_5 - x_min_5000
                            x_in_5000_hi = x_hi_5 - x_min_5000
                            y_in_5000_lo = y_lo_5 - y_min_5000
                            y_in_5000_hi = y_hi_5 - y_min_5000
                            r1_min = max(0, math.ceil((tile_h_5000 - x_in_5000_hi) / tile_h_1000) - 1)
                            r1_max = min(4, math.floor((tile_h_5000 - x_in_5000_lo) / tile_h_1000))
                            c1_min = max(0, math.ceil(y_in_5000_lo / tile_w_1000) - 1)
                            c1_max = min(4, math.floor(y_in_5000_hi / tile_w_1000))

                            for r1 in range(r1_min, r1_max + 1):
                                for c1 in range(c1_min, c1_max + 1):
                                    div_1000 = f"{r1}{chr(ord('A') + c1)}"
                                    code_1000 = f"{code_5000}{div_1000}"
                                    if level == 1000:
                                        codes.append(code_1000)
                                        continue

                                    # レベル500
                                    tile_h_500, tile_w_500 = 300, 400
                                    r05_min = max(0, math.ceil((tile_h_5000 - x_in_5000_hi) / tile_h_500) - 1)
                                    r05_max = min(9, math.floor((tile_h_5000 - x_in_5000_lo) / tile_h_500))
                                    c05_min = max(0, math.ceil(y_in_5000_lo / tile_w_500) - 1)
                                    c05_max = min(9, math.floor(y_in_5000_hi / tile_w_500))

                                    for r05 in range(r05_min, r05_max + 1):
                                        for c05 in range(c05_min, c05_max + 1):
                                            codes.append(f"{code_5000}{r05 * 10 + c05:02d}")

    return sorted(set(codes))
