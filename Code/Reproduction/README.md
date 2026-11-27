# 재현 스크립트

이 저장소의 결과를 Linux에서 다시 만들고 저자 원본과 비교할 때 쓴 스크립트입니다. 결과와 환경은 [RESULTS.md](../../RESULTS.md)에 정리돼 있습니다.

모두 [RESULTS.md의 재현 조건](../../RESULTS.md#재현-조건)에 적힌 패키지 환경(scikit-learn 1.0.1 등)의 python으로 실행합니다. 저장소 안이라면 어느 폴더에서 실행해도 됩니다.

| 스크립트 | 하는 일 |
|---|---|
| `compare_nb.py` | 노트북의 텍스트 출력을 다른 커밋(기본값: 저자 원본 `0ddfa23`)과 셀 단위로 비교합니다. |
| `compare_models.py` | `Models/`의 랜덤 포레스트 6개와 스케일러를 다른 커밋(기본값 `0ddfa23`)의 것과 비교합니다. |
| `make_results_html.py` | 노트북과 결과 파일로 `RESULTS.html`과 `Results/figures/`를 다시 만듭니다. |

```bash
python Code/Reproduction/compare_nb.py                 # 노트북 10개 전체
python Code/Reproduction/compare_nb.py Code/06_RandomForestAnalysis_ML.ipynb --show 3
python Code/Reproduction/compare_models.py             # 30초쯤 걸립니다
python Code/Reproduction/make_results_html.py
```

두 비교 스크립트는 모두 일치하면 종료 코드 0을 돌려줍니다. `make_results_html.py`의 파일 설명, 그림 캡션, 파일 이름, AUC 값은 스크립트 안에 직접 적혀 있습니다. 그래서 노트북의 그림 순서나 내용이 바뀌면 이것도 함께 고쳐야 합니다.
