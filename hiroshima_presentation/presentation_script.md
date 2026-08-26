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

정적 지도는 결과를 확인하는 데 쓰고, deck.gl은 결과를 탐색하는 인터페이스로 사용한다. 인구 압출 지도는 “사람이 많은 곳에 공급이 있는가?”를, 사각지대 레이어는 “미도달 영역이 어디에 남는가?”를, PathLayer는 “실제 보행 경로가 얼마나 우회하는가?”를 보여준다.

We use static maps to verify results and deck.gl as an exploratory interface. The population extrusion map asks whether supply follows people, the blind-spot layer shows where uncovered space remains, and the PathLayer reveals how much real walking detours.

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
