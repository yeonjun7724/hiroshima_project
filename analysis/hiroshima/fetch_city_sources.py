"""Merge/localization plan: city-wide Hiroshima sources for the merged lecture.
병합/현지화 계획: 병합 강의용 히로시마시 전역 데이터.

Task 9 scoped everything to a 1.5km buffer around Koi-ue for the (now
abandoned) slope-case bridge narrative. The merged tutorial needs city-wide
data instead, to mirror geopandas_analysis.ipynb's Seoul-wide ranking/EDA
(all 426 dongs) and 3-4_session.ipynb's bus/subway/bike lookups. This script
re-clips the SAME raw downloads Task 9 already fetched (still cached under
data/hiroshima/_raw/) to all of Hiroshima City (8 wards) instead -- no
re-download needed.
Task 9는 (지금은 폐기된) 사면 사례 브릿지용으로 己斐上 1.5km 반경에 한정했다.
병합 튜토리얼은 geopandas_analysis.ipynb의 서울 전역 순위/EDA(426개 동 전체)와
3-4_session.ipynb의 버스/지하철/따릉이 조회를 대응시키려면 시 전역 데이터가
필요하다. 이 스크립트는 Task 9가 이미 받아둔 원본(data/hiroshima/_raw/에 캐시됨)을
히로시마시 전역(8개 구)으로 재클리핑한다 -- 재다운로드 없음.

Correction from Task 9: the e-Stat download this repo's docs/scripts called
"500m population mesh" is NOT a regular grid -- it's real 小地域 (chōme/town)
boundary polygons with population attached (S_NAME has real neighbourhood
names like 八丁堀, 基町; CITY_NAME has real ward names like 広島市中区). That
makes it the direct Hiroshima equivalent of Seoul's admin-boundary-plus-
registered-population pair (BND_ADM_DONG_PG.shp + 등록인구 CSV combined into
one file), not a separate mesh product. Renamed accordingly here.
Task 9 정정: 이 저장소 문서/스크립트가 "500m 인구격자"라 불렀던 e-Stat 다운로드는
정규 격자가 아니라 실제 小地域(町丁목) 경계 폴리곤에 인구가 붙은 것이다(S_NAME에
八丁堀·基町 같은 실제 동네 이름, CITY_NAME에 広島市中区 같은 실제 구 이름이 있음).
즉 서울의 행정동경계+등록인구(BND_ADM_DONG_PG.shp + 등록인구 CSV를 합친 것과
동급)에 직접 대응한다 — 별도 격자 상품이 아니다. 그에 맞게 이름을 다시 붙였다.
"""
import os

import geopandas as gpd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data", "hiroshima")
RAW_DIR = os.path.join(DATA_DIR, "_raw")

METRIC_CRS = 6670  # JGD2000 / Plane Rectangular CS III


def city_admin_and_population():
    """Hiroshima City's 8 wards, chōme-level, with real population (JINKO)
    and household (SETAI) counts -- the Seoul BND_ADM_DONG_PG.shp + 등록인구
    CSV equivalent, combined into one file already.
    히로시마시 8개 구, 町丁목 단위, 실제 인구(JINKO)·세대수(SETAI) 포함 -- 서울의
    BND_ADM_DONG_PG.shp + 등록인구 CSV 대응본이 이미 한 파일에 합쳐져 있다."""
    gdf = gpd.read_file(os.path.join(RAW_DIR, "mesh_r2ka34", "r2ka34.shp"))
    city = gdf[gdf["CITY_NAME"].astype(str).str.startswith("広島市")].copy()
    city = city.rename(columns={"S_NAME": "region_nm", "CITY_NAME": "ward_nm", "JINKO": "pop", "SETAI": "households"})
    # Every sibling output in this file (and in fetch_sources.py) is normalized
    # to display CRS 4326 before saving; this one was the sole exception,
    # silently saved in the raw source's JGD2011 geographic CRS (EPSG:6668)
    # instead -- fixed to match the project-wide convention.
    # 이 파일(과 fetch_sources.py)의 다른 모든 출력은 저장 전 표시 좌표계(4326)로
    # 정규화하는데, 이 함수만 예외로 원본 소스의 JGD2011 좌표계(EPSG:6668) 그대로
    # 저장되고 있었다 -- 프로젝트 전역 컨벤션에 맞춰 수정.
    city = city.to_crs(4326)
    out = os.path.join(DATA_DIR, "hiroshima_city_admin.gpkg")
    city.to_file(out, driver="GPKG")
    print(f"admin+population: {len(city)} small areas across {city['ward_nm'].nunique()} wards, "
          f"total pop {city['pop'].sum():,}, saved {out}")
    return city


def city_bus_stops(city_boundary_ll):
    """KSJ P11, clipped to the dissolved city boundary instead of a 1.5km buffer.
    KSJ P11, 1.5km 버퍼 대신 병합된 시 경계로 클리핑."""
    gdf = gpd.read_file(os.path.join(RAW_DIR, "P11-10_34_GML", "P11-10_34-jgd-g_BusStop.shp"))
    gdf = gdf.set_crs("EPSG:4612").to_crs(4326)
    sel = gdf[gdf.intersects(city_boundary_ll)].copy()
    out = os.path.join(DATA_DIR, "hiroshima_city_bus_stops.gpkg")
    sel.to_file(out, driver="GPKG")
    print(f"bus stops: {len(sel)} within Hiroshima City, saved {out}")


def city_stations(city_boundary_ll):
    """KSJ N02, same city-wide clip."""
    gdf = gpd.read_file(os.path.join(RAW_DIR, "N02-25_GML", "Shift-JIS", "N02-25_Station.shp")).to_crs(4326)
    sel = gdf[gdf.intersects(city_boundary_ll)].copy()
    out = os.path.join(DATA_DIR, "hiroshima_city_stations.gpkg")
    sel.to_file(out, driver="GPKG")
    print(f"rail/streetcar stations: {len(sel)} within Hiroshima City, saved {out}")


if __name__ == "__main__":
    admin = city_admin_and_population()
    boundary_ll = admin.geometry.union_all()
    city_bus_stops(boundary_ll)
    city_stations(boundary_ll)
