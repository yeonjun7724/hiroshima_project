# Hiroshima Transit Accessibility with Open-Source GIS

> A bilingual, reproducible spatial-analysis tutorial for exploring public-transport accessibility in Hiroshima with GeoPandas, OSMnx, NetworkX, Folium, and pydeck/deck.gl.

> GeoPandas, OSMnx, NetworkX, Folium, pydeck/deck.gl을 이용해 히로시마 대중교통 접근성을 탐색하는 영문·한글 공간분석 튜토리얼입니다.

This repository accompanies a hands-on presentation about designing, testing, and communicating a spatial analysis through vibe coding. Hiroshima is the case study; the reusable outcome is a workflow that moves from raw spatial data to validated accessibility insights.

이 저장소는 바이브 코딩을 활용해 공간분석을 설계하고, 실행 결과를 검증하며, 인사이트를 전달하는 과정을 다루는 실습형 발표 자료입니다. 히로시마는 사례 지역이며, 핵심 결과물은 원시 공간데이터에서 검증 가능한 접근성 인사이트까지 이어지는 재사용 가능한 분석 흐름입니다.

## Analysis workflow / 분석 흐름

1. **Prepare / 데이터 준비** — standardize coordinate reference systems, clean identifiers, and combine administrative boundaries, population, bus stops, and stations.
2. **Measure supply / 공급 측정** — aggregate stops by area and calculate population-normalized indicators.
3. **Measure coverage / 커버리지 측정** — create stop buffers and derive uncovered geometry with overlay operations.
4. **Route on streets / 실제 경로 분석** — use OSMnx and NetworkX to compare straight-line assumptions with walking-network distance.
5. **Prioritize and communicate / 우선순위화·전달** — rank vulnerable areas and explain the result with bilingual Folium and pydeck maps.

## Interactive maps / 인터랙티브 지도

The notebook builds four complementary deck.gl views. Layer order, colour, outline, and tooltip conventions are documented next to each map.

노트북은 서로 다른 질문에 답하는 네 가지 deck.gl 지도를 생성합니다. 레이어 순서, 색상, 외곽선, 툴팁을 읽는 방법은 각 지도 바로 위에 영문과 한글로 설명되어 있습니다.

| Map / 지도 | Visual encoding / 시각 표현 | Analytical question / 분석 질문 |
|---|---|---|
| Population and bus supply / 인구와 버스 공급 | Height = population; red→teal = low→high supply per 10,000 people / 높이=인구, 빨강→청록=1만 명당 공급 부족→충분 | Does supply follow population? / 공급이 인구를 따르는가? |
| Transit blind spots / 교통 사각지대 | Yellow→red = uncovered share; cyan outline = top-five vulnerability / 노랑→빨강=미커버 비율, 청록 외곽선=취약성 상위 5개 | Where are populated coverage gaps? / 인구가 있는 사각지대는 어디인가? |
| Walking routes / 보행 경로 | Cyan = bus routes; magenta = station routes / 청록=버스 경로, 자홍=역 경로 | How different is real walking distance? / 실제 보행거리는 얼마나 다른가? |
| Candidate area in 3D / 3D 후보지역 | Height and sequential colour = effective population; ring = search radius / 높이·순차색=유효 인구, 링=탐색 반경 | Where could a new stop help most? / 새 정류장이 어디에서 가장 도움이 되는가? |

## Repository structure / 저장소 구성

```text
hiroshima_presentation/
├── hiroshima_presentation.ipynb  # Main bilingual tutorial / 메인 영문·한글 튜토리얼
├── presentation_script.md        # Talk narrative / 발표 흐름과 강조점
├── requirements.txt              # Python dependencies / 파이썬 의존성
├── data/hiroshima/               # Packaged input data / 실행용 입력 데이터
└── outputs/                      # Generated maps and layers / 생성 지도·분석 레이어
```

The notebook creates `hiroshima_presentation/cache/` for OSMnx responses and the cached walking graph. The cache is intentionally excluded from Git.

노트북 실행 시 OSMnx 응답과 보행 그래프를 저장하는 `hiroshima_presentation/cache/`가 생성됩니다. 캐시는 Git 추적 대상에서 제외됩니다.

## Quick start / 빠른 실행

Python 3.11 is recommended. Run the notebook from `hiroshima_presentation/` so its relative data paths resolve correctly.

Python 3.11 사용을 권장합니다. 상대 데이터 경로가 올바르게 동작하도록 `hiroshima_presentation/`에서 노트북을 실행하세요.

```powershell
cd hiroshima_presentation
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
jupyter notebook hiroshima_presentation.ipynb
```

macOS/Linux:

```bash
cd hiroshima_presentation
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
jupyter notebook hiroshima_presentation.ipynb
```

Run cells from top to bottom. The first code cell checks required packages and packaged data before the analysis starts.

셀은 위에서 아래로 순서대로 실행하세요. 첫 코드 셀이 분석 시작 전에 필수 패키지와 포함된 데이터 파일을 확인합니다.

## Generated outputs / 생성 결과

- `deck_population_supply.html` — population and bus-stop supply / 인구와 버스정류장 공급
- `deck_transit_blind_spots.html` — uncovered share and vulnerability / 미커버 비율과 취약성
- `deck_walking_routes.html` — walking-network routes / 보행 네트워크 경로
- `hiroshima_3d_population.html` — 3D candidate-area view / 후보지역 3D 지도
- `hiroshima_routes_all.gpkg` — route geometries / 경로 공간데이터
- `top10_priority_areas.csv` — ranked priority areas / 우선지역 순위

Most HTML maps use a hosted Carto basemap and need internet access when viewed. Analysis layers and cached OSMnx data can be reused offline after a successful run.

대부분의 HTML 지도는 Carto 호스팅 배경지도를 사용하므로 열람 시 인터넷 연결이 필요합니다. 한 번 정상 실행한 뒤에는 분석 레이어와 OSMnx 캐시를 오프라인에서 재사용할 수 있습니다.

## Validation principles / 검증 원칙

- Use a projected CRS for distance and area calculations; convert to EPSG:4326 only for web visualization.
- Check key uniqueness, row counts, geometry validity, and unmatched records after spatial joins and overlays.
- Keep routing failures in a CSV instead of silently discarding them.
- Compare numerical summaries with visible map patterns before drawing conclusions.

- 거리·면적 계산에는 투영좌표계를 사용하고 웹 시각화 단계에서만 EPSG:4326으로 변환합니다.
- 공간조인과 오버레이 후 키 유일성, 행 수, geometry 유효성, 미매칭 레코드를 확인합니다.
- 네트워크 경로 실패를 숨기지 않고 CSV로 기록합니다.
- 결론을 내리기 전에 수치 요약과 지도 패턴이 일치하는지 확인합니다.

## Data and attribution / 데이터와 출처

The packaged files combine Hiroshima administrative/population data, public-transport stop data, and OpenStreetMap walking-network data. Consult the notebook commentary and source-layer metadata before reusing the results. OpenStreetMap-derived data is subject to the [Open Database License](https://www.openstreetmap.org/copyright).

포함된 파일은 히로시마 행정구역·인구 데이터, 대중교통 정류장 데이터, OpenStreetMap 보행 네트워크 데이터를 결합합니다. 결과를 재사용하기 전에 노트북 설명과 원본 레이어 메타데이터를 확인하세요. OpenStreetMap 기반 데이터에는 [Open Database License](https://www.openstreetmap.org/copyright)가 적용됩니다.

## Scope / 범위

This is an educational analysis workflow, not an official transport-planning decision model. Buffer distances, walking speed, population allocation, network completeness, and weighting choices should be reviewed before operational use.

이 프로젝트는 교육용 분석 흐름이며 공식 교통계획 의사결정 모델이 아닙니다. 실제 활용 전에는 버퍼 거리, 보행 속도, 인구 배분, 네트워크 완전성, 지표 가중치를 다시 검토해야 합니다.
