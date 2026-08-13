"""Task 3: pre-bake the Seoul-only admin boundary extract app.py needs.
Task 3: app.py가 필요로 하는 서울 한정 행정동 경계 추출본을 미리 만든다.

data/BND_ADM_DONG_PG.shp is nationwide (3,558 rows, 140MB) -- above GitHub's
100MB limit, so it's gitignored and was never committed. app.py, however,
already points at "BND_ADM_DONG_PG.gpkg", a file that has never existed in
this repo: app.py has been broken (FileNotFoundError on load) since it was
written, unless someone ran this exact filter-and-save step by hand first.
This script is that step, made rerunnable, writing GeoParquet instead of
GeoPackage -- smaller, and Task 3's whole point is surviving conference wifi
with as little to fetch as possible.
data/BND_ADM_DONG_PG.shp는 전국(3,558행, 140MB) 데이터라 GitHub 100MB 제한을
넘어 gitignore 대상이고 커밋된 적이 없다. 그런데 app.py는 이미 존재한 적 없는
"BND_ADM_DONG_PG.gpkg"를 가리키고 있다 -- 즉 누군가 이 필터링 단계를 수동으로
먼저 밟아두지 않는 한 app.py는 작성된 이후로 계속 로드 단계에서 깨져 있었다.
이 스크립트가 그 단계를 재현 가능하게 만든 것이며, GeoPackage 대신 GeoParquet로
저장한다 -- 더 작고, Task 3의 목적 자체가 컨퍼런스 와이파이에서 받을 게 최대한
적은 상태로 데모가 버티게 하는 것이기 때문이다.

Requires data/BND_ADM_DONG_PG.shp to be present locally (see CLAUDE.md, Data
notes) -- it is not fetched here since it's too big to script a download for
reliably; this only filters+converts what's already on disk.
로컬에 data/BND_ADM_DONG_PG.shp가 있어야 한다(CLAUDE.md 참고) -- 파일이 너무
커서 이 스크립트가 다운로드까지 책임지지는 않는다. 이미 있는 파일을
필터링·변환만 한다.
"""
import os

import geopandas as gpd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

SRC = os.path.join(DATA_DIR, "BND_ADM_DONG_PG.shp")
OUT = os.path.join(DATA_DIR, "BND_ADM_DONG_SEOUL.parquet")


def main():
    if not os.path.exists(SRC):
        raise SystemExit(
            f"{SRC} not found. This is the 140MB nationwide source -- see "
            "CLAUDE.md's Data notes for where it comes from. Fetch it "
            "separately, then rerun this script."
        )

    gdf = gpd.read_file(SRC)
    gdf["ADM_CD"] = gdf["ADM_CD"].astype(str)
    seoul = gdf[gdf["ADM_CD"].str.startswith("11")].copy()  # Seoul's prefecture-code prefix
    print(f"nationwide: {len(gdf)} rows -> Seoul: {len(seoul)} rows")
    if len(seoul) != 426:
        # Not fatal -- boundary revisions happen -- but CLAUDE.md's "426 dongs"
        # claim (finding 05) depends on this count, so a change here is worth flagging.
        print(f"WARNING: expected 426 Seoul dongs (per CLAUDE.md / finding 05), got {len(seoul)}")

    seoul.to_parquet(OUT)
    size_mb = os.path.getsize(OUT) / 1e6
    print(f"wrote {OUT} ({size_mb:.2f} MB)")


if __name__ == "__main__":
    main()
