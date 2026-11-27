# 노트북 그림

노트북 출력에 들어 있던 그림을 파일로 꺼낸 것입니다. 그림 설명은 [RESULTS.md](../../RESULTS.md)·[RESULTS.html](../../RESULTS.html)과 같습니다.

이 폴더는 [`Code/Reproduction/make_results_html.py`](../../Code/Reproduction/make_results_html.py)가 노트북에서 다시 만듭니다. 실행할 때마다 폴더 전체를 새로 쓰므로 여기에 다른 파일을 두지 마세요.

## 01 · 데이터 정제

노트북: [01_DataCuration.ipynb](../../Code/01_DataCuration.ipynb)

**01-01** 일반 vs 엄격한 EV 데이터셋의 겹침

![01-01 일반 vs 엄격한 EV 데이터셋의 겹침](01_DataCuration/01-01_general_vs_stringent_ev_overlap.png)

**01-02** 상위 EV 단백질의 기능 농축 분석 (KEGG 2019 Human)

![01-02 상위 EV 단백질의 기능 농축 분석 (KEGG 2019 Human)](01_DataCuration/01-02_kegg_enrichment_top_ev_proteins.png)

## 03 · 학습 데이터셋 생성

노트북: [03_DatasetGeneration_ML_EV.ipynb](../../Code/03_DatasetGeneration_ML_EV.ipynb)

**03-01** EV 데이터셋과 인간 프로테옴의 겹침 (데이터셋 3종)

![03-01 EV 데이터셋과 인간 프로테옴의 겹침 (데이터셋 3종)](03_DatasetGeneration_ML_EV/03-01_ev_vs_proteome_overlap.png)

**03-02** 저빈도 단백질 제거 후 EV·비EV 단백질 수

![03-02 저빈도 단백질 제거 후 EV·비EV 단백질 수](03_DatasetGeneration_ML_EV/03-02_ev_counts_after_low_count_removal.png)

## 04 · 특징 분석

노트북: [04_FeatureAnalysis_EV.ipynb](../../Code/04_FeatureAnalysis_EV.ipynb)

**04-01** 특징 간 상관 (히트맵)

![04-01 특징 간 상관 (히트맵)](04_FeatureAnalysis_EV/04-01_feature_correlation_heatmap.png)

**04-02** 특징별 EV 클래스와의 상관

![04-02 특징별 EV 클래스와의 상관](04_FeatureAnalysis_EV/04-02_feature_correlation_with_ev.png)

**04-03** PTM 보유 비율: 팔미토일화·유비퀴틴화·아세틸화·니트로실화

![04-03 PTM 보유 비율: 팔미토일화·유비퀴틴화·아세틸화·니트로실화](04_FeatureAnalysis_EV/04-03_ptm_palmitoylation_ubiquitination_acetylation_nitrosylation.png)

**04-04** PTM 보유 비율: 전체 PTM·메틸화·인산화·당화

![04-04 PTM 보유 비율: 전체 PTM·메틸화·인산화·당화](04_FeatureAnalysis_EV/04-04_ptm_any_methylation_phosphorylation_glycosylation.png)

**04-05** PTM 보유 비율: 프레닐화·미리스토일화·GPI 앵커

![04-05 PTM 보유 비율: 프레닐화·미리스토일화·GPI 앵커](04_FeatureAnalysis_EV/04-05_ptm_prenylation_myristoylation_gpi_anchor.png)

**04-06** coiled coil 보유 비율

![04-06 coiled coil 보유 비율](04_FeatureAnalysis_EV/04-06_coiled_coil.png)

**04-07** 도메인 보유 비율: EGF·RAS·RRM·WW

![04-07 도메인 보유 비율: EGF·RAS·RRM·WW](04_FeatureAnalysis_EV/04-07_domains_egf_ras_rrm_ww.png)

**04-08** 특징 분포: 불안정성 지수·등전점·노출 극성/소수성 잔기 비율

![04-08 특징 분포: 불안정성 지수·등전점·노출 극성/소수성 잔기 비율](04_FeatureAnalysis_EV/04-08_violin_instability_pi_exposed_residues.png)

**04-09** 특징 분포: 알파 나선·베타 시트·턴·무질서도

![04-09 특징 분포: 알파 나선·베타 시트·턴·무질서도](04_FeatureAnalysis_EV/04-09_violin_secondary_structure_disorder.png)

**04-10** 분자량 분포와 MS 필터 효과 (1)

![04-10 분자량 분포와 MS 필터 효과 (1)](04_FeatureAnalysis_EV/04-10_molecular_weight_ms_filter_1.png)

**04-11** 분자량 분포와 MS 필터 효과 (2)

![04-11 분자량 분포와 MS 필터 효과 (2)](04_FeatureAnalysis_EV/04-11_molecular_weight_ms_filter_2.png)

## 06 · 모델 분석

노트북: [06_RandomForestAnalysis_ML.ipynb](../../Code/06_RandomForestAnalysis_ML.ipynb)

**06-01** 테스트 세트 ROC 곡선 · 전체 특징

![06-01 테스트 세트 ROC 곡선 · 전체 특징](06_RandomForestAnalysis_ML/06-01_roc_test_all_features.png)

**06-02** 혼동 행렬 · 전체 특징

![06-02 혼동 행렬 · 전체 특징](06_RandomForestAnalysis_ML/06-02_confusion_matrix_all_features.png)

**06-03** 테스트 세트 ROC 곡선 · 서열 기반 특징

![06-03 테스트 세트 ROC 곡선 · 서열 기반 특징](06_RandomForestAnalysis_ML/06-03_roc_test_sequence_features.png)

**06-04** 혼동 행렬 · 서열 기반 특징

![06-04 혼동 행렬 · 서열 기반 특징](06_RandomForestAnalysis_ML/06-04_confusion_matrix_sequence_features.png)

**06-05** ROC 비교: 전체 특징 vs 서열 기반 특징

![06-05 ROC 비교: 전체 특징 vs 서열 기반 특징](06_RandomForestAnalysis_ML/06-05_roc_all_vs_sequence_features.png)

**06-06** 특징 중요도 · 전체 특징 · no_filter 모델

![06-06 특징 중요도 · 전체 특징 · no_filter 모델](06_RandomForestAnalysis_ML/06-06_importance_all_features_no_filter.png)

**06-07** 특징 중요도 · 전체 특징 · MS_filter 모델

![06-07 특징 중요도 · 전체 특징 · MS_filter 모델](06_RandomForestAnalysis_ML/06-07_importance_all_features_ms_filter.png)

**06-08** 특징 중요도 · 전체 특징 · MS_iso_filter 모델

![06-08 특징 중요도 · 전체 특징 · MS_iso_filter 모델](06_RandomForestAnalysis_ML/06-08_importance_all_features_ms_iso_filter.png)

**06-09** 특징 중요도 · 서열 기반 특징 · no_filter 모델

![06-09 특징 중요도 · 서열 기반 특징 · no_filter 모델](06_RandomForestAnalysis_ML/06-09_importance_sequence_features_no_filter.png)

**06-10** 특징 중요도 · 서열 기반 특징 · MS_filter 모델

![06-10 특징 중요도 · 서열 기반 특징 · MS_filter 모델](06_RandomForestAnalysis_ML/06-10_importance_sequence_features_ms_filter.png)

**06-11** 특징 중요도 · 서열 기반 특징 · MS_iso_filter 모델

![06-11 특징 중요도 · 서열 기반 특징 · MS_iso_filter 모델](06_RandomForestAnalysis_ML/06-11_importance_sequence_features_ms_iso_filter.png)

**06-12** 상위 특징의 중요도와 상관 (데이터셋 3종)

![06-12 상위 특징의 중요도와 상관 (데이터셋 3종)](06_RandomForestAnalysis_ML/06-12_top_features_importance_correlation_3_datasets.png)

**06-13** 상위 특징의 중요도와 상관 (discovery 모델)

![06-13 상위 특징의 중요도와 상관 (discovery 모델)](06_RandomForestAnalysis_ML/06-13_top_features_importance_correlation_discovery.png)

**06-14** 모델별 특징 중요도 순위

![06-14 모델별 특징 중요도 순위](06_RandomForestAnalysis_ML/06-14_importance_rank_by_model.png)

## 07 · 고·저신뢰 EV 세트 검증

노트북: [07_Validation.ipynb](../../Code/07_Validation.ipynb)

**07-01** EV·비EV·고신뢰·저신뢰 비교: 분자량·불안정성 지수·등전점·노출 극성 잔기 비율

![07-01 EV·비EV·고신뢰·저신뢰 비교: 분자량·불안정성 지수·등전점·노출 극성 잔기 비율](07_Validation/07-01_violin_mw_instability_pi_polar_exposed.png)

**07-02** EV·비EV·고신뢰·저신뢰 비교: 알파 나선·베타 시트·턴·무질서도

![07-02 EV·비EV·고신뢰·저신뢰 비교: 알파 나선·베타 시트·턴·무질서도](07_Validation/07-02_violin_secondary_structure_disorder.png)

**07-03** EV·비EV·고신뢰·저신뢰 비교: 팔미토일화·아세틸화·메틸화·니트로실화

![07-03 EV·비EV·고신뢰·저신뢰 비교: 팔미토일화·아세틸화·메틸화·니트로실화](07_Validation/07-03_bar_palmitoylation_acetylation_methylation_nitrosylation.png)

**07-04** EV·비EV·고신뢰·저신뢰 비교: 전체 PTM·유비퀴틴화·당화·인산화

![07-04 EV·비EV·고신뢰·저신뢰 비교: 전체 PTM·유비퀴틴화·당화·인산화](07_Validation/07-04_bar_ptm_ubiquitination_glycosylation_phosphorylation.png)

## 08 · SHAP 사례 분석

노트북: [08_CaseStudy.ipynb](../../Code/08_CaseStudy.ipynb)

SHAP force plot은 JavaScript로 그려지므로 GitHub에서는 보이지 않습니다. 내려받아 브라우저로 여세요.

- [08-01 참양성 (TP) · P46459](08_CaseStudy/08-01_shap_true_positive_P46459.html): 실제 EV, EV로 예측, 예측 확률 0.997
- [08-02 위음성 (FN) · Q14929](08_CaseStudy/08-02_shap_false_negative_Q14929.html): 실제 EV, 비EV로 예측, 예측 확률 0.098
- [08-03 참음성 (TN) · Q14590](08_CaseStudy/08-03_shap_true_negative_Q14590.html): 실제 비EV, 비EV로 예측, 예측 확률 0.019
- [08-04 위양성 (FP) · Q8NHW5](08_CaseStudy/08-04_shap_false_positive_Q8NHW5.html): 실제 비EV, EV로 예측, 예측 확률 0.961

## 부록 · 무작위 모델

노트북: [RandomModel.ipynb](../../Code/Appendix/RandomModel.ipynb)

**RandomModel-01** 무작위 모델의 테스트 세트 ROC 곡선

![RandomModel-01 무작위 모델의 테스트 세트 ROC 곡선](Appendix_RandomModel/RandomModel-01_roc_test.png)

**RandomModel-02** 무작위 모델의 특징 중요도

![RandomModel-02 무작위 모델의 특징 중요도](Appendix_RandomModel/RandomModel-02_feature_importance.png)

## 부록 · EVpedia 비교

노트북: [EVpedia.ipynb](../../Code/Appendix/EVpedia.ipynb)

**EVpedia-01** discovery 데이터셋과 EVpedia 단백질의 겹침

![EVpedia-01 discovery 데이터셋과 EVpedia 단백질의 겹침](Appendix_EVpedia/EVpedia-01_discovery_vs_evpedia_overlap.png)

**EVpedia-02** 필터에서 빠진 EV 단백질과 EVpedia에만 있는 단백질의 겹침

![EVpedia-02 필터에서 빠진 EV 단백질과 EVpedia에만 있는 단백질의 겹침](Appendix_EVpedia/EVpedia-02_filtered_out_vs_evpedia_only_overlap.png)

**EVpedia-03** 최소 연구 수 기준에 따른 민감도

![EVpedia-03 최소 연구 수 기준에 따른 민감도](Appendix_EVpedia/EVpedia-03_sensitivity_by_min_studies.png)
