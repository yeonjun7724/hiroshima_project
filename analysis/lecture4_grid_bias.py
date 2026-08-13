"""Quantify two population-counting biases in the lecture-4 simulation.
4강 시뮬레이션의 두 가지 인구 계상 편향을 정량화한다.

Lecture 4 never clips the grid, so the district-clipping bug does not apply.
It has two different instances of the same underlying mistake - treating a
partial spatial overlap as a whole one:
4강은 격자를 클리핑하지 않으므로 행정동 클리핑 버그는 해당되지 않는다.
대신 동일한 근본 실수 - 부분적인 공간 중첩을 전체로 취급하는 것 - 이
두 군데에서 나타난다:

  (1) is_uncovered = geometry.intersects(unc_union)
      A cell touching the uncovered area by 1 % is counted 100 % uncovered.
      비커버 영역에 1%만 닿은 격자가 100% 비커버로 계상된다.

  (2) gdf_in = cells intersecting the 1 250 m circle, summed at full weight.
      A cell half inside the radius contributes its whole population.
      반경에 절반만 걸친 격자가 인구 전체를 기여한다.
"""
import os
import sys

import geopandas as gpd
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUT_DIR = os.path.join(BASE_DIR, "outputs")

GRID_SHP = os.path.join(DATA_DIR, "nlsp_021001001.shp")
UNCOVERED_GPKG = os.path.join(OUT_DIR, "demo_uncovered.gpkg")
BUS_XLSX = os.path.join(DATA_DIR, "서울시버스정류소위치정보(20260108).xlsx")
SUBWAY_CSV = os.path.join(DATA_DIR, "서울교통공사_1_8호선 역사 좌표(위경도) 정보_20250814.csv")

GRID_ID_COL = "gid"
RADIUS_M = 1250.0        # 5 min at 15 km/h / 15km/h로 5분 거리
SEL_GID = "다사545408"    # the cell the lecture picks / 4강이 선택하는 격자


def read_csv_safely(path):
    """Read a CSV that may be UTF-8 or CP949 encoded.
    UTF-8 또는 CP949로 인코딩된 CSV를 안전하게 읽는다.
    """
    try:
        return pd.read_csv(path, encoding="utf-8")
    except UnicodeDecodeError:
        return pd.read_csv(path, encoding="cp949")


def load_points(df, lon_col, lat_col):
    """Build a metric-CRS point layer from lon/lat columns.
    경도/위도 컬럼으로 미터 좌표계 포인트 레이어를 만든다.
    """
    df = df.copy()
    df[lon_col] = pd.to_numeric(df[lon_col], errors="coerce")
    df[lat_col] = pd.to_numeric(df[lat_col], errors="coerce")
    df = df.dropna(subset=[lon_col, lat_col])
    return gpd.GeoDataFrame(
        df, geometry=gpd.points_from_xy(df[lon_col], df[lat_col]), crs=4326
    ).to_crs(5179)


def main():
    grid = gpd.read_file(GRID_SHP).to_crs(5179)
    grid["pop"] = pd.to_numeric(grid["val"], errors="coerce").fillna(0.0)
    grid["cell_area"] = grid.geometry.area

    unc = gpd.read_file(UNCOVERED_GPKG).to_crs(5179)
    unc_union = unc.geometry.union_all()

    bus = load_points(pd.read_excel(BUS_XLSX), "X좌표", "Y좌표")
    sub = load_points(read_csv_safely(SUBWAY_CSV), "경도", "위도")
    transit = gpd.GeoDataFrame(
        pd.concat([bus[["geometry"]], sub[["geometry"]]], ignore_index=True),
        geometry="geometry", crs=5179,
    )

    # Candidate cells: within RADIUS_M of any transit stop (lecture-4 rule).
    # 후보 격자: 정류장에서 RADIUS_M 이내 (4강 규칙).
    cent = gpd.GeoDataFrame(
        grid[[GRID_ID_COL, "pop"]].copy(), geometry=grid.geometry.centroid, crs=5179
    )
    nn = gpd.sjoin_nearest(cent, transit[["geometry"]], how="inner", distance_col="dist_m")
    cand_ids = set(nn.loc[nn["dist_m"] <= RADIUS_M, GRID_ID_COL].astype(str))
    cand = grid[grid[GRID_ID_COL].astype(str).isin(cand_ids)].copy()

    # --- Bias 1: binary is_uncovered vs fractional overlap -------------------
    # --- 편향 1: 이진 is_uncovered 대 부분 중첩 비율 ------------------------
    cand["unc_frac"] = (
        cand.geometry.intersection(unc_union).area / cand["cell_area"]
    ).clip(0, 1)
    cand["is_uncovered"] = cand.geometry.intersects(unc_union)

    binary_pop = float(cand.loc[cand["is_uncovered"], "pop"].sum())
    frac_pop = float((cand["pop"] * cand["unc_frac"]).sum())

    print("=" * 74)
    print("BIAS 1 - binary intersects vs fractional overlap")
    print("편향 1 - 이진 intersects 대 부분 중첩 비율")
    print("=" * 74)
    print(f"  candidate cells / 후보 격자      : {len(cand):,}")
    print(f"  flagged uncovered (binary)       : {int(cand['is_uncovered'].sum()):,} cells")
    print(f"  uncovered pop, binary  / 이진    : {binary_pop:>10,.0f}")
    print(f"  uncovered pop, weighted / 가중   : {frac_pop:>10,.0f}")
    print(f"  overstated / 과대계상            : {binary_pop-frac_pop:>10,.0f} "
          f"({100*(binary_pop-frac_pop)/frac_pop:+.1f}%)")

    # Cells that only graze the uncovered area but count in full.
    # 비커버 영역에 살짝만 걸쳤는데 전액 계상되는 격자.
    grazing = cand[(cand["is_uncovered"]) & (cand["unc_frac"] < 0.10)]
    print(f"  cells <10% overlapping yet counted 100% / 10%미만 중첩인데 전액 계상: "
          f"{len(grazing):,} cells, {grazing['pop'].sum():,.0f} people")

    # --- Bias 2: full-weight cells inside the 1 250 m circle -----------------
    # --- 편향 2: 1250m 원 안 격자를 전액 계상 -------------------------------
    if SEL_GID not in set(cand[GRID_ID_COL].astype(str)):
        sel_gid = cand.sort_values("pop", ascending=False).iloc[0][GRID_ID_COL]
        print(f"\n[WARN] {SEL_GID} not a candidate; using {sel_gid} "
              f"/ 후보에 없어 {sel_gid} 사용")
    else:
        sel_gid = SEL_GID

    sel_poly = cand.loc[cand[GRID_ID_COL].astype(str) == str(sel_gid), "geometry"].iloc[0]
    circle = sel_poly.centroid.buffer(RADIUS_M)

    inside = cand[cand.geometry.intersects(circle)].copy()
    inside["in_frac"] = (
        inside.geometry.intersection(circle).area / inside["cell_area"]
    ).clip(0, 1)

    full = float(inside["pop"].sum())
    weighted = float((inside["pop"] * inside["in_frac"]).sum())

    print("\n" + "=" * 74)
    print(f"BIAS 2 - population inside the {RADIUS_M:.0f} m circle around {sel_gid}")
    print(f"편향 2 - {sel_gid} 중심 {RADIUS_M:.0f}m 원 내 인구")
    print("=" * 74)
    print(f"  cells intersecting circle / 원에 걸친 격자 : {len(inside):,}")
    print(f"  population, full weight  / 전액 계상       : {full:>10,.0f}")
    print(f"  population, area-weighted / 면적가중       : {weighted:>10,.0f}")
    print(f"  overstated / 과대계상                      : {full-weighted:>10,.0f} "
          f"({100*(full-weighted)/weighted:+.1f}%)")


if __name__ == "__main__":
    main()
