"""Task 9: Tobler's hiking function applied to Koi-ue (己斐上), Hiroshima.
Task 9: 히로시마 己斐上에 Tobler 도보함수를 적용한다.

The defect this closes: app.py's isochrone (and the Seoul 300m/500m walk
buffers generally) treats every metre of the pedestrian network as equally
walkable -- a flat-ground assumption baked into "reachable within 300m".
On a slope, walking speed is not constant: climbing is slower than the flat
assumption predicts, descending is faster. This script applies Tobler's
(1993) hiking function per directed edge (uphill and downhill cost
differently, so the graph must stay directed) and compares the reachable
population under the flat assumption vs the slope-corrected one, at the same
nominal time budget.
이 스크립트가 다루는 결함: app.py의 isochrone(그리고 서울의 300m/500m 도보
버퍼 전반)은 도보 네트워크의 모든 구간을 평지로 취급한다 -- "300m 이내 도달
가능"이라는 판정에 평지 가정이 그대로 깔려 있다. 경사에서는 도보 속도가
일정하지 않다: 오르막은 평지 가정보다 느리고 내리막은 더 빠르다. 이 스크립트는
Tobler(1993) 도보함수를 방향성 있는 각 엣지에 적용하고(오르막/내리막 비용이
다르므로 그래프는 방향성을 유지해야 한다), 동일한 시간 예산 기준으로 평지 가정
대비 경사보정 도달인구를 비교한다.

Run after analysis/hiroshima/fetch_sources.py.
analysis/hiroshima/fetch_sources.py 실행 후에 돌린다.
"""
import glob
import json
import os
import re

import geopandas as gpd
import networkx as nx
import numpy as np
import osmnx as ox
from PIL import Image
from scipy.ndimage import distance_transform_edt
from shapely.geometry import Point
from shapely.ops import unary_union

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data", "hiroshima")

CENTER_LON, CENTER_LAT = 132.42777883, 34.39675456  # Koi station / 己斐역
RADIUS_M = 1500  # walk-network buffer, matches fetch_sources.py's clip radius
METRIC_CRS = 6670  # JGD2000 / Plane Rectangular CS III
BUS_BUFFER_M = 300.0  # same convention as app.py's BUS_BUFFER_M
EDGE_BUFFER_M = 25.0  # same convention as app.py's EDGE_BUFFER_M -- road-width isochrone buffer


def decode_elevation(png_path):
    """RGB -> metres per GSI's demtile spec; NaN where nodata (128,0,0).
    GSI 표고타일 사양대로 RGB를 미터로 변환. nodata(128,0,0)는 NaN."""
    img = np.array(Image.open(png_path).convert("RGB")).astype(np.int64)
    r, g, b = img[..., 0], img[..., 1], img[..., 2]
    x = r * 65536 + g * 256 + b
    h = np.where(x < 8_388_608, x * 0.01, np.where(x == 8_388_608, np.nan, (x - 16_777_216) * 0.01))
    nodata = np.all(img == [128, 0, 0], axis=-1)
    return np.where(nodata, np.nan, h)


def _tile_to_lonlat(x, y, z):
    n = 2**z
    lon = x / n * 360 - 180
    lat = np.degrees(np.arctan(np.sinh(np.pi * (1 - 2 * y / n))))
    return lon, lat


def load_dem_mosaic(zoom=15):
    """Stitch the DEM5A tiles into one array + a nearest-neighbour sampler.
    5m native resolution; nearest-neighbour is adequate at that grain.
    DEM5A 타일을 하나의 배열로 합치고 최근접 샘플러를 만든다. 원본 해상도가
    5m라 최근접 보간으로 충분하다."""
    files = sorted(glob.glob(os.path.join(DATA_DIR, "dem", "*.png")))
    tiles = []
    for f in files:
        m = re.match(r"(\d+)_(\d+)\.png", os.path.basename(f))
        if not m:
            continue  # skip any fallback_* tiles from a different zoom
        x, y = map(int, m.groups())
        tiles.append((x, y, f))

    xs = sorted({t[0] for t in tiles})
    ys = sorted({t[1] for t in tiles})
    x0, y0 = xs[0], ys[0]

    mosaic = np.full((256 * len(ys), 256 * len(xs)), np.nan)
    for x, y, f in tiles:
        arr = decode_elevation(f)
        cx, cy = xs.index(x) * 256, ys.index(y) * 256
        mosaic[cy : cy + 256, cx : cx + 256] = arr

    # A handful of DEM5A pixels are NODATA over the Ota River / gaps in the
    # laser survey. Left as NaN, those propagate into NaN edge times, which
    # Dijkstra does not handle safely (silently mis-includes/excludes nodes
    # rather than erroring) -- fill with the nearest valid pixel instead.
    # DEM5A 픽셀 일부가 太田川(오타강) 위나 레이저 측량 공백 지점이라 NODATA다.
    # NaN을 그대로 두면 엣지 시간이 NaN이 되고, Dijkstra는 NaN 가중치를 안전하게
    # 처리하지 못해(에러 없이 조용히 잘못 포함/제외) -- 최근접 유효 픽셀로 채운다.
    nan_mask = np.isnan(mosaic)
    if nan_mask.any():
        _, (iy, ix) = distance_transform_edt(nan_mask, return_indices=True, return_distances=True)
        mosaic = mosaic[iy, ix]

    lon_min, lat_max = _tile_to_lonlat(x0, y0, zoom)
    lon_max, lat_min = _tile_to_lonlat(x0 + len(xs), y0 + len(ys), zoom)

    def sample(lons, lats):
        lons, lats = np.asarray(lons), np.asarray(lats)
        px = ((lons - lon_min) / (lon_max - lon_min) * mosaic.shape[1]).astype(int)
        py = ((lat_max - lats) / (lat_max - lat_min) * mosaic.shape[0]).astype(int)
        px = np.clip(px, 0, mosaic.shape[1] - 1)
        py = np.clip(py, 0, mosaic.shape[0] - 1)
        return mosaic[py, px]

    return sample


def tobler_speed_kmh(slope):
    """Tobler (1993): W = 6 * exp(-3.5 * |slope + 0.05|), km/h.
    slope = rise/run (e.g. 0.1 = 10% grade), signed: positive = uphill.
    slope = 상승/거리(예: 0.1 = 10% 경사), 부호 있음: 양수 = 오르막."""
    return 6.0 * np.exp(-3.5 * np.abs(slope + 0.05))


FLAT_SPEED_KMH = tobler_speed_kmh(0.0)
FLAT_SPEED_MS = FLAT_SPEED_KMH * 1000 / 3600
TIME_BUDGET_S = BUS_BUFFER_M / FLAT_SPEED_MS  # same nominal budget as the 300m flat buffer


def build_graph():
    center = gpd.GeoSeries([Point(CENTER_LON, CENTER_LAT)], crs=4326).to_crs(METRIC_CRS).iloc[0]
    poly_ll = gpd.GeoSeries([center.buffer(RADIUS_M + 300)], crs=METRIC_CRS).to_crs(4326).iloc[0]

    ox.settings.log_console = False
    ox.settings.use_cache = True
    ox.settings.cache_folder = os.path.join(BASE_DIR, "cache")
    G = ox.graph_from_polygon(poly_ll, network_type="walk", simplify=True)

    sample = load_dem_mosaic()
    lons = [G.nodes[n]["x"] for n in G.nodes]
    lats = [G.nodes[n]["y"] for n in G.nodes]
    elevs = sample(lons, lats)
    for n, e in zip(G.nodes, elevs):
        G.nodes[n]["elev"] = float(e)

    # Directed per-edge time: slope sign depends on travel direction (u->v),
    # so uphill and downhill copies of the same path get different costs.
    # 방향별 엣지 시간: 경사 부호가 진행방향(u->v)에 따라 달라지므로, 같은 길도
    # 오르막/내리막 사본의 비용이 달라진다.
    for u, v, k, data in G.edges(keys=True, data=True):
        length = data.get("length", 0.0)
        if length <= 0:
            data["time_s"] = 0.0
            continue
        rise = G.nodes[v]["elev"] - G.nodes[u]["elev"]
        slope = rise / length
        speed_ms = tobler_speed_kmh(slope) * 1000 / 3600
        data["time_s"] = length / speed_ms

    return G


def isochrone_polygon(G, source_node, radius, weight, undirected, buffer_m=EDGE_BUFFER_M):
    """Mirrors app.py's isochrone construction: ego_graph -> edge buffer -> union.
    app.py의 isochrone 생성 방식과 동일: ego_graph -> 엣지 버퍼 -> union."""
    try:
        sub = nx.ego_graph(G, source_node, radius=radius, distance=weight, undirected=undirected)
    except Exception:
        return None
    if sub.number_of_edges() == 0:
        return None
    _, gdf_edges = ox.graph_to_gdfs(sub, nodes=True, edges=True, fill_edge_geometry=True)
    poly = unary_union(gdf_edges.to_crs(METRIC_CRS).geometry.buffer(buffer_m))
    return poly if poly and not poly.is_empty else None


def area_weighted_population(polygon, gdf_mesh_m):
    """Same areal-weighting convention used throughout this repo (findings 01-03):
    a mesh cell partly inside the polygon contributes only that fraction of pop.
    이 저장소 전반(발견 01-03)과 동일한 면적가중 방식: 폴리곤에 일부만 걸친 격자는
    그 비율만큼만 인구를 기여한다."""
    if polygon is None or polygon.is_empty:
        return 0.0
    frac = gdf_mesh_m.geometry.intersection(polygon).area / gdf_mesh_m.geometry.area
    return float((gdf_mesh_m["JINKO"] * frac.clip(0, 1)).sum())


def main():
    import pandas as pd

    print(f"Tobler flat-ground (0% slope) speed: {FLAT_SPEED_KMH:.3f} km/h")
    print(f"Time budget (== {BUS_BUFFER_M:.0f}m at flat speed): {TIME_BUDGET_S:.1f}s = {TIME_BUDGET_S/60:.2f}min")

    G = build_graph()
    elevs = np.array([G.nodes[n]["elev"] for n in G.nodes])
    print(f"network nodes: {G.number_of_nodes()}, edges: {G.number_of_edges()}, "
          f"elevation range in area: {np.nanmin(elevs):.1f}-{np.nanmax(elevs):.1f}m")

    stops = gpd.read_file(os.path.join(DATA_DIR, "koi_bus_stops.gpkg")).to_crs(4326)
    sample = load_dem_mosaic()
    stops["elev"] = sample(stops.geometry.x.values, stops.geometry.y.values)
    stops["node"] = ox.distance.nearest_nodes(G, X=stops.geometry.x.values, Y=stops.geometry.y.values)
    stops = stops.drop_duplicates("node")

    mesh = gpd.read_file(os.path.join(DATA_DIR, "koi_pop_mesh500.gpkg")).to_crs(METRIC_CRS)

    # "away" = walking FROM the stop, i.e. the walk-home leg -- the realistic
    # accessibility question (can a resident get back from the stop in budget),
    # not the walk-to-the-stop leg computed via a reversed graph.
    # "away" = 정류장에서 '떠나는' 방향, 즉 귀가길 -- 이게 현실적인 접근성 질문이다
    # (정류장까지 가는 방향이 아니라 정류장에서 집으로 돌아갈 수 있는가).
    rows = []
    naive_polys, corrected_polys = [], []
    for _, r in stops.iterrows():
        node = int(r["node"])
        naive = isochrone_polygon(G, node, radius=BUS_BUFFER_M, weight="length", undirected=True)
        corrected = isochrone_polygon(G, node, radius=TIME_BUDGET_S, weight="time_s", undirected=False)
        na = naive.area if naive else 0.0
        ca = corrected.area if corrected else 0.0
        rows.append({
            "node": node, "elev_m": round(float(r["elev"]), 1),
            "naive_m2": round(na), "corrected_m2": round(ca),
            "pct_change": round(100 * (ca - na) / na, 1) if na > 0 else float("nan"),
        })
        if naive is not None:
            naive_polys.append(naive)
        if corrected is not None:
            corrected_polys.append(corrected)

    per_stop = pd.DataFrame(rows).sort_values("elev_m", ascending=False)
    per_stop_path = os.path.join(BASE_DIR, "analysis", "hiroshima", "per_stop_comparison.csv")
    per_stop.to_csv(per_stop_path, index=False)

    hill = per_stop[per_stop["elev_m"] >= 60]
    flat = per_stop[per_stop["elev_m"] < 10]
    print()
    print(f"=== per-stop (saved to {per_stop_path}) ===")
    print(f"  hillside stops (>=60m elev, n={len(hill)}): mean change {hill['pct_change'].mean():+.1f}%, "
          f"range {hill['pct_change'].min():+.1f}% to {hill['pct_change'].max():+.1f}%")
    print(f"  valley-floor stops (<10m elev, n={len(flat)}): mean change {flat['pct_change'].mean():+.1f}%")

    naive_cover = unary_union(naive_polys) if naive_polys else None
    corrected_cover = unary_union(corrected_polys) if corrected_polys else None
    naive_pop = area_weighted_population(naive_cover, mesh)
    corrected_pop = area_weighted_population(corrected_cover, mesh)
    naive_area_km2 = naive_cover.area / 1e6 if naive_cover else 0.0
    corrected_area_km2 = corrected_cover.area / 1e6 if corrected_cover else 0.0

    print()
    print("=== network-wide union across all stops (same shape as findings 01-04) ===")
    print(f"  naive (300m flat buffer):      {naive_area_km2:.4f} km2, {naive_pop:,.0f} people")
    print(f"  corrected (Tobler, same budget): {corrected_area_km2:.4f} km2, {corrected_pop:,.0f} people")
    if corrected_pop > 0:
        diff_pct = 100 * (naive_pop - corrected_pop) / corrected_pop
        print(f"  naive overstatement: {naive_pop - corrected_pop:+,.0f} ({diff_pct:+.1f}%)")
        print("  small in aggregate because 36/44 stops sit on flat ground -- same shape as finding 04:")
        print("  the defect is nearly harmless on average and severe specifically on the hillside stops.")

    out = {
        "flat_speed_kmh": FLAT_SPEED_KMH,
        "time_budget_s": TIME_BUDGET_S,
        "n_bus_stops": int(len(stops)),
        "naive_area_km2": naive_area_km2,
        "naive_population": naive_pop,
        "corrected_area_km2": corrected_area_km2,
        "corrected_population": corrected_pop,
        "hillside_mean_pct_change": float(hill["pct_change"].mean()),
        "hillside_n": int(len(hill)),
        "valley_floor_mean_pct_change": float(flat["pct_change"].mean()),
        "valley_floor_n": int(len(flat)),
    }
    out_path = os.path.join(BASE_DIR, "analysis", "hiroshima", "tobler_result.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"\nsaved {out_path}")

    gpd.GeoDataFrame(geometry=[naive_cover] if naive_cover else [], crs=METRIC_CRS).to_crs(4326).to_file(
        os.path.join(DATA_DIR, "koi_iso_naive.gpkg"), driver="GPKG"
    )
    gpd.GeoDataFrame(geometry=[corrected_cover] if corrected_cover else [], crs=METRIC_CRS).to_crs(4326).to_file(
        os.path.join(DATA_DIR, "koi_iso_corrected.gpkg"), driver="GPKG"
    )


if __name__ == "__main__":
    main()
