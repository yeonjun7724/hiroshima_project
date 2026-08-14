# gis_session — FOSS4G Hiroshima talk

Seoul public-transport accessibility analysis, being rebuilt into a conference
talk. Roughly one month to delivery from 2026-08-13.

서울 대중교통 접근성 분석을 컨퍼런스 발표로 재구성하는 작업.
2026-08-13 기준 발표까지 약 1개월.

Working document (structure, findings, abstract draft):
[talk/storyline.html](talk/storyline.html) — also published as an artifact.

---

## ⚠️ Goal correction (2026-08-13, read this first)

Everything below "The talk's thesis" and "Findings" describes a plan that
was **built on a misunderstanding** and is now superseded. The user's actual
goal, stated directly: merge `3-4_session.ipynb` and `geopandas_analysis.ipynb`
(the two lecture notebooks) into **one notebook**, and replace **all** the
Seoul-specific data throughout with Hiroshima data, so it can be presented as
a normal tutorial at FOSS4G Hiroshima — "이렇게 코드를 짜면 이런 지도가
나온다" (write code like this, get a map like this). **Not** a bug-hunting
narrative. The "Counted in Full" defects reframe below was this session's own
invention, based on a stale reading of the goal — it is kept in this file for
reference (the Seoul findings are still real and reproducible) but is **not**
the current plan. Do not resume it without asking the user first.
사용자가 실제로 말한 목표: `3-4_session.ipynb`와 `geopandas_analysis.ipynb`
(강의 1~4강)을 **하나의 노트북으로 합치고**, 서울 데이터를 **전부** 히로시마
데이터로 바꿔서, FOSS4G Hiroshima에서 정상적인 튜토리얼("이렇게 코드를 짜면
이런 지도가 나온다")로 발표하는 것. 버그 찾기 내러티브가 아니다. 아래
"Counted in Full" 재구성은 이번 세션이 목표를 잘못 읽고 자체적으로 만든
방향이라 지금은 유효하지 않다 (서울 결함 자체는 실제고 재현 가능하니 참고자료로만
남겨둠). 사용자에게 먼저 묻지 않고 그 방향으로 되돌아가지 말 것.

**What's already usable toward the real goal:**
- The full section-by-section catalog of both notebooks (headers, what each
  section's code actually does, every Seoul data file touched, verbatim/
  near-duplicate content between the two, a hard sequential dependency — NB2
  loads `outputs/demo_admin.gpkg`/`demo_uncovered.gpkg`, which only exist
  because NB1 writes them at the end) is done — see
  [`analysis/notebook_merge_catalog.md`](analysis/notebook_merge_catalog.md).
  Start there, not by re-reading the notebooks.
- **City-wide Hiroshima data is now fetched**, not just the 1.5km Koi-ue
  buffer: `analysis/hiroshima/fetch_city_sources.py` re-clips the *same* raw
  downloads Task 9 already pulled (still cached in `data/hiroshima/_raw/`,
  no re-download) to all of Hiroshima City's 8 wards. Produces:
  - `data/hiroshima/hiroshima_city_admin.gpkg` — 1,136 chōme (小地域) across
    8 wards, **total pop 1,200,754** (matches Hiroshima City's real
    population — sanity-checked). Columns renamed `region_nm`/`ward_nm`/
    `pop`/`households`. **This is the Seoul `BND_ADM_DONG_PG.shp` +
    등록인구 CSV equivalent, already combined into one file** — see the
    correction below, it does double duty.
  - `data/hiroshima/hiroshima_city_bus_stops.gpkg` — 1,660 stops, city-wide.
  - `data/hiroshima/hiroshima_city_stations.gpkg` — 143 rail/streetcar
    stations, city-wide.
  - The Koi-ue-only extracts (`koi_*.gpkg`, 1.5km radius) are untouched and
    still there if the merged lecture wants a "zoom into one neighbourhood"
    demo section — Seoul's version does exactly this (남현동/청림동 out of
    426 dongs), so Koi-ue can play that same role rather than being wasted.
- **Correction to a Task 9 labeling mistake**: what this repo's docs/scripts
  called Hiroshima's "500m population mesh" (`koi_pop_mesh500.gpkg`, e-Stat
  `dlserveyId=A002005212020&downloadType=5`) is **not a regular grid** — it's
  real 小地域 (chōme/town) boundary polygons with population attached
  (`S_NAME` has real neighbourhood names like 八丁堀, 基町; `CITY_NAME` has
  real ward names like 広島市中区). Confirmed by inspecting the data directly,
  not assumed. This means it's the Seoul admin-boundary-plus-population
  equivalent, not a separate mesh product — one less data source to chase
  down than Task 9's notes implied. The variable/file naming ("mesh500")
  in `fetch_sources.py`/`tobler_slope_correction.py` is now misleading but
  left as-is since those scripts are for the abandoned slope-case narrative,
  not the merge.
- **Language decision (user-confirmed)**: `hiroshima_tutorial.ipynb` is
  English-first, Korean-translation-second throughout — both markdown prose
  *and* code comments (extending this file's existing bilingual-comment
  convention to the notebook's narrative text too, since FOSS4G Hiroshima's
  audience mostly won't read Korean). Exception: actual matplotlib-rendered
  output (plot titles, axis labels, legends, category values) is
  English-only — see the font note below for why.
- Still missing, not yet fetched:
  - **Bikeshare** (따릉이 equivalent, for lecture 3's "따릉이는 어디까지
    닿고 있는가"): Hiroshima's ぴーすくる (Peesakuru, run by DOCOMO Bike
    Share) publishes station data as GBFS via 公共交通オープンデータセンター
    (ODPT, api.odpt.org) — but it needs a free ODPT developer account +
    API token, which the user has to create themselves (self-service email
    signup, not something to do on their behalf without asking). **User
    chose to skip this and proceed with the rest for now** — ask again
    before spending more effort here, or ask the user to hand over a token.
  - A true regular population **mesh** (like Seoul's 100m
    `nlsp_021001001.shp`, used only in NB2 lecture 4 for the 3D lonboard
    population blocks) — not fetched. The chōme polygons above can likely
    substitute directly for this (extrude by chōme instead of by grid cell);
    probably don't need a separate mesh fetch unless the visual result looks
    bad with irregular chōme shapes instead of uniform squares.
- lonboard (Task 6), the uv environment (Task 10), and PMTiles self-hosting
  (Task 3) are all genuinely reusable regardless of narrative — they're
  infrastructure, not tied to the abandoned defects framing.
- Both source notebooks are 5MB+ and can't be opened with the Read tool
  (even offset/limit doesn't page a notebook this large — it always tries to
  load the whole file). Inspect them by writing small scripts that
  `json.load()` the file directly and work with `nb["cells"]`, same approach
  used throughout `analysis/`.
- A verbatim-duplicate section ("GeoPandas와 Folium의 차이") already exists in
  both notebooks — worth deduping during the merge, not carrying twice.

**Progress: Lecture 1 is drafted, executed, and verified** — see
`hiroshima_tutorial.ipynb` (47 cells, English-first/Korean-second throughout
per the user's language decision — see below). Covers NB1's cells 0-69:
Pandas/GeoPandas intro, folder setup, utility functions, admin boundary +
population, bus/rail aggregation, merge + derived indicators (bus/rail stops
per 10,000 residents), EDA. Executed end-to-end via nbclient, not just
read — that caught four real bugs the Seoul original never had to handle,
because Hiroshima's data has a different shape:
- `pd.qcut` on `bus_per_10k` crashed (`Bin edges must be unique`): 93 of
  1,136 small areas have zero registered population (parks, industrial
  land, the airport) — Seoul's coarser 426 dongs never hit this. Fixed by
  excluding zero-population areas from the per-capita indicator (NaN, not
  inf) rather than papering over it with `duplicates="drop"`.
- Even after that fix, qcut still failed: 40% of *populated* small areas
  have literally zero bus stops inside their own polygon (fine subdivision
  → most residents rely on a neighbouring block's stop). A 5-quantile split
  can't work when the bottom 40% of values are identical. Fixed by giving
  "no stop in block" its own explicit class and only quantile-splitting the
  areas that do have a stop.
- The `bus_class` choropleth's colors came out backwards (`"high"` rendered
  lightest, `"no stop in block"` darkest) because geopandas colors
  unordered categoricals alphabetically. Fixed with an explicit
  `pd.Categorical(..., ordered=True)`.
- Matplotlib rendered the Korean half of bilingual plot titles as tofu
  boxes: "Yu Gothic" (needed for Japanese place names) doesn't cover
  Hangul. Resolution: bilingual EN/KO applies to markdown prose and code
  comments only — actual matplotlib-rendered text (titles, axis labels,
  legends, category values) is English-only, since a font that covers
  Japanese place names *and* Korean *and* renders cleanly isn't a given.
- Not a bug, but caught by actually looking at the rendered map: outlying
  mountainous wards show as "high" bus accessibility per 10,000 residents —
  not because service is better, but because a tiny population denominator
  inflates the per-capita ratio. Left in as a teaching moment (added a
  markdown note) rather than hidden — same shape as the Seoul areal-weighting
  findings: a correct number describing the wrong thing.
- Also fixed on sight, not load-bearing: `target_top10`'s tie-break now
  favours population (most people affected first, not sort-order luck), and
  the two EDA scatter plots clip axes / cap labels at 5, since a few
  small-denominator outliers and 100+ overlapping labels made the raw
  version unreadable.

**Progress: Lecture 2 is also drafted, executed, and verified** —
`hiroshima_tutorial.ipynb` is now 80 cells. Covers NB1's cells 70-106:
buffer coverage (bus 300m / rail 500m), Union/Intersection/Difference,
uncovered-area extraction, min-max-normalized vulnerability score, Top-20/
Top-5 ranking, a Step1/2/3 comparison Folium map, and the spatial-
multicollinearity writeup. The GeoPandas-vs-Folium duplicate section was
skipped (already covered in lecture 1, per the catalog's dedup note).
- **The final demo area is data-derived, not hand-picked**: `final_names =
  candidate_top20.head(2)["region_nm"]` — whatever the real ranking produces.
  For this run that's **海老園四丁目 and 海老山南一丁目** (both 佐伯区/Saeki
  ward): ~1,100-1,300 residents, 0 bus stops, 0 stations, 87-100% uncovered.
  This is *not* Koi-ue (己斐上) from Task 9 — the ranking never put Koi-ue
  in the top 20, so forcing it in would have meant hand-picking the answer
  instead of letting the computed result stand. The earlier note in this
  file suggesting Koi-ue could double as the lecture 3-4 demo area was wrong;
  lecture 3-4 needs fresh Hiroshima data fetched for 海老園四丁目/海老山南一丁目's
  actual location instead (walk network, local population detail).
  `outputs/demo_admin.gpkg` / `demo_uncovered.gpkg` are written the same way
  Seoul's version did, for lecture 3-4 to load.
- Real fix, not cosmetic: the Top-5 map was originally unreadable — each
  small area is a tiny sliver against the whole city, so a thin red outline
  was invisible at city scale, and the 5 areas span two distant wards so a
  single shared zoom window didn't help either. Fixed with a small-multiples
  panel, one tightly-zoomed subplot per area, regardless of how scattered
  they are.
- No new bugs of the qcut/font/color-order kind this section — those were
  all fixed once in lecture 1 and the fixes carried forward cleanly.

**Next step:** lectures 3-4 from `3-4_session.ipynb`, using
`analysis/notebook_merge_catalog.md`'s cell-range tables. Needs fresh
Hiroshima source data for wherever 海老園四丁目/海老山南一丁目 actually are
(OSMnx walk network, a population-grid equivalent for the lonboard 3D
blocks) — the existing Koi-ue extracts from Task 9 do not cover this area
and are not the right base to build on for this lecture (see above).

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
- **Hiroshima bus stops (KSJ P11) are FY2010 data** — the government has not
  republished this dataset since; routes may have changed since then. The
  rail/streetcar (N02) and population mesh (e-Stat) sources are current
  (2025 and 2020-census respectively). Hiroshima analysis CRS is EPSG:6670
  (JGD2000 / Plane Rectangular CS III); display CRS is EPSG:4326.
  **히로시마 버스정류장(KSJ P11)은 2010년 데이터** — 정부가 그 이후 갱신하지
  않았다. 철도/노면전차(N02)와 인구격자(e-Stat)는 최신(각각 2025년, 2020년
  국세조사). 히로시마 분석 좌표계는 EPSG:6670, 표시 좌표계는 EPSG:4326.
- **lonboard's exported HTML must be served over HTTP, not opened via
  `file://`.** Double-clicking `deck_3d_population_...html` or
  `koi_slope_map.html` renders an empty map with no error dialog: the widget
  offloads GeoArrow parsing to a Web Worker, and browsers block worker script
  loading from `file://` origins. Confirmed by hitting this exact failure
  (blank map, `importScripts` errors in the console) and fixing it by running
  `python -m http.server` in the directory and opening `localhost:PORT/...`
  instead. This applies at the conference too — no internet needed, but a
  local server process must be running.
  **lonboard가 내보낸 HTML은 `file://`로 직접 열면 안 되고 반드시 HTTP로
  서빙해야 한다.** 더블클릭하면 에러 없이 빈 지도만 뜬다 — GeoArrow 파싱을
  Web Worker에서 하는데, 브라우저가 `file://`에서 워커 스크립트 로드를 막는다.
  실제로 이 실패(빈 지도, 콘솔에 importScripts 에러)를 겪고 `python -m
  http.server`로 서빙해서 고쳤다. 발표 당일에도 마찬가지 — 인터넷은 필요
  없지만 로컬 서버 프로세스는 반드시 떠 있어야 한다.

---

## Environment

**Isolated via uv — `uv run <command>` for everything, not the system Python.**
`pyproject.toml` + `uv.lock` pin exact versions (geopandas 1.1.4, shapely
2.1.2, pandas 3.0.5, osmnx 2.1.1, streamlit 1.61.1, lonboard 0.16.0, and
everything each of those pulls in transitively). First-time setup: `uv sync`
(installs into `.venv/`, gitignored). Verified end-to-end in this isolated
env: `analysis/hiroshima/tobler_slope_correction.py` reproduces its exact
published numbers, `hiroshima_slope_case.ipynb` executes clean via nbclient,
`app.py` serves and loads in a browser.
**uv로 격리됨 — 시스템 파이썬이 아니라 매사 `uv run <command>`를 쓸 것.**
처음 설정: `uv sync`. 이 격리 환경에서 실제로 검증함: Tobler 스크립트가 발표된
수치를 그대로 재현, 히로시마 노트북이 nbclient로 깨끗이 실행, app.py가 브라우저에서
정상 동작.

**Why this exists:** installing streamlit/osmnx into the old shared global
Python downgraded pyarrow 25.0.1 → 24.0.0, and an unrelated `arcgis` package
in that same global env pins `pyarrow<24` — a real, already-triggered
conflict. The uv environment is fully separate from that global install, so
it can't inherit the problem. `pyarrow` is pinned explicitly at 23.0.1 (below
both ceilings) precisely because of that history — don't bump it casually.
**왜 필요했는가:** 기존 공유 전역 파이썬에 streamlit/osmnx를 설치하며 pyarrow가
25.0.1→24.0.0으로 내려갔고, 같은 환경의 무관한 `arcgis` 패키지는 pyarrow<24를
요구한다 — 실제로 이미 터진 충돌이다. uv 환경은 그 전역 설치와 완전히 분리돼
있어 이 문제를 물려받을 수 없다. `pyarrow`를 23.0.1로 명시 고정한 것도 이
이력 때문이다 — 가볍게 올리지 말 것.

**Dev-only tools** (`uv add --dev`, not needed to run the actual demo):
`nbclient`/`nbformat` (headless notebook execution for verification),
`playwright` (browser-driven screenshot verification — this is how every
map/app change in this repo has actually been checked, not just read from
the diff).
**개발용 전용 도구**(`uv add --dev`, 실제 데모 실행에는 불필요):
`nbclient`/`nbformat`(검증용 헤드리스 노트북 실행), `playwright`(브라우저
스크린샷 검증 — 이 저장소의 지도/앱 변경은 실제로 이렇게 확인해왔다).

---

## Layout

```
analysis/     forensic scripts + result CSVs (rerunnable)
analysis/hiroshima/  Task 9 data acquisition (fetch_sources.py, rerunnable)
talk/         storyline.html — talk structure, findings, abstract draft
data/         source data (large shp gitignored — see .gitignore)
data/hiroshima/  Task 9 clipped extracts + DEM tiles (_raw/ gitignored)
outputs/      generated maps and gpkg (gitignored)
cache/        Overpass cache, ~400 MB (gitignored)
tools/        local dev binaries (go-pmtiles), gitignored, not project source
app.py        Streamlit demo — buffer vs network coverage, with A/B toggles
3-4_session.ipynb        lectures 3 & 4 (final)
geopandas_analysis.ipynb lectures 1 & 2
practice.ipynb           lecture 3 exercise stub (has deliberate typos)
hiroshima_slope_case.ipynb  lonboard map of the Task 9 result
pyproject.toml / uv.lock    the actual dev environment (Task 10) — use this,
                            not requirements.txt, which exists only in case
                            something still expects it for Streamlit Cloud
                            auto-detection and has not been verified against it
```

Notebook filenames do not match lecture numbers — see the mapping above.
노트북 파일명이 강의 번호와 일치하지 않는다. 위 매핑을 참고할 것.

---

## Remaining work, in order

**⚠️ This numbered list (Tasks 2/3/6/8/9/10) was built for the abandoned
"Counted in Full" plan — see the goal-correction section near the top of
this file.** The infrastructure items (6, 3, 10) are still genuinely done
and reusable; treat the rest as historical. The real next task — merging
the two lecture notebooks into a Hiroshima-localized tutorial — isn't on
this list yet because the plan for it doesn't exist yet.

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
2. ~~**Task 9** — Hiroshima slope case, Koi-ue (己斐上).~~ Done:
   `analysis/hiroshima/fetch_sources.py` (data) +
   `analysis/hiroshima/tobler_slope_correction.py` (analysis). Tobler's
   (1993) hiking function applied per directed edge (uphill/downhill cost
   differently) to the walk-home leg from each of 44 bus stops, compared
   against the flat-ground 300m buffer app.py already uses.
   **Result**: small in aggregate (+2.4%, 788 people, network-wide union)
   but the same shape as finding 04 — nearly harmless on the 26 valley-floor
   stops (mean −0.7%), severe on the 10 hillside stops ≥60m elevation (mean
   −15.5%, worst single stop −32.5%). Per-stop numbers in
   `analysis/hiroshima/per_stop_comparison.csv`.
   A real bug was caught and fixed during this work, not just narrative
   material: 7 DEM pixels were NaN (river/survey gaps), which produced NaN
   edge times that networkx's Dijkstra doesn't handle safely — one edge
   case silently inflated a single stop's catchment by ~75x before a
   nearest-valid-pixel fill closed it. Left in git history as a reminder
   that this failure mode (spatial predicate silently wrong, no
   exception) is exactly what the talk is about, including in the tooling
   built *for* the talk.
   **Task 9 완료**: 언덕 정류장(10곳, 평균 −15.5%)에서는 뚜렷하지만 평지
   정류장(26곳, −0.7%)에서는 거의 없어 finding 04와 같은 모양. 작업 중 NaN
   표고(강/측량 공백 7개 픽셀)가 Dijkstra에서 조용히 특정 정류장의 도달범위를
   75배 부풀리는 실제 버그를 발견·수정함 — 발표의 주제(조용히 틀리는 공간분석)가
   발표 준비 도구에서도 그대로 재현된 사례.
3. ~~**Task 3** — GeoParquet pre-bake + self-hosted PMTiles basemap.~~ Done.
   `analysis/prebake_seoul_admin.py` filters the 140MB nationwide boundary
   shapefile to Seoul's 426 dongs and writes `data/BND_ADM_DONG_SEOUL.parquet`
   (4.15MB, committed). This fixed a real, previously-undiscovered bug: app.py
   pointed at `data/BND_ADM_DONG_PG.gpkg`, a file that has **never existed**
   in this repo — app.py has been broken since it was written. Verified live
   in a browser (Playwright): both 남현동 and 청림동 load, KPIs match the
   published findings (청림동 total pop 17,881, matching finding 02) and both
   maps render.
   PMTiles: confirmed MapLibre GL JS (and so lonboard's bundled instance)
   does **not** speak `pmtiles://` natively — needs the JS plugin's
   `addProtocol`, which lonboard doesn't register. Worked around it by
   converting server-side instead of client-side: `go-pmtiles serve` decodes
   the archive into plain XYZ tile HTTP responses, so the browser never needs
   the protocol at all. `data/hiroshima/hiroshima_basemap.pmtiles` (5.5MB) is
   a Koi-ue-area extract from `build.protomaps.com`'s daily build (range
   requests only — never downloaded the 120GB global file).
   `analysis/hiroshima/build_basemap_style.py` writes a hand-built dark style
   (Protomaps' official theme needs npm; skipped that for one style file).
   `hiroshima_slope_case.ipynb` wires it in with a live-URL check that falls
   back to CartoCDN if the local servers aren't running. Full offline
   procedure is in that notebook's last cell.
   **Task 3 완료**: GeoParquet 사전굽기 중 app.py의 실제 버그(존재한 적 없는
   파일 참조, 작성 이후 계속 깨져 있었음)를 발견·수정함. PMTiles는 MapLibre가
   `pmtiles://`를 네이티브 지원하지 않음을 확인하고, 서버 쪽에서 미리 일반
   XYZ 타일로 변환해 서빙하는 방식(`go-pmtiles serve`)으로 우회함. 오프라인
   절차는 `hiroshima_slope_case.ipynb` 마지막 셀 참고.
4. ~~**Task 10** — isolated environment + lockfile.~~ Done: `uv` project,
   `pyproject.toml` + `uv.lock`, all versions pinned to what was already
   validated this session (see Environment section above). Missed one
   dependency on the first pass — `osmnx.distance.nearest_nodes` needs
   scikit-learn, which wasn't in any top-level import so it slipped past the
   initial pinning by direct-import inspection; caught by actually running
   `tobler_slope_correction.py` in the new env, not by reading requirements
   off imports. `.venv/` and `tools/` are both gitignored (regenerate via
   `uv sync`; `tools/` needs `go-pmtiles` refetched separately, see Task 3).
   **Task 10 완료**: uv 프로젝트로 전환, 이번 세션에서 이미 검증된 버전 그대로
   고정. 첫 시도에서 scikit-learn 하나를 놓쳤다(어떤 코드도 직접 import하지
   않아서) — 실제로 스크립트를 돌려보고서야 잡음. import 목록만 보고 판단하지
   않은 이유.
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
