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

This script used to read outputs/demo_admin.gpkg / demo_uncovered.gpkg,
written by the now-retired geopandas_analysis.ipynb Seoul lecture 2. Those
exact filenames are now written by hiroshima_tutorial.ipynb's OWN lecture 2,
with Hiroshima data -- reading them here would silently join Seoul grid cells
against Hiroshima geometry (the same failure class practice.ipynb was retired
over; see CLAUDE.md). Fixed to recompute the Seoul district + uncovered
geometry independently instead, the same self-contained pattern
analysis/edge_effect_experiment.py already uses.
이 스크립트는 예전엔 outputs/demo_admin.gpkg / demo_uncovered.gpkg를 읽었는데,
이는 이제 폐기된 geopandas_analysis.ipynb 서울 2강이 쓰던 파일이었다. 이제 정확히
같은 파일명을 hiroshima_tutorial.ipynb의 자체 2강이 히로시마 데이터로 쓴다 --
여기서 그대로 읽으면 서울 격자와 히로시마 지오메트리가 조용히 조인된다
(practice.ipynb를 폐기시킨 것과 같은 실패 유형, CLAUDE.md 참고). 대신
analysis/edge_effect_experiment.py와 같은 자체완결 방식으로 서울 행정동/
비커버 지오메트리를 직접 재계산하도록 고쳤다.
"""
import os
import sys

import geopandas as gpd
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

GRID_SHP = os.path.join(DATA_DIR, "nlsp_021001001.shp")
ADMIN_SHP = os.path.join(DATA_DIR, "BND_ADM_DONG_PG.shp")
BUS_XLSX = os.path.join(DATA_DIR, "서울시버스정류소위치정보(20260108).xlsx")
SUBWAY_CSV = os.path.join(DATA_DIR, "서울교통공사_1_8호선 역사 좌표(위경도) 정보_20250814.csv")

GRID_ID_COL = "gid"
TARGET_CRS = 5179
BUS_BUFFER_M = 300.0
SUB_BUFFER_M = 500.0
RADIUS_M = 1250.0            # 5 min at 15 km/h / 15km/h로 5분 거리
NEIGHBOUR_MARGIN_M = 2000.0  # same edge-effect-corrected stop-selection rule as edge_effect_experiment.py
SEL_GID = "다사545408"        # the cell the lecture picks / 4강이 선택하는 격자


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
    ).to_crs(TARGET_CRS)


def main():
    grid = gpd.read_file(GRID_SHP).to_crs(TARGET_CRS)
    grid["pop"] = pd.to_numeric(grid["val"], errors="coerce").fillna(0.0)
    grid["cell_area"] = grid.geometry.area
    grid[GRID_ID_COL] = grid[GRID_ID_COL].astype(str)

    admin = gpd.read_file(ADMIN_SHP)
    admin["region_id"] = admin["ADM_CD"].astype(str).str.strip()
    admin = admin.to_crs(TARGET_CRS)

    bus = load_points(pd.read_excel(BUS_XLSX), "X좌표", "Y좌표")
    sub = load_points(read_csv_safely(SUBWAY_CSV), "경도", "위도")
    transit = gpd.GeoDataFrame(
        pd.concat([bus[["geometry"]], sub[["geometry"]]], ignore_index=True),
        geometry="geometry", crs=TARGET_CRS,
    )

    # Find which district actually hosts the demo cell, rather than hardcoding
    # one -- keeps this reproducible if SEL_GID or the source shapefile ever
    # changes.
    # 어느 행정동이 데모 격자를 품고 있는지 하드코딩하지 않고 직접 찾는다 --
    # SEL_GID나 원본 shapefile이 바뀌어도 재현 가능하게 유지한다.
    sel_row = grid.loc[grid[GRID_ID_COL] == SEL_GID]
    if sel_row.empty:
        raise SystemExit(f"grid cell {SEL_GID} not found in {GRID_SHP}")
    host = gpd.sjoin(sel_row[["geometry"]], admin[["region_id", "geometry"]], predicate="intersects", how="left")
    rid = host["region_id"].iloc[0]
    district = admin.loc[admin["region_id"] == rid, "geometry"].union_all()
    print(f"demo cell {SEL_GID} sits in district {rid}")

    # Uncovered area = district minus the walk buffer of every nearby stop
    # (edge_effect_experiment.py's corrected "Version B" rule) -- same
    # methodology the retired geopandas_analysis.ipynb lecture 2 used to
    # produce demo_uncovered.gpkg.
    # 비커버 영역 = 행정동 - 인근 모든 정류장의 도보버퍼 (edge_effect_experiment.py의
    # 수정된 "B안" 방식) -- 폐기된 geopandas_analysis.ipynb 2강이 demo_uncovered.gpkg를
    # 만들 때 쓰던 것과 같은 방법론.
    neighbourhood = district.buffer(NEIGHBOUR_MARGIN_M)
    near_bus = bus[bus.geometry.intersects(neighbourhood)]
    near_sub = sub[sub.geometry.intersects(neighbourhood)]
    parts = []
    if len(near_bus):
        parts.append(near_bus.geometry.buffer(BUS_BUFFER_M).union_all())
    if len(near_sub):
        parts.append(near_sub.geometry.buffer(SUB_BUFFER_M).union_all())
    cover = gpd.GeoSeries(parts, crs=TARGET_CRS).union_all() if parts else None
    unc_union = district.difference(cover) if cover else district

    # Candidate cells: within RADIUS_M of any transit stop (lecture-4 rule).
    # 후보 격자: 정류장에서 RADIUS_M 이내 (4강 규칙).
    cent = gpd.GeoDataFrame(
        grid[[GRID_ID_COL, "pop"]].copy(), geometry=grid.geometry.centroid, crs=TARGET_CRS
    )
    nn = gpd.sjoin_nearest(cent, transit[["geometry"]], how="inner", distance_col="dist_m")
    cand_ids = set(nn.loc[nn["dist_m"] <= RADIUS_M, GRID_ID_COL])
    cand = grid[grid[GRID_ID_COL].isin(cand_ids)].copy()

    # --- Bias 1: binary is_uncovered vs fractional overlap -------------------
    # --- 편향 1: 이진 is_uncovered 대 부분 중첩 비율 ------------------------
    cand["unc_frac"] = (
        cand.geometry.intersection(unc_union).area / cand["cell_area"]
    ).clip(0, 1)
    cand["is_uncovered"] = cand.geometry.intersects(unc_union)

    binary_pop = float(cand.loc[cand["is_uncovered"], "pop"].sum())
    frac_pop = float((cand["pop"] * cand["unc_frac"]).sum())
    # Guard against a zero denominator (e.g. no uncovered population in this
    # district) crashing the script instead of reporting nan%, matching the
    # pattern already used in reproduce_ranking.py / edge_effect_experiment.py.
    # 분모가 0인 경우(해당 행정동에 비커버 인구가 없는 경우) 크래시 대신 nan%를
    # 보고하도록 방어한다 -- reproduce_ranking.py / edge_effect_experiment.py와
    # 동일한 패턴.
    overstate_pct = 100 * (binary_pop - frac_pop) / frac_pop if frac_pop > 0 else float("nan")

    print("=" * 74)
    print("BIAS 1 - binary intersects vs fractional overlap")
    print("편향 1 - 이진 intersects 대 부분 중첩 비율")
    print("=" * 74)
    print(f"  candidate cells / 후보 격자      : {len(cand):,}")
    print(f"  flagged uncovered (binary)       : {int(cand['is_uncovered'].sum()):,} cells")
    print(f"  uncovered pop, binary  / 이진    : {binary_pop:>10,.0f}")
    print(f"  uncovered pop, weighted / 가중   : {frac_pop:>10,.0f}")
    print(f"  overstated / 과대계상            : {binary_pop-frac_pop:>10,.0f} ({overstate_pct:+.1f}%)")

    # Cells that only graze the uncovered area but count in full.
    # 비커버 영역에 살짝만 걸쳤는데 전액 계상되는 격자.
    grazing = cand[(cand["is_uncovered"]) & (cand["unc_frac"] < 0.10)]
    print(f"  cells <10% overlapping yet counted 100% / 10%미만 중첩인데 전액 계상: "
          f"{len(grazing):,} cells, {grazing['pop'].sum():,.0f} people")

    # --- Bias 2: full-weight cells inside the 1 250 m circle -----------------
    # --- 편향 2: 1250m 원 안 격자를 전액 계상 -------------------------------
    if SEL_GID not in set(cand[GRID_ID_COL]):
        sel_gid = cand.sort_values("pop", ascending=False).iloc[0][GRID_ID_COL]
        print(f"\n[WARN] {SEL_GID} not a candidate; using {sel_gid} "
              f"/ 후보에 없어 {sel_gid} 사용")
    else:
        sel_gid = SEL_GID

    sel_poly = cand.loc[cand[GRID_ID_COL] == sel_gid, "geometry"].iloc[0]
    circle = sel_poly.centroid.buffer(RADIUS_M)

    # Search the FULL grid for the circle, not just `cand` -- `cand` was built
    # around a different condition (distance to the nearest STOP), so a cell
    # that genuinely overlaps this circle but whose own centroid happens to be
    # >RADIUS_M from any stop would otherwise be silently dropped.
    # `cand`가 아니라 전체 격자에서 원과의 교차를 찾는다 -- `cand`는 다른 조건
    # (가장 가까운 정류장까지 거리)으로 만들어졌으므로, 이 원과 실제로 겹치지만
    # 자기 중심점이 어떤 정류장에서도 RADIUS_M보다 먼 격자는 그렇지 않으면
    # 조용히 누락된다.
    inside = grid[grid.geometry.intersects(circle)].copy()
    inside["in_frac"] = (
        inside.geometry.intersection(circle).area / inside["cell_area"]
    ).clip(0, 1)

    full = float(inside["pop"].sum())
    weighted = float((inside["pop"] * inside["in_frac"]).sum())
    overstate2_pct = 100 * (full - weighted) / weighted if weighted > 0 else float("nan")

    print("\n" + "=" * 74)
    print(f"BIAS 2 - population inside the {RADIUS_M:.0f} m circle around {sel_gid}")
    print(f"편향 2 - {sel_gid} 중심 {RADIUS_M:.0f}m 원 내 인구")
    print("=" * 74)
    print(f"  cells intersecting circle / 원에 걸친 격자 : {len(inside):,}")
    print(f"  population, full weight  / 전액 계상       : {full:>10,.0f}")
    print(f"  population, area-weighted / 면적가중       : {weighted:>10,.0f}")
    print(f"  overstated / 과대계상                      : {full-weighted:>10,.0f} "
          f"({overstate2_pct:+.1f}%)")


if __name__ == "__main__":
    main()
