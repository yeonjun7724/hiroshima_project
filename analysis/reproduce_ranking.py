"""Reproduce the lecture-2 vulnerability ranking exactly as written.
2강의 취약도 순위를 원본 그대로 재현한다.

Purpose: establish the true baseline before changing anything. The lecture
scores every Seoul dong on three min-max normalised indicators, equally
weighted, and takes the top 5.
목적: 무엇을 바꾸기 전에 진짜 기준선을 확정한다. 2강은 서울 전체 행정동을
세 개의 min-max 정규화 지표로 균등 가중 채점한 뒤 상위 5개를 취한다.

Critically, `population` here comes from the registered-population CSV, which
covers all 426 dongs - NOT from the 100 m grid, which covers only 39 dongs.
중요한 점: 여기서 `population`은 426개 동을 모두 포함하는 등록인구 CSV에서
오며, 39개 동만 덮는 100m 격자에서 오는 것이 아니다.
"""
import os
import sys

import geopandas as gpd
import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

ADMIN_SHP = os.path.join(DATA_DIR, "BND_ADM_DONG_PG.shp")
BUS_XLSX = os.path.join(DATA_DIR, "서울시버스정류소위치정보(20260108).xlsx")
SUBWAY_CSV = os.path.join(DATA_DIR, "서울교통공사_1_8호선 역사 좌표(위경도) 정보_20250814.csv")
POP_CSV = os.path.join(DATA_DIR, "pop_by_admin.csv")

TARGET_CRS = 5179
MAP_CRS = 4326

BUS_BUFFER_M = 300.0
SUB_BUFFER_M = 500.0

# The five dongs the lecture selected, in the order it lists them.
# 2강이 선정한 5개 동. 노트북에 나열된 순서 그대로.
LECTURE_TOP5 = ["11210540", "11210630", "11110640", "11250630", "11200660"]


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
        df, geometry=gpd.points_from_xy(df[lon_col], df[lat_col]), crs=MAP_CRS
    ).to_crs(TARGET_CRS)


def minmax(s):
    """Scale a series to 0-1; return zeros if the series is constant.
    시리즈를 0~1로 정규화한다. 값이 모두 같으면 0을 반환한다.
    """
    s = s.astype(float)
    if s.max() == s.min():
        return pd.Series(np.zeros(len(s)), index=s.index)
    return (s - s.min()) / (s.max() - s.min())


def main():
    print("Loading layers... / 레이어 로딩 중...")

    adm = gpd.read_file(ADMIN_SHP)
    adm["region_id"] = adm["ADM_CD"].astype(str).str.strip()
    adm["region_nm"] = adm["ADM_NM"].astype(str).str.strip()
    adm = adm[adm["region_id"].str.startswith("11")].to_crs(TARGET_CRS)
    adm = adm[["region_id", "region_nm", "geometry"]].copy()

    bus = load_points(pd.read_excel(BUS_XLSX), "X좌표", "Y좌표")
    sub = load_points(read_csv_safely(SUBWAY_CSV), "경도", "위도")
    print(f"  dongs={len(adm):,}  bus={len(bus):,}  subway={len(sub):,}")

    # Facility counts per dong, as in lecture 1.
    # 1강과 동일하게 행정동별 시설 개수를 집계한다.
    bus_cnt = (gpd.sjoin(bus[["geometry"]], adm, predicate="within")
               .groupby("region_id").size().rename("bus_stop_cnt"))
    sub_cnt = (gpd.sjoin(sub[["geometry"]], adm, predicate="within")
               .groupby("region_id").size().rename("subway_cnt"))

    # Coverage from EVERY stop, then subtract - the correct construction.
    # 모든 정류장으로 커버리지를 만든 뒤 차집합한다 - 올바른 구성.
    print("Building coverage union... / 커버리지 합집합 생성 중...")
    cover = gpd.GeoSeries(
        [bus.geometry.buffer(BUS_BUFFER_M).union_all(),
         sub.geometry.buffer(SUB_BUFFER_M).union_all()],
        crs=TARGET_CRS,
    ).union_all()

    print("Differencing per dong... / 행정동별 차집합 계산 중...")
    adm["admin_area_m2"] = adm.geometry.area
    adm["uncovered_geom"] = adm.geometry.difference(cover)
    adm["uncovered_area_m2"] = gpd.GeoSeries(adm["uncovered_geom"], crs=TARGET_CRS).area
    adm["uncovered_ratio"] = np.where(
        adm["admin_area_m2"] > 0,
        adm["uncovered_area_m2"] / adm["admin_area_m2"],
        0.0,
    )
    adm["uncovered_ratio"] = adm["uncovered_ratio"].fillna(0.0).clip(0, 1)

    # Attach registered population (all 426 dongs) and facility counts.
    # 등록인구(426개 동 전체)와 시설 개수를 결합한다.
    pop = read_csv_safely(POP_CSV)
    pop["region_id"] = (pd.to_numeric(pop["region_id"], errors="coerce")
                        .astype("Int64").astype(str).str.strip())

    df = (adm.drop(columns=["uncovered_geom"])
          .merge(pop[["region_id", "population", "pop_density"]], on="region_id", how="left")
          .merge(bus_cnt, on="region_id", how="left")
          .merge(sub_cnt, on="region_id", how="left"))
    df["bus_stop_cnt"] = df["bus_stop_cnt"].fillna(0)
    df["subway_cnt"] = df["subway_cnt"].fillna(0)

    # The lecture's three equally weighted components.
    # 2강의 세 가지 균등 가중 요소.
    df["pop_norm"] = minmax(df["pop_density"])
    df["unc_norm"] = minmax(df["uncovered_ratio"])
    df["bus_sub_inv_norm"] = 1 - minmax(df["bus_stop_cnt"] + df["subway_cnt"])
    df["vulnerability_score"] = (
        0.33 * df["pop_norm"] + 0.33 * df["unc_norm"] + 0.33 * df["bus_sub_inv_norm"]
    )

    ranked = df.sort_values("vulnerability_score", ascending=False).reset_index(drop=True)
    ranked["rank"] = ranked.index + 1

    print("\n" + "=" * 92)
    print("REPRODUCED TOP 10 / 재현된 상위 10개")
    print("=" * 92)
    cols = ["rank", "region_nm", "region_id", "pop_density", "uncovered_ratio",
            "bus_stop_cnt", "subway_cnt", "vulnerability_score"]
    print(ranked.head(10)[cols].to_string(index=False,
          formatters={"pop_density": "{:,.0f}".format,
                      "uncovered_ratio": "{:.4f}".format,
                      "vulnerability_score": "{:.4f}".format}))

    print("\n" + "=" * 92)
    print("WHERE THE LECTURE'S TOP5 ACTUALLY LAND / 2강 Top5의 실제 위치")
    print("=" * 92)
    sel = ranked[ranked["region_id"].isin(LECTURE_TOP5)]
    print(sel[cols].to_string(index=False,
          formatters={"pop_density": "{:,.0f}".format,
                      "uncovered_ratio": "{:.4f}".format,
                      "vulnerability_score": "{:.4f}".format}))

    # Drop geometry before saving: this is a result table, not a spatial layer.
    # Serialising 426 polygons as WKT bloats the file to ~9.5 MB for no gain.
    # 저장 전 geometry를 제거한다. 이것은 결과 테이블이지 공간 레이어가 아니다.
    # 426개 폴리곤을 WKT로 직렬화하면 아무 이득 없이 파일이 9.5MB로 불어난다.
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ranking_baseline.csv")
    ranked.drop(columns=["geometry"], errors="ignore").to_csv(
        out, index=False, encoding="utf-8-sig"
    )
    print(f"\nSaved / 저장: {out}")


if __name__ == "__main__":
    main()
