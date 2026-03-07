"""
国土基本図図郭コード計算のCLI
"""

from . import latlon_to_jprcs, latlon_to_zukaku
from .constants import LEVEL_500, LEVEL_5000, LEVEL_50000, LEVEL_1000, LEVEL_2500


def main() -> None:
    """テスト用デモ実行"""
    test_coords = [
        (35.681236, 139.767125, "東京駅", 9),
        (35.658581, 139.745433, "渋谷駅", 9),
        (34.702485, 135.495951, "大阪駅", 6),
        (43.068564, 141.350726, "札幌駅", 12),
    ]

    print("=" * 70)
    print("国土基本図 図郭コード計算ツール")
    print("=" * 70)

    for lat, lon, name, zone in test_coords:
        print(f"\n【{name}】緯度: {lat}, 経度: {lon}, 系: {zone}")

        x, y = latlon_to_jprcs(lat, lon)
        print(f"平面直角座標: X={x:.2f}m, Y={y:.2f}m")
        print("-" * 50)

        for level in [LEVEL_50000, LEVEL_5000, LEVEL_2500, LEVEL_1000, LEVEL_500]:
            info = latlon_to_zukaku(lat, lon, zone, level)
            print(f"レベル{level:5d}: {info.code}")

        print("-" * 50)
        info_500 = latlon_to_zukaku(lat, lon, zone, LEVEL_500)
        print(info_500)


if __name__ == "__main__":
    main()
