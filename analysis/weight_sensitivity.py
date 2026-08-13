"""Test how stable the lecture-2 Top 5 is under different indicator weights.
2강 Top5가 지표 가중치 변화에 얼마나 안정적인지 검증한다.

The lecture fixes W_POP = W_UNC = W_BUS = 0.33 without justifying the choice.
Equal weighting is a modelling decision, not a neutral default - so the honest
question is whether the answer survives other defensible choices.
2강은 W_POP = W_UNC = W_BUS = 0.33을 근거 없이 고정한다. 균등 가중은
중립적 기본값이 아니라 하나의 모델링 결정이므로, 다른 타당한 선택에서도
결론이 유지되는지 확인하는 것이 정직한 질문이다.

Reads the reproduced baseline written by reproduce_ranking.py.
reproduce_ranking.py가 저장한 재현 기준선을 읽는다.
"""
import os
import sys
from collections import Counter

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
BASELINE = os.path.join(HERE, "ranking_baseline.csv")

STEP = 0.05   # weight grid resolution / 가중치 격자 해상도
TOP_N = 5

LECTURE_TOP5 = {
    "11210540": "청림동",
    "11210630": "남현동",
    "11110640": "중계4동",
    "11250630": "천호3동",
    "11200660": "사당4동",
}


def main():
    df = pd.read_csv(BASELINE, encoding="utf-8-sig")
    df["region_id"] = (pd.to_numeric(df["region_id"], errors="coerce")
                       .astype("Int64").astype(str))

    comps = df[["pop_norm", "unc_norm", "bus_sub_inv_norm"]].to_numpy()
    labels = (df["region_nm"].astype(str) + " (" + df["region_id"] + ")").tolist()

    # Enumerate every weight triple on a simplex grid.
    # 단체(simplex) 격자 위의 모든 가중치 조합을 나열한다.
    steps = int(round(1.0 / STEP))
    combos = [
        (i / steps, j / steps, (steps - i - j) / steps)
        for i in range(steps + 1)
        for j in range(steps + 1 - i)
    ]

    appearances = Counter()
    rank1 = Counter()

    for w_pop, w_unc, w_bus in combos:
        score = comps @ np.array([w_pop, w_unc, w_bus])
        order = np.argsort(-score)[:TOP_N]
        for k in order:
            appearances[labels[k]] += 1
        rank1[labels[order[0]]] += 1

    n = len(combos)
    print("=" * 78)
    print(f"WEIGHT SENSITIVITY - {n} weight combinations, step {STEP}")
    print(f"가중치 민감도 - {n}개 조합, 간격 {STEP}")
    print("=" * 78)

    print(f"\ndistinct dongs that enter the Top{TOP_N} at least once / "
          f"한 번이라도 Top{TOP_N}에 든 행정동 수: {len(appearances)}")
    print(f"distinct dongs that reach rank 1 / 1위에 오른 행정동 수: {len(rank1)}")

    print(f"\n--- Most frequent Top{TOP_N} members / 최다 진입 ---")
    for name, cnt in appearances.most_common(12):
        print(f"  {name:<24} {cnt:>5} / {n}  ({100*cnt/n:5.1f}%)")

    print("\n--- Dongs that reach rank 1 / 1위 도달 ---")
    for name, cnt in rank1.most_common(10):
        print(f"  {name:<24} {cnt:>5} / {n}  ({100*cnt/n:5.1f}%)")

    print(f"\n--- How the lecture's Top5 hold up / 2강 Top5의 견고성 ---")
    for rid, nm in LECTURE_TOP5.items():
        key = f"{nm} ({rid})"
        cnt = appearances.get(key, 0)
        print(f"  {nm:<8} in Top{TOP_N} for {cnt:>5} / {n} combinations "
              f"({100*cnt/n:5.1f}%)")

    out = os.path.join(HERE, "weight_sensitivity.csv")
    pd.DataFrame(
        [{"region": k, "top5_count": v, "share": v / n}
         for k, v in appearances.most_common()]
    ).to_csv(out, index=False, encoding="utf-8-sig")
    print(f"\nSaved / 저장: {out}")


if __name__ == "__main__":
    main()
