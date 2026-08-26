"""Quantify the boundary-clipping bug in buffer-based transit coverage.
버퍼 기반 대중교통 커버리지 분석의 경계 절단 버그를 정량화한다.

Two implementations of the SAME question - "which parts of this district are
not within walking distance of transit?" - give different answers:
동일한 질문("이 행정동에서 대중교통 도보권 밖은 어디인가?")에 대한 두 구현이
서로 다른 답을 낸다:

  Version A (app.py:123)  : keep only stops INSIDE the district, then buffer.
  A안 (app.py:123)        : 행정동 내부 정류장만 남긴 뒤 버퍼를 생성한다.

  Version B (notebook)    : buffer ALL stops, then subtract from the district.
  B안 (노트북)            : 모든 정류장을 버퍼링한 뒤 행정동에서 차집합한다.

Version A is wrong. Coverage is a property of space, not of administrative
membership: a bus stop 10 m outside the boundary still serves people inside it.
A안은 틀렸다. 커버리지는 공간의 속성이지 행정 소속의 속성이 아니다.
경계 밖 10m에 있는 정류장도 경계 안의 주민에게 서비스를 제공한다.

Both versions use the SAME (naive) centroid-in-polygon population rule, so the
measured difference isolates the edge effect alone.
두 버전 모두 동일한 (단순) centroid-in-polygon 인구 판정을 사용하므로,
측정된 차이는 오직 edge effect만을 분리해서 보여준다.
"""
import os
import sys

import geopandas as gpd
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

ADMIN_SHP = os.path.join(DATA_DIR, "BND_ADM_DONG_PG.shp")
BUS_XLSX = os.path.join(DATA_DIR, "서울시버스정류소위치정보(20260108).xlsx")
SUBWAY_CSV = os.path.join(DATA_DIR, "서울교통공사_1_8호선 역사 좌표(위경도) 정보_20250814.csv")
GRID_SHP = os.path.join(DATA_DIR, "nlsp_021001001.shp")

TARGET_IDS = {"11210630": "남현동", "11210540": "청림동"}

TARGET_CRS = 5179   # metric CRS for distance work / 거리 연산용 미터 좌표계
MAP_CRS = 4326      # lon/lat of the source files / 원본 파일의 경위도 좌표계

BUS_BUFFER_M = 300.0   # walkable radius for a bus stop / 버스정류장 도보 반경
SUB_BUFFER_M = 500.0   # walkable radius for a station  / 지하철역 도보 반경

# Only stops within this distance of the district can possibly cover it.
# 이 거리 안의 정류장만이 해당 행정동을 커버할 수 있다.
NEIGHBOUR_MARGIN_M = 2000.0


def read_csv_safely(path):
    """Read a CSV that may be UTF-8 or CP949 encoded.
    UTF-8 또는 CP949로 인코딩된 CSV를 안전하게 읽는다.
    """
    try:
        return pd.read_csv(path, encoding="utf-8")
    except UnicodeDecodeError:
        return pd.read_csv(path, encoding="cp949")


def load_points(df, lon_col, lat_col):
    """Build a metric-CRS GeoDataFrame from lon/lat columns.
    경도/위도 컬럼으로부터 미터 좌표계 GeoDataFrame을 생성한다.
    """
    df = df.copy()
    df[lon_col] = pd.to_numeric(df[lon_col], errors="coerce")
    df[lat_col] = pd.to_numeric(df[lat_col], errors="coerce")
    df = df.dropna(subset=[lon_col, lat_col])
    return gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df[lon_col], df[lat_col]),
        crs=MAP_CRS,
    ).to_crs(TARGET_CRS)


def coverage_union(bus_pts, sub_pts):
    """Union the walk-radius buffers of every supplied stop.
    주어진 모든 정류장의 도보 반경 버퍼를 합집합으로 만든다.
    """
    parts = []
    if len(bus_pts):
        parts.append(bus_pts.geometry.buffer(BUS_BUFFER_M).union_all())
    if len(sub_pts):
        parts.append(sub_pts.geometry.buffer(SUB_BUFFER_M).union_all())
    if not parts:
        return None
    return gpd.GeoSeries(parts, crs=TARGET_CRS).union_all()


def uncovered_population(grid, uncovered_geom):
    """Sum grid population whose centroid falls in the uncovered area.
    중심점이 비커버 영역에 속하는 격자의 인구를 합산한다.

    NOTE: this is the naive rule used by the original code. It is held constant
    across both versions on purpose, so it cancels out of the comparison.
    참고: 원본 코드가 쓰는 단순 판정 방식이다. 두 버전에 동일하게 적용해
    비교 과정에서 상쇄되도록 의도한 것이다.
    """
    if uncovered_geom is None or uncovered_geom.is_empty:
        return 0.0
    mask = grid["centroid_m"].within(uncovered_geom)
    return float(grid.loc[mask, "pop"].sum())


def main():
    print("Loading source layers... / 원본 레이어 로딩 중...")

    gdf_admin = gpd.read_file(ADMIN_SHP)
    gdf_admin["region_id"] = gdf_admin["ADM_CD"].astype(str).str.strip()
    gdf_admin = gdf_admin.to_crs(TARGET_CRS)

    gdf_bus = load_points(pd.read_excel(BUS_XLSX), "X좌표", "Y좌표")
    gdf_sub = load_points(read_csv_safely(SUBWAY_CSV), "경도", "위도")

    gdf_grid = gpd.read_file(GRID_SHP).to_crs(TARGET_CRS)
    gdf_grid["pop"] = pd.to_numeric(gdf_grid["val"], errors="coerce").fillna(0.0)

    print(f"  admin={len(gdf_admin):,}  bus={len(gdf_bus):,}  "
          f"subway={len(gdf_sub):,}  grid={len(gdf_grid):,}\n")

    rows = []

    for rid, name in TARGET_IDS.items():
        sel = gdf_admin[gdf_admin["region_id"] == rid]
        if sel.empty:
            print(f"[WARN] district {rid} not found / 행정동 {rid} 없음")
            continue

        district = sel.geometry.union_all()
        neighbourhood = district.buffer(NEIGHBOUR_MARGIN_M)

        # Grid cells of this district, with the population rule held constant.
        # 해당 행정동의 격자. 인구 판정 방식은 두 버전에 동일하게 적용한다.
        grid = gpd.clip(
            gdf_grid[gdf_grid.geometry.intersects(district)], sel
        )[["gid", "pop", "geometry"]].copy()
        grid["centroid_m"] = grid.geometry.centroid

        # --- Version A: stops inside the district only (the bug) -------------
        # --- A안: 행정동 내부 정류장만 사용 (버그) --------------------------
        bus_in = gdf_bus[gdf_bus.geometry.within(district)]
        sub_in = gdf_sub[gdf_sub.geometry.within(district)]
        cover_a = coverage_union(bus_in, sub_in)
        uncov_a = district.difference(cover_a) if cover_a else district

        # --- Version B: every nearby stop, regardless of district ------------
        # --- B안: 행정동과 무관하게 인근의 모든 정류장 사용 -----------------
        bus_near = gdf_bus[gdf_bus.geometry.intersects(neighbourhood)]
        sub_near = gdf_sub[gdf_sub.geometry.intersects(neighbourhood)]
        cover_b = coverage_union(bus_near, sub_near)
        uncov_b = district.difference(cover_b) if cover_b else district

        rows.append(dict(
            region=name,
            region_id=rid,
            district_km2=district.area / 1e6,
            total_pop=float(grid["pop"].sum()),
            stops_a=len(bus_in) + len(sub_in),
            stops_b=len(bus_near) + len(sub_near),
            uncov_km2_a=uncov_a.area / 1e6,
            uncov_km2_b=uncov_b.area / 1e6,
            uncov_pop_a=uncovered_population(grid, uncov_a),
            uncov_pop_b=uncovered_population(grid, uncov_b),
        ))

    df = pd.DataFrame(rows)
    df["area_overstated_km2"] = df["uncov_km2_a"] - df["uncov_km2_b"]
    df["pop_overstated"] = df["uncov_pop_a"] - df["uncov_pop_b"]
    df["pop_overstated_pct"] = 100 * df["pop_overstated"] / df["uncov_pop_b"].replace(0, float("nan"))

    print("=" * 78)
    print("EDGE EFFECT: version A (buggy) vs version B (correct)")
    print("EDGE EFFECT: A안(버그) 대 B안(정상)")
    print("=" * 78)

    for _, r in df.iterrows():
        print(f"\n[{r['region']}] ({r['region_id']})  "
              f"{r['district_km2']:.2f} km², pop {r['total_pop']:,.0f}")
        print(f"  stops used      A={r['stops_a']:>4}      B={r['stops_b']:>4}"
              f"      (+{r['stops_b']-r['stops_a']} ignored by A / A안이 무시한 정류장)")
        print(f"  uncovered area  A={r['uncov_km2_a']:.4f}  B={r['uncov_km2_b']:.4f} km²"
              f"   overstated by {r['area_overstated_km2']:.4f} km²")
        print(f"  uncovered pop   A={r['uncov_pop_a']:>9,.0f}  B={r['uncov_pop_b']:>9,.0f}"
              f"   overstated by {r['pop_overstated']:,.0f} "
              f"({r['pop_overstated_pct']:.1f}%)")

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "edge_effect_results.csv")
    df.to_csv(out, index=False, encoding="utf-8-sig")
    print(f"\nSaved / 저장: {out}")


if __name__ == "__main__":
    main()
