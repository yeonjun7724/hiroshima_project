# Hiroshima 발표용 분석 패키지

이 저장소는 실제 발표에 사용할 자료를 `hiroshima_presentation/` 폴더에 모아둔 독립 패키지입니다.

## 발표 순서

1. `hiroshima_presentation/hiroshima_presentation.ipynb`를 실행해 데이터와 분석 방법을 설명합니다.
2. `hiroshima_presentation/outputs/01_bus_supply.png`에서 공급량 분포를 보여줍니다.
3. `hiroshima_presentation/outputs/02_priority_areas.png`와 `top10_priority_areas.csv`에서 신규 교통시설 후보를 설명합니다.
4. `hiroshima_presentation/presentation_script.md`를 발표 대본으로 사용합니다.

## 실행

```powershell
cd hiroshima_presentation
python -m pip install -r requirements.txt
jupyter notebook hiroshima_presentation.ipynb
```

인터넷 연결 없이도 1차 분석과 지도 출력은 실행됩니다. 보행 네트워크 분석은 기존 `outputs/hiroshima_routes_all.gpkg` 결과를 참고용으로 포함했습니다.

## 포함 데이터

- `data/hiroshima_city_admin.gpkg`: 히로시마시 소지역 경계와 분석에 사용한 기준 인구
- `data/hiroshima_chome_population_2026_07.csv`: 히로시마시 공식 2026년 7월 町丁目별 인구 CSV
- `data/hiroshima_gtfs_stops_all.gpkg`: 히로시마현 GTFS-JP 6개 사업자 정류장 통합본
- `data/hiroshima_transport_jr.csv`, `data/hiroshima_transport_astramline.csv`: 역 원본 CSV
- `data/hiroshima_alternative_stations.gpkg`: JR·Astram 역 대체 데이터

## 출처와 주의점

- 인구: [히로시마시 町丁目別人口・世帯数](https://www.city.hiroshima.lg.jp/shisei/toukei/1027844/1027845/1027846/1038151/index.html)
- 버스: [히로시마현 버스협회 GTFS 오픈데이터](https://www.bus-kyo.or.jp/gtfs-open-data)
- 역·교통시설: [G空間정보센터 히로시마시 교통시설](https://www.geospatial.jp/ckan/dataset/34100-010)

노트북의 순위 계산은 `hiroshima_city_admin.gpkg`에 포함된 기준 인구를 사용합니다. 별도 인구 CSV는 최신 공식 월말 자료로 포함했지만, 일부 소지역이 개인정보 보호를 위해 합산될 수 있어 경계와 완전한 1:1 조인이 보장되지 않습니다. 버퍼 기반 접근성은 직선거리 기준이며 실제 도보거리와 다릅니다. `priority_score`의 가중치는 발표용 예시 지표입니다.
