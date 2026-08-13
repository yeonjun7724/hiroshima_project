# gis_session — FOSS4G Hiroshima talk

Seoul public-transport accessibility analysis, being rebuilt into a conference
talk. Roughly one month to delivery from 2026-08-13.

서울 대중교통 접근성 분석을 컨퍼런스 발표로 재구성하는 작업.
2026-08-13 기준 발표까지 약 1개월.

Working document (structure, findings, abstract draft):
[talk/storyline.html](talk/storyline.html) — also published as an artifact.

---

## Conventions

**Comments are bilingual: English first, Korean translation directly below.**
This applies to every code comment and docstring. The user asked for it
explicitly; it is not optional.

**주석은 영·한 병기. 영문을 먼저 쓰고 바로 아래 한글 번역을 단다.**
모든 코드 주석과 독스트링에 적용한다.

```python
# Areal weighting: a cell 30 % inside the district contributes 30 % of its
# population, not 100 %.
# 면적가중: 30%만 걸친 격자는 인구의 30%만 기여한다.
```

Prose in chat is Korean. Code identifiers stay English.

---

## The talk's thesis

The original course taught *how to write* GeoPandas. That part is now cheap.
The reframe: **AI-generated spatial analysis fails silently** — it runs, it
draws a map, and it is wrong. Four defects were found in this codebase and all
four are the same mistake: a spatial predicate answering *whether* two
geometries meet, used where the question was *how much*.

원래 교안은 GeoPandas '작성법'을 가르쳤다. 그 부분은 이제 값이 싸다.
리프레임: **AI가 생성한 공간분석은 조용히 틀린다** — 실행되고, 지도가 그려지고,
답이 틀리다. 발견된 결함 4건은 모두 같은 실수다.

Title: **Counted in Full**

---

## Findings (measured, reproducible)

| # | Defect | Location | Overstatement |
|---|--------|----------|---------------|
| 01 | Binary `intersects()` used for population | `3-4_session.ipynb` cell 75 | **+51.7 %** (8,672 vs 5,715) |
| 02 | Grid clipped, population not redistributed | `app.py:158`, 청림동 | **+34.8 %** (17,881 vs 13,265) |
| 03 | Cells straddling the 1,250 m radius counted whole | `3-4_session.ipynb` cell 82 | **+23.1 %** (10,906 vs 8,861) |
| 04 | Stops selected by administrative membership | `app.py:123`, 남현동 | **+3.2 %** (9 stops used, 362 relevant) |
| 05 | Join on a non-unique key (district *name*) | `geopandas_analysis.ipynb` cell 31 | **one district lost** |

Finding 05 is a different mechanism from 01–04 and the strongest anecdote.
Seoul has 426 dongs but only 425 distinct names: 신사동 exists in both 관악구
(11210680) and 강남구 (11230510). `set_index("region_nm").to_dict()` keeps one.
Result: 관악구 신사동 ends with NaN population, NaN score, **rank 427 of 427** —
it silently dropped out of an analysis about underserved districts. 강남구
신사동 appears twice, carrying its own population (24,296) and 관악구's (15,291).
No error, no warning; the table simply has 427 rows for 426 districts.

발견 05는 01~04와 메커니즘이 다르며 가장 강력한 일화다. 서울 426개 동의 이름은
425개뿐 — 신사동이 관악구와 강남구에 각각 있다. 이름으로 dict를 만들면 하나가
덮어써진다. 관악구 신사동은 인구·점수가 NaN이 되어 427위로 분석에서 소실되고,
강남구 신사동은 두 행에 걸쳐 두 동의 인구를 모두 가져간다.

Weight sensitivity — 231 combinations, step 0.05, nothing else changed:
**24 districts enter the Top 5, 7 reach rank 1.** 청림동 (published winner)
holds rank 1 in 39.4 %; 우이동, absent from the published result, takes rank 1
in 21.6 %; 사당4동 (published fifth) survives in 11.7 %.

Regenerate any of these with the scripts in `analysis/`.

---

## Decisions already made

- **Bugs are exhibits, not silent fixes.** `app.py` carries sidebar toggles
  that default to the ORIGINAL (incorrect) behaviour so both versions can be
  flipped live on stage. Do not "clean this up".
  **버그는 대조군이다. 조용히 고치지 않는다.** app.py 토글 기본값은 원본(오류)
  동작이다. 정리하지 말 것.
- **Finding 04 opens the talk but carries no weight.** Its small error is the
  point: the same bug is nearly harmless on empty mountainside and severe in a
  dense block. Severity belongs to the terrain, not the code. This is the
  bridge to the Hiroshima slope case.
- **Mapbox is out.** It is a proprietary SaaS dependency in a FOSS4G talk.
  Migrating to MapLibre + PMTiles and pydeck → lonboard.
- **GTFS / r5py is out of scope** for this talk. Mention as future work.

---

## Data notes that will bite you

- **The population grid is not all of Seoul.** `nlsp_021001001.shp` covers
  31.3 km² across 39 districts (관악구 and neighbours). Seoul is 605 km² /
  426 districts. Any grid-based statement is limited to that extent.
  **인구 격자는 서울 전체가 아니다.** 39개 동, 31.3km²만 덮는다.
- **Two different population sources.** Lecture 2's ranking uses registered
  population from `data/pop_by_admin.csv` (all 426 dongs). Lecture 4 and
  `app.py` use the 100 m grid. Grid defects do NOT affect the Top 5 ranking.
  **인구 출처가 두 개다.** 2강 순위는 등록인구, 4강·app.py는 격자.
  격자 결함은 Top5 순위에 영향을 주지 않는다.
- **Registered population is the independent check.** It validated the areal
  weighting: 남현동 +5.4 % → −0.9 %, 청림동 +24.0 % → −8.0 %.
- Analysis CRS is EPSG:5179 (metres); display CRS is EPSG:4326.

---

## Environment

geopandas 1.1.4 · shapely 2.1.2 · pandas 3.0.5 · osmnx 2.1.1 · streamlit 1.61.1 ·
lonboard 0.16.0 (added for Task 6; pulls in its own arro3 Arrow impl, doesn't
touch pyarrow)

**Known conflict:** installing streamlit/osmnx downgraded pyarrow 25.0.1 → 24.0.0,
and an `arcgis` package in the same environment pins `pyarrow<24`. The env is
already inconsistent. Task 10 moves the talk to an isolated pixi/uv environment
with a lockfile — do this before relying on any demo.

**알려진 충돌:** streamlit/osmnx 설치가 pyarrow를 24.0.0으로 내렸고, 같은 환경의
arcgis는 pyarrow<24를 요구한다. 이미 불일치 상태다. 데모를 신뢰하기 전에
10번(격리 환경 + 락파일)을 먼저 처리할 것.

---

## Layout

```
analysis/     forensic scripts + result CSVs (rerunnable)
talk/         storyline.html — talk structure, findings, abstract draft
data/         source data (large shp gitignored — see .gitignore)
outputs/      generated maps and gpkg (gitignored)
cache/        Overpass cache, ~400 MB (gitignored)
app.py        Streamlit demo — buffer vs network coverage, with A/B toggles
3-4_session.ipynb        lectures 3 & 4 (final)
geopandas_analysis.ipynb lectures 1 & 2
python_visualization.ipynb  lecture 3 early draft
practice.ipynb           lecture 3 exercise stub (has deliberate typos)
```

Notebook filenames do not match lecture numbers — see the mapping above.
노트북 파일명이 강의 번호와 일치하지 않는다. 위 매핑을 참고할 것.

---

## Remaining work, in order

1. ~~**Task 6** — pydeck → lonboard.~~ Done: `3-4_session.ipynb`'s 3D
   population-block cells now use `SolidPolygonLayer`/`PolygonLayer.from_geopandas`
   + `Map(basemap=MaplibreBasemap(style=CartoStyle...))`. Renders through
   MapLibre GL, zero Mapbox token. Verified via a standalone `to_html()`
   smoke test (synthetic data, not the real notebook run — that's Task 2).
   PMTiles (self-hosted basemap, not Carto's live CDN) is **not** done; it's
   now folded into Task 3 below since it's the same conference-wifi problem.
   **Task 6 완료**: 3D 인구블록 셀을 lonboard로 전환, MapLibre 렌더링·토큰 불필요.
   합성 데이터로 스모크 테스트만 검증(실제 노트북 실행은 Task 2). PMTiles
   자체 호스팅은 미완료 — Task 3으로 이관.
2. **Task 9** — Hiroshima slope case. 国土数値情報 stops, e-Stat 500 m mesh,
   DEM, Tobler's hiking function. **Ask before downloading** — state filename,
   source and size first.
3. **Task 3** — GeoParquet pre-bake + self-hosted PMTiles basemap so the demo
   survives conference wifi.
4. **Task 10** — isolated environment + lockfile.
5. **Task 2** — run all four notebooks end to end on pandas 3.0. This is
   where the lonboard cells (Task 6) get their first real execution against
   Seoul data — treat that as unverified until this runs.
6. **Task 8** (optional) — spopt MCLP against the greedy siting heuristic.

Talk runs ~36 min as structured; FOSS4G slots are usually 20–25. Compress
beat 02, protect beats 05 and 06.
구성상 약 36분인데 FOSS4G 슬롯은 보통 20~25분이다. 02단계를 압축하고
05·06단계를 지킬 것.

---

## Outstanding user action

The two exposed Mapbox tokens were removed from all files, but **they still
need to be revoked in the Mapbox account.** Not done as of the last session.

노출됐던 Mapbox 토큰 2개를 파일에서 모두 제거했으나, **Mapbox 계정에서
폐기(revoke)하는 것은 아직 남아 있다.**
