# 발표 컨셉

## 바이브 코딩으로 이해하는 공간분석과 데이터 인사이트
## Understanding Spatial Analysis and Data Insights through Vibe Coding

이 발표는 히로시마의 교통지도를 보여주는 데서 끝나지 않는다. 자연어로 공간 질문을 만들고, 바이브 코딩으로 필요한 분석 기능을 빠르게 조합하고, 결과를 지도와 수치로 검증해 인사이트로 발전시키는 과정을 보여준다.

This presentation goes beyond showing a transportation map of Hiroshima. It demonstrates how to turn a natural-language spatial question into a working analysis, combine spatial functions through vibe coding, validate results with maps and numbers, and develop them into insights.

## 1. 출발점: 공간 질문 만들기
## 1. Starting point: Formulating a spatial question

“정류장이 많은 지역이 정말 교통 접근성이 좋은가?”, “인구를 고려하면 어디가 비어 있는가?”, “직선거리와 실제 보행거리는 얼마나 다른가?”처럼 관찰 가능한 질문에서 시작한다. 질문이 명확해야 필요한 데이터와 공간분석 기능을 선택할 수 있다.

We start with observable questions: “Do areas with many stops actually have good access?”, “Where are the gaps after accounting for population?”, and “How different are straight-line and walking distances?” A clear question determines which data and spatial functions are needed.

## 2. 바이브 코딩으로 분석 기능 탐색하기
## 2. Exploring analytical functions through vibe coding

바이브 코딩은 코드를 무비판적으로 생성하는 것이 아니다. AI에게 분석 의도를 자연어로 설명하고, GeoPandas·OSMnx·pydeck/deck.gl 같은 기능을 조합해 빠르게 실행한다. 이후 좌표계, 조인 결과, 지도 모양, 결측치와 예외를 직접 확인하며 코드를 고친다.

Vibe coding is not uncritical code generation. We describe the analytical intent in natural language, combine tools such as GeoPandas, OSMnx, and pydeck/deck.gl, run quickly, and then inspect coordinate systems, join results, map shapes, missing values, and exceptions to refine the code.

## 3. 기능이 인사이트로 바뀌는 과정
## 3. Turning functions into insights

1. `GeoPandas + CRS + spatial join`: 원자료를 공간 단위별 분석 테이블로 만든다.  
   `GeoPandas + CRS + spatial join`: Convert raw files into an analysis table by spatial unit.
2. `buffer + overlay`: 정류장 주변 서비스 범위와 미도달 영역을 구분한다.  
   `buffer + overlay`: Separate service areas around stops from uncovered areas.
3. `OSMnx + shortest path`: 직선거리가 아닌 실제 보행 네트워크 접근성을 계산한다.  
   `OSMnx + shortest path`: Measure accessibility on the real walking network rather than a straight line.
4. `pydeck/deck.gl`: 인구를 높이로, 취약성을 색으로, 정류장과 경로를 점·선으로 표현하며 가설을 탐색한다.  
   `pydeck/deck.gl`: Use height for population, colour for vulnerability, and points and paths for stops and routes while exploring hypotheses.

## 4. deck.gl 시각화로 질문을 탐색하기
## 4. Exploring questions with deck.gl visualizations

정적 지도는 결과 검증에, deck.gl은 가설 탐색에 사용한다. 시각 문법은 모든 지도에서 동일하다. 폴리곤은 공간 맥락, 색은 정규화 지표, 높이는 규모, 선은 이동, 점은 관측값이나 후보 위치를 나타낸다. 넓은 배경 레이어를 먼저 그리고 경로·외곽선·마커를 나중에 그려 중요한 정보가 가려지지 않게 한다.

Static maps support verification; deck.gl supports hypothesis exploration. Every view uses the same visual grammar: polygons provide spatial context, colour shows a normalized indicator, height shows magnitude, paths show movement, and points mark observations or candidate locations. Broad context layers are drawn first and routes, outlines, and markers last so important information remains visible.

1. 인구·공급 지도: 높이는 인구, 빨강→청록은 인구 1만 명당 버스 공급 부족→충분을 뜻한다. 높고 붉은 블록을 먼저 찾는다.
   - Population and supply: height is population; red→teal is low→high bus supply per 10,000 residents. Look first for tall red blocks.
2. 사각지대 지도: 노랑→빨강은 미커버 비율, 청록 외곽선은 취약성 상위 5개 지역이다.
   - Blind spots: yellow→red is uncovered share; cyan outlines identify the five highest vulnerability scores.
3. 보행 경로 지도: 청록은 버스정류장 경로, 자홍은 역 경로이며 어두운 외곽선이 중첩 경로를 분리한다.
   - Walking routes: cyan leads to bus stops, magenta to stations, and a dark casing separates overlaps.
4. 3D 후보지역 지도: 높이와 순차색은 탐색 반경 내 유효 인구, 흰색 링은 탐색 범위, 중심 마커는 선택 후보를 나타낸다.
   - 3D candidate view: height and sequential colour show effective population, the white ring shows the search radius, and the centre marker shows the selected candidate.

## 5. 히로시마 사례에서 읽는 인사이트
## 5. Insights from the Hiroshima case

단순 정류장 수만 보면 공급이 충분해 보이는 지역도 인구 규모와 서비스 범위를 함께 보면 취약할 수 있다. 직선거리 결과는 도로망·하천·철도 같은 장벽을 반영하지 못한다. 최종 후보지는 시설 수 하나가 아니라 인구, 미도달 면적, 보행거리, 기존 공급을 함께 고려해 해석한다.

An area can appear well supplied when we count stops alone but become vulnerable after considering population and service coverage. Straight-line results do not reflect barriers such as roads, rivers, or railways. Candidate locations should therefore be interpreted using population, uncovered area, walking distance, and existing supply together.

## 6. 발표에서 강조할 검증 포인트
## 6. Validation points to emphasize

- CRS가 도 단위인지 미터 단위인지 확인한다.  
  Confirm whether the CRS uses degrees or metres.
- spatial join과 overlay 이후 행 수·면적·중복을 점검한다.  
  Check row counts, areas, and duplicates after spatial joins and overlays.
- deck.gl에서 보이는 패턴이 수치 결과와 일치하는지 확인한다.  
  Confirm that patterns visible in deck.gl agree with the numerical results.
- 네트워크 분석 실패와 데이터 누락을 숨기지 않고 기록한다.  
  Record network failures and missing data instead of hiding them.
- 다른 도시 데이터로 바꿔 끼워도 재현되는지 확인한다.  
  Check whether the workflow remains reproducible with data from another city.

## 결론
## Conclusion

공간분석에서 중요한 것은 특정 라이브러리의 문법을 암기하는 것이 아니다. 질문에 맞는 기능을 선택하고, 빠르게 시도하고, 공간적으로 검증하고, 데이터의 한계를 밝히면서 인사이트를 만드는 능력이다. 히로시마는 그 과정을 보여주는 사례이며, 최종 목표는 어디서든 다시 쓸 수 있는 분석 패턴이다.

Spatial analysis is not about memorizing the syntax of a particular library. It is about selecting functions that fit the question, trying them quickly, validating them spatially, acknowledging data limits, and creating insights. Hiroshima is a case for demonstrating that process; the real goal is a reusable analytical pattern.
