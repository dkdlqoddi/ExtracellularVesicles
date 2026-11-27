# 결과물 파일 정리

`Code/`의 노트북 01~08과 `Code/Appendix/`의 부록 노트북·스크립트가 만드는 결과 파일을 정리한 문서입니다.

- 파일로 저장되는 결과는 23개, 약 319 MB입니다.
- 그 밖의 그림과 표는 노트북 안에만 저장됩니다.
- 노트북들이 서로의 결과를 정해진 경로에서 읽으므로 파일 위치를 옮기면 안 됩니다.

## 한눈에 보기

크기는 저장소에 커밋된 원본 기준입니다. 가운데 열은 그 파일을 만든 노트북 번호이고, 마지막 열은 파이프라인을 처음부터 다시 실행해 얻은 파일을 원본과 비교한 결과입니다([재실행 비교](#재실행-비교)).

```text
ExtracellularVesicles/
├── Data/
│   ├── Curated/                                          ── 정제된 EV 단백질 목록 · 프로테옴 특징 행렬 (65M)
│   │   ├── VPEC_all.csv                            253K  01  동일
│   │   ├── VP_Isolation_filter.csv                 271K  01  동일
│   │   ├── VP_pre2014_mapped.csv                   367K  01  동일
│   │   ├── Isolation_methods_filtered.txt          1.3K  01  동일
│   │   ├── Low_confidence_EV_proteins.txt           68K  01  동일
│   │   ├── High_confidence_EV_proteins.txt          22K  01  줄 순서만 다름
│   │   ├── features_human_proteome.csv              35M  02  값 차이 ≤5e-15
│   │   ├── features_human_proteome_MS_filter.csv    30M  02  값 차이 ≤5e-15
│   │   └── EV_proteins.txt                          41K  03  동일
│   ├── Training/                                         ── 학습 데이터셋 3종 (53M)
│   │   ├── training_data_no_filter.csv              19M  03  값 차이 ≤5e-15
│   │   ├── training_data_MS_filter.csv              15M  03  값 차이 ≤5e-15
│   │   └── training_data_MS_iso_filter.csv          18M  03  값 차이 ≤5e-15
│   ├── MS_iso_filter_P_values.csv                  5.0K  04  동일
│   └── Feature_summary.csv                         8.6K  06  동일
├── Models/                                               ── 랜덤 포레스트 모델 6개 + 스케일러 (200M)
│   ├── EV_RF_model_no_filter.pkl                    38M  05  트리 동일, 바이트만 다름
│   ├── EV_RF_model_MS_filter.pkl                    28M  05  트리 동일, 바이트만 다름
│   ├── EV_RF_model_MS_iso_filter.pkl                30M  05  트리 동일, 바이트만 다름
│   ├── EV_RF_model_no_filter_seq.pkl                42M  05  트리 동일, 바이트만 다름
│   ├── EV_RF_model_MS_filter_seq.pkl                30M  05  트리 동일, 바이트만 다름
│   ├── EV_RF_model_MS_iso_filter_seq.pkl            32M  05  트리 동일, 바이트만 다름
│   └── EV_scaler_MS_iso_filter.pkl                 2.1K  05  동일
└── Code/
    ├── 01~08_*.ipynb                                     ── 그림·표는 노트북 안에 저장 (아래 '노트북 안에만 있는 결과')
    └── Appendix/
        ├── EVpedia.ipynb, RandomModel.ipynb              ── 그림은 노트북 안에 저장
        ├── FI_Random_model.csv                     2.9K  RandomModel.ipynb   동일
        └── Combined_AUC_filter_crossval.png        329K  RandomForest_CV.py  글꼴만 다름
```

## 파일 설명

### `Data/Curated/`: 정제된 EV 단백질 목록과 프로테옴 특징 행렬

| 파일 | 노트북 | 내용 |
|---|---|---|
| [VPEC_all.csv](Data/Curated/VPEC_all.csv) | 01 | 일반 EV 데이터셋. Vesiclepedia와 ExoCarta를 합친 EV 단백질 11,952개 (Entrez ID, 유전자 기호, 등장 횟수, UniProt ID) |
| [VP_Isolation_filter.csv](Data/Curated/VP_Isolation_filter.csv) | 01 | 엄격한 EV 데이터셋. 분리 방법으로 거른 Vesiclepedia EV 단백질 6,678개 |
| [VP_pre2014_mapped.csv](Data/Curated/VP_pre2014_mapped.csv) | 01 | 2014년 이전 연구에서 검출된 Vesiclepedia EV 단백질 9,988개 |
| [Isolation_methods_filtered.txt](Data/Curated/Isolation_methods_filtered.txt) | 01 | 엄격한 EV 데이터셋을 만들 때 인정한 분리 방법 조합 18개 |
| [Low_confidence_EV_proteins.txt](Data/Curated/Low_confidence_EV_proteins.txt) | 01 | 저신뢰 EV 단백질 UniProt ID 9,988개 (`VP_pre2014_mapped.csv`의 ID) |
| [High_confidence_EV_proteins.txt](Data/Curated/High_confidence_EV_proteins.txt) | 01 | 고신뢰 EV 단백질 UniProt ID 3,243개. `Data/Validation/Raw/`에 있는 고품질 EV 연구 3편(혈장·소변·세포 배양)의 합집합 |
| [features_human_proteome.csv](Data/Curated/features_human_proteome.csv) | 02 | 인간 프로테옴 단백질 20,381개 × 특징 93개 (`id`, `fasta_sequence` 열 포함) |
| [features_human_proteome_MS_filter.csv](Data/Curated/features_human_proteome_MS_filter.csv) | 02 | 위 행렬에서 ProteomicsDB 기준으로 질량분석(MS) 검출이 가능한 단백질 16,790개만 남긴 것 |
| [EV_proteins.txt](Data/Curated/EV_proteins.txt) | 03 | 논문 discovery 데이터셋의 EV 단백질 UniProt ID 5,965개 |

같은 폴더의 `EV_proteins_Entrez_to_Uniprot.tsv`는 결과물이 아니라 입력 파일(Entrez → UniProt ID 변환표)입니다.

### `Data/Training/`: 학습 데이터셋 (03)

세 파일 모두 열은 `id`, `EV`(1 = EV 단백질, 0 = 비EV 단백질), 특징 93개입니다. EV 목록에 있는 단백질은 EV로, 나머지 프로테옴은 비EV로 표시했습니다. EV 데이터베이스에 2번 이하로만 등장한 단백질은 애매하다고 보고 뺐습니다.

| 파일 | 구성 | 단백질 | EV / 비EV |
|---|---|---:|---:|
| [training_data_no_filter.csv](Data/Training/training_data_no_filter.csv) | 일반 EV 데이터셋 × 전체 프로테옴 | 16,929 | 8,408 / 8,521 |
| [training_data_MS_filter.csv](Data/Training/training_data_MS_filter.csv) | 일반 EV 데이터셋 × MS 검출 가능 프로테옴 | 13,709 | 8,198 / 5,511 |
| [training_data_MS_iso_filter.csv](Data/Training/training_data_MS_iso_filter.csv) | 엄격한 EV 데이터셋 × MS 검출 가능 프로테옴 (논문의 discovery 데이터셋) | 16,255 | 5,965 / 10,290 |

### `Data/`: 특징 통계 요약

| 파일 | 노트북 | 내용 |
|---|---|---|
| [MS_iso_filter_P_values.csv](Data/MS_iso_filter_P_values.csv) | 04 | discovery 데이터셋에서 특징 93개를 EV와 비EV로 나눠 비교한 p-value와 FDR 보정 p-value. 연속형 특징은 Mann-Whitney U, 범주형 특징은 Fisher 정확 검정 |
| [Feature_summary.csv](Data/Feature_summary.csv) | 06 | 특징 93개별 보정 p-value, EV 클래스와의 상관계수, 학습 모델과 무작위 모델의 특징 중요도. 학습 모델은 `EV_RF_model_MS_iso_filter` |

### `Models/`: 랜덤 포레스트 모델 (05)

- 모든 모델은 `RandomForestClassifier(n_estimators=1000, max_features=10, random_state=0)`입니다.
- 다수 클래스를 언더샘플링해 EV와 비EV를 1:1로 맞춘 뒤 80%로 학습하고 20%는 테스트용으로 남겼습니다. 연속형 특징은 RobustScaler로 스케일링했습니다.
- `_seq` 모델은 서열에서 계산하거나 예측한 특징 75개만 씁니다. 나머지 모델은 여기에 데이터베이스 주석 특징 18개(UniProt·PhosphoSitePlus 등의 PTM 주석, HSP, 막관통 주석)를 더한 93개를 씁니다.

| 파일 | 학습 데이터 | 특징 수 | 학습 / 테스트 |
|---|---|---:|---:|
| EV_RF_model_no_filter.pkl | no_filter | 93 | 13,452 / 3,364 |
| EV_RF_model_no_filter_seq.pkl | no_filter | 75 | 13,452 / 3,364 |
| EV_RF_model_MS_filter.pkl | MS_filter | 93 | 8,817 / 2,205 |
| EV_RF_model_MS_filter_seq.pkl | MS_filter | 75 | 8,817 / 2,205 |
| EV_RF_model_MS_iso_filter.pkl | MS_iso_filter | 93 | 9,544 / 2,386 |
| EV_RF_model_MS_iso_filter_seq.pkl | MS_iso_filter | 75 | 9,544 / 2,386 |

`EV_scaler_MS_iso_filter.pkl`은 MS_iso_filter 학습 데이터에 맞춘 RobustScaler로, 08에서 씁니다. 모델은 gzip으로 압축한 pickle이고 스케일러는 일반 pickle입니다. scikit-learn 1.0.1로 저장돼 있어 1.3 이상에서는 열리지 않습니다.

```python
import gzip, pickle

with gzip.open("Models/EV_RF_model_MS_iso_filter.pkl", "rb") as f:
    rf = pickle.load(f)
with open("Models/EV_scaler_MS_iso_filter.pkl", "rb") as f:
    scaler = pickle.load(f)
```

### `Code/Appendix/`: 부록 결과

| 파일 | 만든 곳 | 내용 |
|---|---|---|
| [FI_Random_model.csv](Code/Appendix/FI_Random_model.csv) | RandomModel.ipynb | 라벨을 섞어 학습한 무작위 모델의 특징 중요도(93개). 06이 학습 모델과 비교할 때 읽음 |
| [Combined_AUC_filter_crossval.png](Code/Appendix/Combined_AUC_filter_crossval.png) | RandomForest_CV.py | 데이터셋 3종 × (전체 특징 / 서열 기반 특징)의 5-fold 교차검증 ROC 곡선과 AUC |

## 노트북 안에만 있는 결과

아래 그림과 표는 별도 파일로 저장되지 않고 노트북 출력으로만 남아 있습니다.

| 노트북 | 그림 | 내용 |
|---|---:|---|
| [01_DataCuration](Code/01_DataCuration.ipynb) | 2 | 일반·엄격한 EV 데이터셋 비교 벤 다이어그램, 상위 EV 단백질 기능 농축 분석 |
| [02_FeatureGeneration_Human_Proteome](Code/02_FeatureGeneration_Human_Proteome.ipynb) | – | 특징 CSV만 저장 |
| [03_DatasetGeneration_ML_EV](Code/03_DatasetGeneration_ML_EV.ipynb) | 2 | EV 데이터셋과 프로테옴의 겹침, 저빈도 단백질 제거 후 EV·비EV 수 |
| [04_FeatureAnalysis_EV](Code/04_FeatureAnalysis_EV.ipynb) | 11 | 특징 상관, PTM·도메인 막대그래프, 물리화학·구조 특징 바이올린 플롯, MS 필터 전후 분자량 분포 |
| [05_RandomForestTraining_ML](Code/05_RandomForestTraining_ML.ipynb) | – | 모델 파일만 저장 |
| [06_RandomForestAnalysis_ML](Code/06_RandomForestAnalysis_ML.ipynb) | 14 | 모델 성능(전체·서열 기반 특징, 모델 비교), 특징 중요도, 중요도와 상관 비교, 중요도 순위 |
| [07_Validation](Code/07_Validation.ipynb) | 4 | 고·저신뢰 EV 세트 비교 바이올린 플롯 2개, 막대그래프 2개 |
| [08_CaseStudy](Code/08_CaseStudy.ipynb) | 4 | TP·FN·TN·FP 사례별 SHAP force plot, 사례를 고르는 데 쓴 예측 확률 표 5개 |
| [Appendix/EVpedia](Code/Appendix/EVpedia.ipynb) | 3 | EVpedia 비교 벤 다이어그램 2개, 그래프 1개 |
| [Appendix/RandomModel](Code/Appendix/RandomModel.ipynb) | 2 | 무작위 모델의 성능과 특징 중요도 |

08의 SHAP 그림은 JavaScript로 그려지기 때문에 GitHub 미리보기에서는 보이지 않습니다. Jupyter에서 열어야 보입니다.

## 재실행 비교

2026년 11월 27일에 Linux(WSL2)에서 아래 [재현 조건](#재현-조건)으로 모든 노트북과 스크립트를 처음부터 다시 실행하고, 새로 만들어진 파일을 커밋된 원본과 비교했습니다. 다시 만든 파일은 커밋하지 않았으므로 저장소의 결과 파일은 모두 저자 원본입니다.

| 표시 | 파일 수 | 의미 |
|---|---:|---|
| 동일 | 10 | 원본과 바이트까지 같음 |
| 줄 순서만 다름 | 1 | ID 3,243개는 같고 순서만 다름. 01이 파이썬 set을 그대로 저장해서 실행할 때마다 순서가 바뀜 |
| 값 차이 ≤5e-15 | 5 | 부동소수점 끝자리만 다름. 이 파일로 다시 학습한 모델이 원본과 같으므로 이후 결과에 영향 없음 |
| 트리 동일, 바이트만 다름 | 6 | 1,000개 트리와 예측 확률이 원본과 같고, 저장된 pickle 바이트만 다름 |
| 글꼴만 다름 | 1 | 그림 내용은 같고 글꼴만 다름 |

노트북에 저장된 텍스트 출력(단백질 수, p-value, 성능 지표 등)도 빈 줄 차이를 빼면 원본과 같았습니다.

## 결과물이 아닌 파일

아래 입력 데이터는 실행 중에 바뀌지 않습니다. 자세한 설명은 [Data/README.md](Data/README.md)에 있습니다.

- `Data/Raw/`: Vesiclepedia, ExoCarta, EVpedia 원본 데이터
- `Data/Features/`: NetSurfP-2.0, UniProt, PhosphoSitePlus, PROSITE, TMHMM 등 특징 원자료
- `Data/ProteomicsDB/`: 단백질별 질량분석 검출 근거
- `Data/Validation/Raw/`: 고신뢰 EV 세트를 만드는 데 쓴 연구 3편의 데이터
- `Data/Curated/EV_proteins_Entrez_to_Uniprot.tsv`: Entrez → UniProt ID 변환표

## 재현 조건

위 비교에 쓴 환경입니다.

- 패키지: Python 3.8.20, numpy 1.21.6, pandas 1.3.5, scipy 1.6.3, scikit-learn 1.0.1, imbalanced-learn 0.8.1, statsmodels 0.13.5, biopython 1.79, shap 0.41.0, numba 0.56.4, matplotlib 3.5.3, seaborn 0.11.2, gseapy 0.14.0, matplotlib-venn 0.11.10
  - scikit-learn 1.3 이상은 `Models/`의 pickle을 열지 못합니다.
  - scipy 1.7부터 `mannwhitneyu`의 기본값이 양측 검정으로 바뀌어, 04의 p-value가 원본(단측 값)과 달라집니다.
  - 최신 numba는 numpy 1.22 이상이 필요해서, numba를 0.56.4로 고정해야 shap을 불러올 수 있습니다.
- 경로: 노트북은 `Data/raw`처럼 소문자 경로를 쓰지만 실제 폴더 이름은 대문자로 시작합니다(Windows에서 작성됨). Linux에서는 심볼릭 링크를 만들어야 합니다.

  ```bash
  cd Data
  ln -s Raw raw; ln -s Curated curated; ln -s Training training; ln -s Features features; ln -s Validation validation
  ln -s Raw Validation/raw; ln -s UniProt Features/Uniprot
  ```

- 02 수정: PROSITE 파일 목록을 정렬하는 수정(커밋 `a9d938c`)이 있어야 Linux에서도 특징 열 순서가 원본과 같아지고, 모델이 원본과 똑같이 학습됩니다.
- 실행 순서: 01 → 02 → 03 → 04 → `Appendix/RandomModel` → 05 → 06 → 07 → 08. `Appendix/EVpedia`는 05 다음, `Appendix/RandomForest_CV.py`는 03 다음이면 언제 실행해도 됩니다. 노트북은 자기 폴더에서 실행해야 경로가 맞습니다.

  ```bash
  (cd Code && jupyter nbconvert --to notebook --execute --inplace 01_DataCuration.ipynb)
  (cd Code/Appendix && MPLBACKEND=Agg python RandomForest_CV.py)
  ```
