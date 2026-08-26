"""Task 9 data acquisition: Koi-ue (己斐上) slope case, Hiroshima.
Task 9 데이터 수집: 히로시마 己斐上(코이우에) 사면 사례.

Downloads four public sources, clips each to a 1.5 km radius around
Hiroden Nishi-Hiroshima (Koi) station -- the flat-land transit anchor at the
foot of the hill -- and writes the small extracts to data/hiroshima/.
Raw downloads (prefecture/nationwide files, tens of MB) are NOT committed;
only the clipped outputs are. Rerun this script to regenerate them.
공공데이터 4종을 내려받아 广電西広島(己斐)駅(언덕 아래 평지 교통 거점) 반경 1.5km로
클리핑해 data/hiroshima/에 저장한다. 원본(현/전국 단위, 수십MB)은 커밋하지 않고
클리핑된 결과만 커밋한다. 재현하려면 이 스크립트를 다시 실행하면 된다.

Sources / 출처:
  - Bus stops (P11), 国土数値情報: https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-P11.html
  - Railway/streetcar stations (N02), 国土数値情報: https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-N02-2025.html
  - 500m population mesh (2020 census, 4次メッシュ), e-Stat 統計GIS: https://www.e-stat.go.jp/gis/statmap-search?type=1
  - 5m DEM (DEM5A, airborne laser), 国土地理院 elevation tiles: https://maps.gsi.go.jp/development/demtile.html

Why this area / 이 지역을 고른 이유:
  Koi-ue sits on the old Koi-jo/Chausu-yama castle hill -- real relief next to
  a real transit anchor, and (unlike Yagi in Asa-Minami-ku) it carries no
  disaster history, so it's usable as a plain "does the bus reach the hill"
  demo without editorializing on the 2014 landslide deaths.
  己斐上은 옛 己斐城/茶臼山 성터 언덕으로, 실제 교통 거점 옆에 실제 고저차가 있다.
  安佐南区 八木와 달리 재해 이력이 없어 "버스가 언덕까지 닿는가"를 순수한 접근성
  데모로 다룰 수 있다.
"""
import os
import zipfile

import geopandas as gpd
import numpy as np
import requests
from PIL import Image
from shapely.geometry import Point

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data", "hiroshima")
RAW_DIR = os.path.join(DATA_DIR, "_raw")  # gitignored; regenerable
os.makedirs(RAW_DIR, exist_ok=True)

UA = {"User-Agent": "Mozilla/5.0 (compatible; gis_session-research/1.0)"}

# Koi (己斐) station -- transit anchor at the foot of the hill.
# 己斐역 -- 언덕 아래 교통 거점.
CENTER_LON, CENTER_LAT = 132.42777883, 34.39675456
RADIUS_M = 1500

# JGD2000 Plane Rectangular CS III -- covers Hiroshima pref, metres.
# 히로시마현을 포함하는 평면직각좌표계 3계 (미터 단위).
METRIC_CRS = 6670


def _buffer():
    center = gpd.GeoSeries([Point(CENTER_LON, CENTER_LAT)], crs=4326).to_crs(METRIC_CRS).iloc[0]
    return center.buffer(RADIUS_M)


def _download(url, path):
    if os.path.exists(path):
        return
    r = requests.get(url, headers=UA, timeout=60)
    r.raise_for_status()
    with open(path, "wb") as f:
        f.write(r.content)


def fetch_bus_stops():
    """KSJ P11, Hiroshima prefecture (code 34). ~0.6MB, FY2010 vintage --
    the only version the government has published for this dataset.
    KSJ P11, 히로시마현(코드 34). ~0.6MB, 2010년(평성22년)판 -- 이 데이터셋은
    정부가 그 이후 갱신판을 낸 적이 없다."""
    zip_path = os.path.join(RAW_DIR, "P11-10_34_GML.zip")
    _download("https://nlftp.mlit.go.jp/ksj/gml/data/P11/P11-10/P11-10_34_GML.zip", zip_path)

    extract_dir = os.path.join(RAW_DIR, "P11-10_34_GML")
    if not os.path.exists(extract_dir):
        with zipfile.ZipFile(zip_path) as z:
            z.extractall(RAW_DIR)

    gdf = gpd.read_file(os.path.join(extract_dir, "P11-10_34-jgd-g_BusStop.shp"))
    gdf = gdf.set_crs("EPSG:4612").to_crs(METRIC_CRS)  # JGD2000 geographic, per KSJ spec
    sel = gdf[gdf.intersects(_buffer())].copy()
    sel.to_crs(4326).to_file(os.path.join(DATA_DIR, "koi_bus_stops.gpkg"), driver="GPKG")
    print(f"bus stops: {len(sel)} within {RADIUS_M}m")


def fetch_stations():
    """KSJ N02, latest FY (nationwide, no per-prefecture split) -- clip to
    the buffer immediately, don't keep the national file.
    KSJ N02, 최신 연도(전국 단일 파일, 현별 분할 없음) -- 받은 즉시 반경으로
    클리핑하고 전국 파일은 보관하지 않는다."""
    zip_path = os.path.join(RAW_DIR, "N02-25_GML.zip")
    _download("https://nlftp.mlit.go.jp/ksj/gml/data/N02/N02-25/N02-25_GML.zip", zip_path)

    extract_dir = os.path.join(RAW_DIR, "N02-25_GML", "Shift-JIS")
    if not os.path.exists(extract_dir):
        with zipfile.ZipFile(zip_path) as z:
            names = [n for n in z.namelist() if "Shift-JIS/N02-25_Station." in n]
            z.extractall(RAW_DIR, members=names)

    gdf = gpd.read_file(os.path.join(extract_dir, "N02-25_Station.shp")).to_crs(METRIC_CRS)
    sel = gdf[gdf.intersects(_buffer())].copy()
    sel.to_crs(4326).to_file(os.path.join(DATA_DIR, "koi_stations.gpkg"), driver="GPKG")
    print(f"rail/streetcar stations: {len(sel)} within {RADIUS_M}m")


def fetch_population_mesh():
    """e-Stat 500m mesh (4th mesh), 2020 census (r2ka = Reiwa-2 kokusei
    chosa), Hiroshima prefecture. Split boundary cells carry an 11-digit
    KEY_CODE instead of 9; both are real, non-masked JINKO (population)
    counts -- verified no -9999 sentinel rows in this extract.
    e-Stat 500m 격자(4次メッシュ), 2020년 국세조사, 히로시마현. 행정경계에 걸친
    셀은 9자리 대신 11자리 KEY_CODE를 갖는다. 이 클리핑 범위 안에는 -9999
    마스킹(비공개) 값이 없음을 확인함."""
    zip_path = os.path.join(RAW_DIR, "A002005212020DDSWC34-JGD2011.zip")
    url = (
        "https://www.e-stat.go.jp/gis/statmap-search/data"
        "?dlserveyId=A002005212020&code=34&coordSys=1&format=shape"
        "&downloadType=5&datum=2011"
    )
    _download(url, zip_path)

    extract_dir = os.path.join(RAW_DIR, "mesh_r2ka34")
    if not os.path.exists(extract_dir):
        with zipfile.ZipFile(zip_path) as z:
            z.extractall(extract_dir)

    gdf = gpd.read_file(os.path.join(extract_dir, "r2ka34.shp")).to_crs(METRIC_CRS)
    sel = gdf[gdf.intersects(_buffer())].copy()
    sel.to_crs(4326).to_file(os.path.join(DATA_DIR, "koi_pop_mesh500.gpkg"), driver="GPKG")
    print(f"500m mesh cells: {len(sel)} within {RADIUS_M}m, total pop {sel['JINKO'].sum():,}")


def _lonlat_to_tile(lon, lat, z):
    n = 2**z
    x = int((lon + 180.0) / 360.0 * n)
    lat_rad = np.radians(lat)
    y = int((1.0 - np.log(np.tan(lat_rad) + 1 / np.cos(lat_rad)) / np.pi) / 2.0 * n)
    return x, y


def _tile_to_lonlat(x, y, z):
    n = 2**z
    lon = x / n * 360 - 180
    lat = np.degrees(np.arctan(np.sinh(np.pi * (1 - 2 * y / n))))
    return lon, lat


def fetch_dem(zoom=15):
    """GSI DEM5A elevation tiles (5m mesh, airborne laser), no account
    needed. Falls back silently to 10m DEM10B (dem_png, zoom 14) per
    missing tile -- 5A coverage is airborne-survey-dependent and not
    guaranteed everywhere, though it is present for this area.
    国土地理院 DEM5A 표고 타일(5m, 항공레이저), 계정 불필요. 타일별로 5A가
    없으면 10m DEM10B(dem_png, zoom 14)로 자동 대체 -- 이 지역은 5A가
    있음을 확인했지만 다른 지역에서는 보장되지 않는다."""
    out_dir = os.path.join(DATA_DIR, "dem")
    os.makedirs(out_dir, exist_ok=True)

    # tobler_slope_correction.py's build_graph() downloads the walk network
    # with RADIUS_M + 300m of padding, not RADIUS_M -- match that here so
    # every network node's elevation comes from a real tile instead of being
    # silently clamped to the mosaic edge for nodes in that outer 300m ring.
    # tobler_slope_correction.py의 build_graph()는 도보 네트워크를 RADIUS_M이
    # 아니라 RADIUS_M + 300m 여유로 받는다 -- 여기서도 맞춰서, 바깥쪽 300m 링에
    # 있는 노드의 표고가 모자이크 가장자리로 조용히 클램핑되지 않고 실제 타일에서
    # 나오게 한다.
    dem_radius_m = RADIUS_M + 300
    d_lat = dem_radius_m / 111_320
    d_lon = dem_radius_m / (111_320 * np.cos(np.radians(CENTER_LAT)))
    x1, y1 = _lonlat_to_tile(CENTER_LON - d_lon, CENTER_LAT + d_lat, zoom)
    x2, y2 = _lonlat_to_tile(CENTER_LON + d_lon, CENTER_LAT - d_lat, zoom)

    ok, fallback = 0, 0
    for x in range(x1, x2 + 1):
        for y in range(y1, y2 + 1):
            path = os.path.join(out_dir, f"{x}_{y}.png")
            if os.path.exists(path):
                ok += 1
                continue
            url = f"https://cyberjapandata.gsi.go.jp/xyz/dem5a_png/{zoom}/{x}/{y}.png"
            r = requests.get(url, headers=UA, timeout=15)
            if r.status_code == 200:
                with open(path, "wb") as f:
                    f.write(r.content)
                ok += 1
            else:
                fallback += 1
                fb_zoom = 14
                tile_lon, tile_lat = _tile_to_lonlat(x + 0.5, y + 0.5, zoom)
                fbx, fby = _lonlat_to_tile(tile_lon, tile_lat, fb_zoom)
                fb_url = f"https://cyberjapandata.gsi.go.jp/xyz/dem_png/{fb_zoom}/{fbx}/{fby}.png"
                r = requests.get(fb_url, headers=UA, timeout=15)
                if r.status_code == 200:
                    with open(os.path.join(out_dir, f"fallback_{fb_zoom}_{fbx}_{fby}.png"), "wb") as f:
                        f.write(r.content)
    print(f"DEM tiles: {ok} at z{zoom} (5m), {fallback} fell back to 10m")


def decode_elevation(png_path):
    """RGB -> metres, per GSI's demtile spec. NaN where nodata (128,0,0).
    GSI 표고타일 사양에 따라 RGB를 미터로 변환. nodata(128,0,0)는 NaN."""
    img = np.array(Image.open(png_path).convert("RGB")).astype(np.int64)
    r, g, b = img[..., 0], img[..., 1], img[..., 2]
    x = r * 65536 + g * 256 + b
    h = np.where(x < 8_388_608, x * 0.01, np.where(x == 8_388_608, np.nan, (x - 16_777_216) * 0.01))
    nodata = np.all(img == [128, 0, 0], axis=-1)
    return np.where(nodata, np.nan, h)


if __name__ == "__main__":
    fetch_bus_stops()
    fetch_stations()
    fetch_population_mesh()
    fetch_dem()
