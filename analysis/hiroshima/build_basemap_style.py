"""Task 3: hand-written MapLibre style.json for the self-hosted PMTiles basemap.
Task 3: 자체 호스팅 PMTiles 베이스맵용 MapLibre 스타일 JSON (직접 작성).

Protomaps' official themes (protomaps-themes-base) are generated via an npm
script -- no Python/pip equivalent exists. Rather than add a Node toolchain
to a Python project for one style file, this hand-writes a minimal dark
theme against the documented schema (docs.protomaps.com/basemaps/layers):
earth -> landuse -> water -> roads -> buildings -> boundaries -> place labels.
Not visually identical to the official theme, just self-hosted and legible.
Protomaps 공식 테마(protomaps-themes-base)는 npm 스크립트로 생성하고 파이썬/pip
대응품이 없다. 스타일 파일 하나 때문에 파이썬 프로젝트에 Node 툴체인을 넣는 대신,
문서화된 스키마 기준으로 다크 테마를 손으로 작성했다: earth -> landuse -> water
-> roads -> buildings -> boundaries -> 지명 라벨. 공식 테마와 똑같지는 않지만
자체 호스팅되고 읽을 수 있다.

Requires the local pmtiles tile server running (see notebook markdown / CLAUDE.md
for the exact `pmtiles serve` command) -- this script only writes the style JSON
that points at it.
로컬 pmtiles 타일 서버가 떠 있어야 한다(정확한 `pmtiles serve` 명령은 노트북/
CLAUDE.md 참고) -- 이 스크립트는 그 서버를 가리키는 스타일 JSON만 만든다.

CLI args let one script serve both self-hosted extracts in this repo (Koi-ue,
from Task 9, and 海老園四丁目/海老山南一丁目, from the lecture-4 merge) without
duplicating the layer-paint logic:
    python build_basemap_style.py                      # Koi-ue (default, port 8890)
    python build_basemap_style.py --name ebaen --port 8891 --out basemap_style_ebaen.json
CLI 인자로 이 저장소의 두 자체 호스팅 추출본(Task 9의 己斐上, 4강 병합의
海老園四丁目/海老山南一丁目)을 같은 레이어/색상 로직으로 재사용한다.
"""
import argparse
import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

parser = argparse.ArgumentParser()
parser.add_argument("--name", default="hiroshima_basemap", help="pmtiles archive basename (no extension) served by `pmtiles serve`")
parser.add_argument("--port", type=int, default=8890, help="port `pmtiles serve` is listening on")
parser.add_argument("--out", default="basemap_style.json", help="output style JSON filename, written under data/hiroshima/")
args = parser.parse_args()

OUT = os.path.join(BASE_DIR, "data", "hiroshima", args.out)

TILE_SERVER = f"http://localhost:{args.port}"
SOURCE_ID = "protomaps"
TILESET_NAME = args.name

style = {
    "version": 8,
    "sources": {
        SOURCE_ID: {
            "type": "vector",
            "url": f"{TILE_SERVER}/{TILESET_NAME}.json",
        }
    },
    "glyphs": "https://fonts.protomaps.dev/{fontstack}/{range}.pbf",  # labels only; falls back to no text if unreachable offline
    "layers": [
        {"id": "background", "type": "background", "paint": {"background-color": "#111318"}},
        {"id": "earth", "type": "fill", "source": SOURCE_ID, "source-layer": "earth",
         "paint": {"fill-color": "#171a21"}},

        {"id": "landuse-green", "type": "fill", "source": SOURCE_ID, "source-layer": "landuse",
         "filter": ["in", ["get", "kind"], ["literal", ["forest", "wood", "park", "national_park",
                                                          "nature_reserve", "grass", "meadow", "scrub", "garden"]]],
         "paint": {"fill-color": "#1c2b1e", "fill-opacity": 0.9}},
        {"id": "landuse-urban", "type": "fill", "source": SOURCE_ID, "source-layer": "landuse",
         "filter": ["in", ["get", "kind"], ["literal", ["residential", "commercial", "industrial",
                                                          "military", "railway", "cemetery"]]],
         "paint": {"fill-color": "#1e2029", "fill-opacity": 0.7}},

        {"id": "water", "type": "fill", "source": SOURCE_ID, "source-layer": "water",
         "paint": {"fill-color": "#0c3b52"}},

        {"id": "roads-minor", "type": "line", "source": SOURCE_ID, "source-layer": "roads",
         "filter": ["in", ["get", "kind"], ["literal", ["minor_road", "path"]]],
         "paint": {"line-color": "#3a3f4b", "line-width": ["interpolate", ["linear"], ["zoom"], 12, 0.5, 16, 1.5]}},
        {"id": "roads-major", "type": "line", "source": SOURCE_ID, "source-layer": "roads",
         "filter": ["==", ["get", "kind"], "major_road"],
         "paint": {"line-color": "#565d6e", "line-width": ["interpolate", ["linear"], ["zoom"], 10, 1, 16, 3]}},
        {"id": "roads-highway", "type": "line", "source": SOURCE_ID, "source-layer": "roads",
         "filter": ["==", ["get", "kind"], "highway"],
         "paint": {"line-color": "#7d8698", "line-width": ["interpolate", ["linear"], ["zoom"], 8, 1.2, 16, 4]}},
        {"id": "rail", "type": "line", "source": SOURCE_ID, "source-layer": "roads",
         "filter": ["==", ["get", "kind"], "rail"],
         "paint": {"line-color": "#8a6d3b", "line-width": 1, "line-dasharray": [2, 2]}},

        {"id": "buildings", "type": "fill", "source": SOURCE_ID, "source-layer": "buildings",
         "minzoom": 13,
         "paint": {"fill-color": "#262a35", "fill-opacity": 0.8}},

        {"id": "boundaries", "type": "line", "source": SOURCE_ID, "source-layer": "boundaries",
         "paint": {"line-color": "#5a5f6e", "line-width": 1, "line-dasharray": [3, 2]}},

        {"id": "place-labels", "type": "symbol", "source": SOURCE_ID, "source-layer": "places",
         "minzoom": 10,
         "layout": {"text-field": ["get", "name"], "text-size": 11, "text-font": ["Noto Sans Regular"]},
         "paint": {"text-color": "#c8ccd6", "text-halo-color": "#111318", "text-halo-width": 1.2}},
    ],
}

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(style, f, ensure_ascii=False, indent=2)
print(f"wrote {OUT}")
