# Hiroshima 공간분석 발표 패키지

이 저장소는 **바이브 코딩으로 공간분석 기능을 이해하고, 데이터 분석으로 인사이트를 도출하는 과정**을 발표하기 위한 패키지다. 히로시마 교통 접근성은 공간분석 흐름을 설명하기 위한 사례이며, 핵심은 다른 도시에도 재사용할 수 있는 분석 패턴이다.

## 발표 자료

- `hiroshima_presentation/hiroshima_presentation.ipynb`: 전체 실습 노트북. 질문 설정 → 공간 데이터 준비 → 공간 연산 → 네트워크 분석 → 시각화·우선순위화의 흐름을 포함한다.
- `hiroshima_presentation/presentation_script.md`: 발표용 스토리와 강조 포인트.
- `hiroshima_presentation/data/hiroshima/`: 발표 실행에 필요한 행정구역·인구·정류장·지도 데이터.
- `hiroshima_presentation/outputs/`: 분석 결과 지도, 후보지 및 중간 산출물.

## 실행

```powershell
cd hiroshima_presentation
python -m pip install -r requirements.txt
jupyter notebook hiroshima_presentation.ipynb
```

원본 프로젝트 파일과 연구용 자료는 로컬 작업공간에 보존되어 있으며, GitHub에는 발표에 필요한 `hiroshima_presentation/`와 이 README만 게시한다.
