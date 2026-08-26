# 노트북 병합 카탈로그 — geopandas_analysis.ipynb + 3-4_session.ipynb

`CLAUDE.md`의 "Goal correction" 섹션이 정의한 실제 작업(두 강의 노트북을 하나로
합치고 서울 데이터를 히로시마로 전면 교체)을 위해 2026-08-13에 Explore 에이전트로
두 노트북 전체를 조사한 결과. 헤더만이 아니라 각 섹션 코드가 실제로 뭘 하는지,
어떤 데이터를 쓰는지, 어디가 중복인지까지 담았다. 병합 계획을 짤 때 이 문서에서
시작하면 되고, 다시 조사할 필요 없다 (조사 자체가 에이전트로 약 6분 걸림).

**하드 의존성**: `geopandas_analysis.ipynb`(1·2강) 맨 끝에서
`outputs/demo_admin.gpkg`, `outputs/demo_uncovered.gpkg`(청림동·남현동 2개
동만 추출)를 저장하고, `3-4_session.ipynb`(3·4강)가 그걸 시작점으로 불러온다.
이 두 파일은 `outputs/*.gpkg` 패턴으로 gitignore돼 있어 저장소엔 없다 — 두 노트북을
합칠 때 이 순차 의존성을 유지할지, 한 노트북 안에서 한 번만 만들지 결정 필요.

---

## NOTEBOOK 1 — `geopandas_analysis.ipynb` (1·2강, 107 cells: code 85 / markdown 22)

### 헤더 전체 (순서대로, cell index)

```
[0]   ### [문제 인식] 닿지 않는 공간을 처음으로 인식하다
[0]     #### Python을 활용한 공간데이터 전처리
[1]   ### Pandas
[1]   ### GeoPandas
[6]   ### 0. 폴더 구조 설정
[7]     #### 데이터 출처
[9]   ### 1. 유틸 함수 설정
[14]  ### 2. Shp 파일로 구성된 공간 데이터 전처리
[14]    #### 행정동 경계 벡터 데이터를 통한 면적 계산
[23]  ### 3. 일반 CSV 데이터 전처리
[23]    #### 인구데이터 처리
[36]  ### 4. 공간정보가 부여된 CSV 파일 전처리 : 버스 및 지하철 집계
[40]    #### 좌표계(CRS, Coordinate Reference System)
[40]    #### EPSG:4326 (WGS84, 위경도 좌표계)
[40]    #### EPSG:5179 (Korea 2000 / Central Belt)
[40]    #### 4326과 5179의 핵심 차이
[40]    #### 실무 권장 원칙
[52]  ### 5. 가공 데이터 병합 및 파생지표
[62]    #### Shapefile(.shp)와 GeoPackage(.gpkg) 요약 비교
[62]    #### 활용 권장
[62]    #### 한 줄 요약
[63]  ### 6. EDA(Exploratory Data Analysis)
[64]    #### "버스 접근성이 낮은 동은 지하철 접근성도 좋지 않은가?"
[67]    #### "인구 밀도가 높은데 버스 접근성은 충분한가?"
[70]  ### [공간 파생변수 생성] 닿는 곳과 닿지 않는 곳을 공간으로 분리하다
[70]    #### 버퍼 기반 커버 / 비커버 분석 (GeoPandas)
[71]    #### 보행 접근권 설정 기준
[76]    #### 공간 연산 기본 개념 (Union · Intersection · Difference)
[98]  ### GeoPandas와 Folium의 차이   ← NB2에도 동일 문단 있음 (중복, 아래 §4)
[103] ### [과업의 한계] 단계별 교통 취약 지역 비교 인사이트
[103]   #### Step 1: 교통만 기준
[103]   #### Step 2: 교통 + 인구 기준
[103]   #### Step 3: 교통 + 인구 + 직선거리 기반 커버리지 기준
[103] ### 종합 해석 및 다음 단계
[105] ### 📌 공간적 다중공선성 (Spatial Multicollinearity)
```

### 섹션별 코드가 실제로 하는 일 + 셀 구성

| 섹션 (cell 범위) | code/md | 실제로 하는 일 |
|---|---|---|
| 인트로 / Pandas vs GeoPandas (0–5) | 3/2 | `%pip install geopandas`; pandas/numpy/matplotlib/geopandas import; 한글 폰트(Malgun Gothic) 설정 |
| 0. 폴더 구조 설정 (6–8) | 1/2 | `BASE_DIR`/`DATA_DIR`/`OUT_DIR` 정의, `data/`/`outputs/` 생성 |
| 1. 유틸 함수 설정 (9–13) | 4/1 | `read_csv_safely`(utf-8→cp949 폴백), `to_num`, `norm_nm`(동명 정규화, `.`→`·`), `ensure_crs` |
| 2. Shp 전처리 (14–22) | 8/1 | `BND_ADM_DONG_PG.shp` 로드 → id/name/geometry만 남김 → `region_id`/`region_nm`로 리네임 → 코드 `"11"` 시작(서울)만 필터 → 경계 플롯 → 이름 정규화 → EPSG:5179 변환 → `area_km2` 계산 → `area_by_admin.csv` 저장 |
| 3. CSV 전처리 (23–35) | 12/1 | 등록인구 CSV(3행 멀티헤더) 로드 → 동/남/여 컬럼 서브스트링으로 탐색 → 리네임 → 합계/소계 행 제거 → 숫자 강제변환 → `population` 합산 → 동이름→`region_id` 매핑 → area와 merge → `pop_density` 계산 → 코로플레스 플롯 → `pop_by_admin.csv` 저장 |
| 4. 버스/지하철 집계 (36–51) | 14/2 | 버스정류장 xlsx 로드 → X/Y로 Point GeoDataFrame(4326→5179) → `sjoin(within)` 행정동 폴리곤과 조인 → groupby→`bus_stop_cnt` → 플롯 → `bus_stop_cnt_by_admin.csv` 저장; 지하철 CSV도 동일 파이프라인 반복 → `subway_cnt_by_admin.csv`. CRS 개념 설명(4326 vs 5179) 포함 |
| 5. 병합/파생지표 (52–62) | 9/2 | 파생 CSV 4개 재로드 → `region_id`로 merge → NaN 카운트 0 채움 → `region_id` dtype 정규화 → `bus_per_10k`/`subway_per_10k` 계산 → `qcut`으로 5단계 `bus_class` → 코로플레스 플롯 → 전체 병합 맵 `outputs/eda_map_dong.gpkg` 저장. Shapefile vs GeoPackage 비교 마크다운 포함 |
| 6. EDA (63–69) | 4/3 | 버스 vs 지하철 접근성 산점도(하위 10개 동 강조, `target_top10`); 인구밀도 vs 버스접근성 산점도(고밀도·저버스 동 강조, `target2`) |
| [공간 파생변수 생성] 커버리지 분석 (70–97, 가장 큼) | 24/4 | 버스정류장 300m/지하철역 500m 버퍼 → 각각 `union_all()` → 하나로 union → 행정동 폴리곤에서 `difference()` → `uncovered_geom` → `uncovered_area_m2`/`uncovered_ratio` 계산 → 인구밀도/비커버비율/역카운트 역수를 min-max 정규화 → 가중치(0.33 균등) `vulnerability_score` 계산 → 동 랭킹 → Top5/Top20 후보 선정 → Top5 폴리곤 + 비커버 음영 지도 |
| GeoPandas와 Folium의 차이 (98–102) | 4/1 | `%pip install folium`; Folium 인터랙티브 지도(OSM 타일)에 Step1/2/3 후보 동 폴리곤(색상/점선 다르게) + 지하철/버스 마커(`MarkerCluster`) 오버레이 → `seoul_steps_compare.html` 저장(노트북 cwd에, `OUT_DIR` 아님) |
| [과업의 한계] (103–104) | 1/1 | 3단계 비교의 한계에 대한 회고 마크다운(정류장수·버퍼커버리지 간 공간적 다중공선성); 최종 데모 동 `["청림동", "남현동"]` 선정 코드 |
| 공간적 다중공선성 (105–106) | 1/1 | 공간적 다중공선성 정의 마크다운; `gdf_vuln`을 데모 2개 동으로 필터 → **`outputs/demo_admin.gpkg`**(폴리곤만), **`outputs/demo_uncovered.gpkg`**(비커버 geometry만) 저장 — NB2가 시작점으로 불러오는 바로 그 파일 |

### 외부 데이터 파일 (정확한 이름)

**원본 입력 (`data/`):**
- `BND_ADM_DONG_PG.shp` (+`.dbf/.shx/.prj/.cpg`) — 서울 행정동 경계 폴리곤 (VWorld)
- `등록인구_20260126112616.csv` — 등록인구, 3행 멀티헤더 (서울 열린데이터광장)
- `서울시버스정류소위치정보(20260108).xlsx` — 서울 버스정류장 위치 (서울 열린데이터광장)
- `서울교통공사_1_8호선 역사 좌표(위경도) 정보_20250814.csv` — 서울 지하철 1~8호선 역 좌표 (data.go.kr)

**노트북 내에서 저장 후 재로드하는 중간 산출물:**
- `data/area_by_admin.csv`, `data/pop_by_admin.csv`, `data/bus_stop_cnt_by_admin.csv`, `data/subway_cnt_by_admin.csv`
- `outputs/eda_map_dong.gpkg` (서울 전체 병합 맵, layer `eda_map_dong`)
- `outputs/demo_admin.gpkg`, `outputs/demo_uncovered.gpkg` — **NB2가 소비**
- `seoul_steps_compare.html` (cwd에 저장)

---

## NOTEBOOK 2 — `3-4_session.ipynb` (3·4강, 97 cells: code 73 / markdown 24)

### 헤더 전체

```
[0]   ### [3강] 따릉이는 어디까지 닿고 있는가
[0]     #### Folium 기반 따릉이 커버리지 시각화
[2]     #### OSMnx · NetworkX 기반 최단경로 알고리즘
[5]   ### GeoPandas와 Folium의 차이   ← NB1에서 중복 (§4)
[7]     #### 0. 데이터 디렉토리 설정
[9]     #### 1. 유틸 함수
[12]    #### 2. 데이터 로드
[26]    #### Folium 지도(Tile) 선택 기준 이해하기
[26]      ##### 실습이 목적일 때는 안정성을 최우선으로 선택한다
[26]      ##### 결과를 보여주는 단계에서는 지도 가독성을 고려한다
[26]      ##### 분석 결과 자체를 설명해야 할 때는 배경을 최대한 단순화한다
[26]      ##### 왜 타일 선택이 중요한가?
[28]    #### Folium 시각화 시 EPSG:4326을 사용하는 이유
[28]      ##### 실무 기준 좌표계 사용 원칙
[31]    #### Folium 핵심 함수 한눈 요약
[36]    #### 3. OSMnx · NetworkX 기반 최단경로 알고리즘
[44]    #### 노드(Node)와 링크(Link)
[49]    #### 이 블록에서 꼭 알아야 할 핵심 함수(실무 필수)
[49]      ##### 1) GeoDataFrame.iterrows()
[49]      ##### 2) ox.distance.nearest_nodes(G, X, Y)
[49]      ##### 3) nx.single_source_dijkstra_path_length(G, source, cutoff, weight)
[49]      ##### 4) nx.shortest_path(G, u, v, weight)
[49]      ##### 5) LineString([...])
[49]      ##### 6) GeoSeries(...).to_crs(5179).length
[49]      ##### 7) dict.setdefault(key, default)
[56]  ### [4강] 어디에 놓아야 가장 효과적인가
[56]    #### Pydeck 기반 신규 따릉이 설치 시뮬레이션
[60]    #### Folium과 Pydeck의 차이
[84]    #### MapLibre
[89]    #### 꼭 알아야 할 lonboard 핵심 함수·개념 정리
[89]      ##### 1. Layer (예: SolidPolygonLayer, PolygonLayer)
[89]      ##### 2. accessor는 컬럼 '이름'이 아니라 '배열'이다
[89]      ##### 3. MapViewState : 카메라 위치와 시점
[89]      ##### 4. Map : 최종 지도 객체
[89]      ##### 5. Map.to_html()
[91]    #### 시각화 좌표계 사용 원칙 (EPSG:4326)
[91]      ##### 권장 좌표계 흐름
```

### 섹션별 코드가 실제로 하는 일

**3강 블록 (cells 0–55, 41 code / 15 md)**

| 섹션 | code/md | 실제로 하는 일 |
|---|---|---|
| 인트로/개념 (0–4) | 2/3 | `%pip install osmnx`; geopandas, shapely `LineString`/`mapping`, folium+`MarkerCluster`, `osmnx`, `networkx` import |
| Folium/GeoPandas 차이 + 폴더설정 (5–8) | 1/3 | `BASE_DIR`/`DATA_DIR`/`OUT_DIR` 설정, `outputs/` 생성 |
| 1. 유틸 함수 (9–11) | 2/1 | `norm_nm`, `read_csv_safely` 재정의 (NB1과 동일 로직, `to_num`/`ensure_crs`는 없음) |
| 2. 데이터 로드 (12–25) | 13/1 | `outputs/demo_admin.gpkg`/`demo_uncovered.gpkg`(NB1 산출물, 2개 동) 로드, 버스 xlsx + 지하철 csv + **`서울시 따릉이대여소 마스터 정보.csv`**(따릉이) 재로드 → 각각 Point GeoDataFrame → 좌표 0/NaN 행 제거 → 전부 EPSG:5179 변환 |
| Folium 타일선택 + EPSG4326 근거 + 함수요약 (26–35) | 9/3 | 버스/지하철/따릉이를 데모 행정동에 `sjoin` → 점점 레이어가 느는 Folium 지도 3개(OSM→CartoDB Positron→CartoDB Voyager) → 각각 별도 HTML(`bus_admin_uncovered.html`, `admin_uncovered_bus_subway.html`, `admin_uncovered_bus_subway_bike.html`) |
| 3. OSMnx·NetworkX 최단경로 (36–48) | 12/3 | 행정동 폴리곤 union+8km버퍼 → `ox.graph_from_polygon`로 도보망 → 따릉이 정류소 4326 변환 → 버스/지하철 동별 dict 그룹 → 버스+지하철 합쳐 `gdf_stop_5179`/`gdf_stop_ll` → 전체 정류장 최근접노드 스냅(`nearest_nodes`) → `node_to_stops` 맵 구성; 따릉이 정류소마다 노드 스냅 → `single_source_dijkstra_path_length`(cutoff=5분≈1250m@15km/h) → 도달 가능 정류장 노드 필터 → `shortest_path` 복원 → `LineString` 경로 생성 → EPSG:5179 길이 계산 → `routes`/`fails` 리스트에 추가 |
| 함수요약 + 저장 (49–55) | 6/1 | `routes`/`fails`를 GeoDataFrame/DataFrame으로 → `outputs/routes_all.gpkg`(레이어는 stop_type별: bus/subway), `outputs/routes_fail.csv` 저장; 최종 통합 Folium 지도(행정동+비커버+버스/지하철/따릉이 마커+5분 경로, 타입별 색상) → `outputs/lecture3_map_with_uncovered_routes_5min.html` |

**4강 블록 (cells 56–96, 32 code / 9 md)**

| 섹션 | code/md | 실제로 하는 일 |
|---|---|---|
| 인트로/Folium-Pydeck 비교 (56–61) | 1/4 | `%pip install lonboard`; Folium(2D 인터랙티브) vs Pydeck(3D/GPU, deck.gl) 역할 설명 마크다운 |
| import + 격자 로드 (62–66) | 5/0 | `lonboard`(`Map`, `PolygonLayer`, `SolidPolygonLayer`, `CartoStyle`, `MaplibreBasemap`, `MapViewState`) import; **`data/nlsp_021001001.shp`**(100m 인구격자) 로드 → EPSG:5179 변환 → `pop` 컬럼 숫자 강제변환; `outputs/demo_uncovered.gpkg` 재로드(3강 세션 상태와 독립) |
| 교통 union + 최근접조인 필터링 (67–76) | 10/0 | 버스/지하철 5179 변환 후 `gdf_transit`로 union; 격자 중심점 계산; `sjoin_nearest` 중심점→교통, `distance_col`; `dist_m <= 1250m` 필터 → `gdf_cand`(후보 격자); `is_uncovered`(이진 intersects)와 `unc_frac`(면적가중 교차비율) 계산 — 코드 주석에 이진 카운팅이 비커버 인구를 +51.7% 과대계상한다고 명시 |
| 후보 격자 선정 + KPI (77–83) | 7/0 | 특정 격자 id 선정(`sel_gid = "다사545408"`, 인구최대값 자동 폴백 있음) → 그 중심점 기준 1250m 원형 버퍼 → 버퍼와 겹치는 후보 격자 필터 → `in_frac`(부분중첩 가중)과 `pop_eff` 계산 → 면적가중 KPI 블록 출력(총/비커버/커버 인구, 비가중 대비 과대계상 %) |
| MapLibre 베이스맵 + 압출/색상 (84–90) | 4/2 | `BASEMAP_STYLE`(CartoStyle DarkMatter/Positron/Voyager) 설정; 4326 재변환; 인구 기반 `elev` 계산(멱함수 스케일, 99.5퍼센타일 캡); 인구 분위 breakpoint 계산; 분위별 `fill_color` 부여(비커버 셀은 alpha 부스트) |
| lonboard 렌더 (91–96) | 5/2 | `circle_ll` 링 geometry 생성; `SolidPolygonLayer.from_geopandas`(3D 압출 인구블록) + `PolygonLayer.from_geopandas`(반경 링 외곽선); 선택 격자 중심 기준 pitch/bearing `MapViewState`; `lonboard.Map` 조립 → `deck_3d_population_yellow_orange_red_radius_only.html` 저장 → 인라인 렌더; 마지막 마크다운에 스크린샷이 낡았다는(pydeck 시절, lonboard 전환 전) 메모 있음 |

### 외부 데이터 파일

**NB1에서 이어받음 (새 커널 세션이라 다시 로드, 공유 안 됨):**
- `outputs/demo_admin.gpkg`, `outputs/demo_uncovered.gpkg` (3강 설정에서 한 번, 4강 설정에서 또 한 번 독립적으로 로드)
- `data/서울시버스정류소위치정보(20260108).xlsx`
- `data/서울교통공사_1_8호선 역사 좌표(위경도) 정보_20250814.csv`

**이 노트북에 새로 등장:**
- `data/서울시 따릉이대여소 마스터 정보.csv` — 서울 자전거 공유(따릉이) 정류소 마스터 정보
- `data/nlsp_021001001.shp` (+ sidecar) — 100m 인구격자 shapefile (국토정보플랫폼)

**생성 산출물:**
- `outputs/bus_admin_uncovered.html`, `outputs/admin_uncovered_bus_subway.html`, `outputs/admin_uncovered_bus_subway_bike.html`
- `outputs/routes_all.gpkg`, `outputs/routes_fail.csv`
- `outputs/lecture3_map_with_uncovered_routes_5min.html`
- `deck_3d_population_yellow_orange_red_radius_only.html` (cwd에 저장, `OUT_DIR` 아님)

---

## 4. 두 노트북 간 중복/겹치는 교육 내용

1. **"GeoPandas와 Folium의 차이" 마크다운** — 완전 동일 문단. NB1 cell [98], NB2 cell [5].
2. **`norm_nm()`/`read_csv_safely()` 유틸 함수** — 두 노트북에서 거의 동일하게 처음부터 재정의(NB1 [10],[12]; NB2 [10],[11]). NB1엔 `to_num()`/`ensure_crs()`가 더 있는데 NB2는 안 씀(대신 `pd.to_numeric(..., errors="coerce")`를 인라인으로 씀). 병합 시 공용 유틸 섹션으로 뺄 것.
3. **CRS 개념을 두 번 가르침, 결론도 겹침.** NB1 [40]번 블록(좌표계 개념, 4326, 5179, 핵심 차이, **실무 권장 원칙**)이 이미 "분석은 5179, 시각화는 4326"을 확립. NB2 [28]번 블록("Folium 시각화 시 EPSG:4326을 사용하는 이유" + **실무 기준 좌표계 사용 원칙**)이 사실상 같은 규칙을 Folium 관점으로만 다시 가르침. 하나의 일반 CRS 설명(NB1) + Folium 전용 짧은 참조(NB2)로 합칠 것.
4. **버스정류장/지하철역 로드→Point→변환 파이프라인이 거의 줄 단위로 중복.** NB1 [37]-[48]과 NB2 [17]-[22]가 같은 원본 파일 2개를 읽어서 같은 방식(`gpd.points_from_xy` → `crs=4326` → `.to_crs(5179)`)으로 geometry를 만듦, 변수/컬럼명 관례만 다름. 병합 노트북에서는 NB2가 새로 디스크에서 읽지 말고 NB1이 이미 만든 `gdf_bus`/`gdf_sub`를 그대로 이어받게 할 것 (지금은 커널 세션이 분리돼서 어쩔 수 없이 다시 읽는 것뿐).
5. **`sjoin(..., predicate="within")` 패턴이 용도만 바꿔 반복 사용됨** — NB1은 동별 *개수 집계*에 두 번 씀([41],[50]); NB2는 지도 표시용 *필터링*에 두 번 씀([27],[32]). 같은 기법, 다른 활용 — 완전 중복은 아니지만 "같은 도구, 다른 용도"로 한 번만 가르치고 두 번째는 참조만 하면 됨.
6. **공간 오버레이 로직이 개념적으로 반복됨.** NB1이 Union/Intersection/Difference를 명시적으로 가르치고([76]) 버퍼-union-difference로 커버/비커버 폴리곤을 만듦. NB2 4강은 같은 개념(`.intersects()`, `.intersection().area` 비율)을 인구격자-비커버폴리곤, 격자-검색반경 가중에 재사용([74]-[75], [81]-[82]). 완전 반복은 아니지만, 병합판에서는 새로 유도하지 말고 NB1의 Union/Intersection/Difference 설명을 명시적으로 다시 참조하게 할 것.
7. **NB2 내부에서 Folium 지도 생성 보일러플레이트가 반복됨** (노트북 간 중복은 아니지만 "섹션당 작업량" 참고용): cell [30], [33], [35], [55]가 각각 레이어 하나씩 늘려가며(버스→+지하철→+따릉이→+경로) 거의 동일한 ~40줄짜리 지도 생성 블록을 4번 반복. 히로시마판 재작성 시 점진적 빌드나 헬퍼 함수로 합칠 후보.
8. **사소한 중복**: 두 노트북 다 상단에서 `BASE_DIR`/`DATA_DIR`/`OUT_DIR` 보일러플레이트(NB1 [8], NB2 [8], 동일 패턴); 둘 다 노트북 중간에 `%pip install ...`을 흩어놓음(NB1: geopandas [3], folium [99]; NB2: osmnx [1], lonboard [59]) — 병합 시 한 곳으로 모을 것.

---

## 5. 셀 구성 요약 (최상위 `###` 섹션 기준)

**NB1** — 13개 최상위 섹션, code 85 / markdown 22:
인트로/Pandas-GeoPandas 3c/2m · 폴더구조 1c/2m · 유틸함수 4c/1m · Shp전처리 8c/1m · CSV전처리 12c/1m · 버스지하철집계 14c/2m · 병합/파생지표 9c/2m · EDA 4c/3m · **커버리지분석(최대, 24c/4m)** · Folium차이 4c/1m · 과업의한계 1c/1m · 다중공선성 1c/1m

**NB2** — 최상위 `###`는 3개뿐(대부분 `####` 레벨), code 73 / markdown 24:
[3강]인트로 2c/3m · **"GeoPandas/Folium차이" 우산블록, 데이터로드부터 라우팅파이프라인 전체 포함(최대, 39c/12m)** · [4강]pydeck/lonboard시뮬레이션 32c/9m

3강의 라우팅/네트워크분석(대략 cell 36–55)과 4강의 인구격자/lonboard 시뮬레이션(cell 62–96)이 NB2에서 가장 크고 독창적인 부분 — NB1엔 대응물이 없고, 히로시마 대응 데이터(히로시마 도보망, 히로시마 인구격자 shapefile로 `nlsp_021001001.shp` 대체)로 바꿀 때 가장 손이 많이 갈 곳.

---

## 참고: 조사 중 발견된 것 (요청 범위 밖이지만 관련 있음)

`outputs/`에 `BND_ADM_DONG_PG_TOP5_SEOUL.gpkg`가 있고, `data/`에
`BND_ADM_DONG_SEOUL.parquet`(Task 3에서 만든 것, app.py용 — 이건 알려진 파일)가
있는데, 둘 다 위 두 노트북 어디서도 참조되지 않음. `BND_ADM_DONG_PG_TOP5_SEOUL.gpkg`는
이번 세션 이전부터 있던 것으로 보임 — 정체 확인 필요하면 다음에 볼 것.
