"""Build RESULTS.html and Results/figures/ from the notebooks and result files in the repository.

Usage (python from the pinned environment in RESULTS.md, from anywhere in the repository):
    python Code/Reproduction/make_results_html.py

- RESULTS.html: one self-contained page (images embedded) with the run order, the result files,
  key numbers, every notebook figure, the SHAP plots of 08 and the reproduction notes.
- Results/figures/: the notebook figures as PNG files, the SHAP plots as standalone HTML files and
  a README.md index. The folder is deleted and written again on every run.

Figures come from the notebook outputs. File sizes, the cross-validation figure and
Feature_summary.csv are read from the working tree, and the directory tree is copied from
RESULTS.md. Descriptions, captions, file names and the AUC values (read off
Combined_AUC_filter_crossval.png) are written in this script: update them if the notebooks change.
"""
import base64
import html
import json
import re
import shutil
import struct
import sys
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[2]
FIG_DIR = REPO / "Results" / "figures"
GH = "https://github.com/dkdlqoddi/ExtracellularVesicles/blob/master/"
GH_TREE = "https://github.com/dkdlqoddi/ExtracellularVesicles/tree/master/"
esc = html.escape


def tree_from_results_md():
    text = (REPO / "RESULTS.md").read_text(encoding="utf-8")
    return re.search(r"```text\n(.*?)\n```", text, re.S).group(1) + "\n"


def file_size(path):
    return (REPO / path).stat().st_size


def human(n):
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n:.1f} {unit}" if n < 10 and unit != "B" else f"{n:.0f} {unit}"
        n /= 1024


def png_size(raw):
    return struct.unpack(">II", raw[16:24])


STATUS = {
    "=": ("동일", "ok"),
    "o": ("줄 순서만 다름", "eq"),
    "f": ("값 차이 ≤5e-15", "eq"),
    "m": ("트리 동일, 바이트만 다름", "eq"),
    "g": ("글꼴만 다름", "eq"),
}

# key -> (path, short label, Korean title, what it does, files it writes)
NOTEBOOKS = {
    "01": ("Code/01_DataCuration.ipynb", "01", "데이터 정제",
           "Vesiclepedia·ExoCarta를 정제해 일반·엄격한 EV 데이터셋과 고·저신뢰 EV 세트를 만듭니다.", "Curated 목록 6개"),
    "02": ("Code/02_FeatureGeneration_Human_Proteome.ipynb", "02", "인간 프로테옴 특징 생성",
           "인간 프로테옴 단백질마다 특징 93개를 계산하고 MS 필터를 적용합니다.", "특징 행렬 2개"),
    "03": ("Code/03_DatasetGeneration_ML_EV.ipynb", "03", "학습 데이터셋 생성",
           "EV 라벨을 붙이고 저빈도 단백질을 빼서 학습 데이터 3종을 만듭니다.", "학습 데이터 3개, EV_proteins.txt"),
    "04": ("Code/04_FeatureAnalysis_EV.ipynb", "04", "특징 분석",
           "특징별 EV·비EV 유의성 검정, 상관, 분포를 봅니다.", "MS_iso_filter_P_values.csv"),
    "RandomModel": ("Code/Appendix/RandomModel.ipynb", "부록", "무작위 모델",
                    "라벨을 섞어 학습한 모델로 특징 중요도의 기준선을 만듭니다.", "FI_Random_model.csv"),
    "05": ("Code/05_RandomForestTraining_ML.ipynb", "05", "랜덤 포레스트 학습",
           "데이터셋 3종 × 전체·서열 기반 특징으로 모델 6개를 학습합니다.", "모델 6개, 스케일러"),
    "06": ("Code/06_RandomForestAnalysis_ML.ipynb", "06", "모델 분석",
           "테스트 성능과 특징 중요도를 분석합니다.", "Feature_summary.csv"),
    "07": ("Code/07_Validation.ipynb", "07", "고·저신뢰 EV 세트 검증",
           "고·저신뢰 EV 세트의 특징 분포를 EV·비EV와 비교합니다.", "—"),
    "08": ("Code/08_CaseStudy.ipynb", "08", "SHAP 사례 분석",
           "참양성·위음성·참음성·위양성 사례를 SHAP으로 설명합니다.", "—"),
    "EVpedia": ("Code/Appendix/EVpedia.ipynb", "부록", "EVpedia 비교",
                "EVpedia 데이터베이스와 비교합니다.", "—"),
    "CV": ("Code/Appendix/RandomForest_CV.py", "부록", "교차검증",
           "데이터셋 3종의 5-fold 교차검증 ROC 곡선을 그립니다.", "Combined_AUC_filter_crossval.png"),
}
RUN_ORDER = ["01", "02", "03", "04", "RandomModel", "05", "06", "07", "08", "EVpedia", "CV"]
GALLERY_ORDER = ["01", "03", "04", "06", "07", "08", "RandomModel", "EVpedia"]

FOLDERS = [
    ("curated", "Data/Curated/", "정제된 EV 단백질 목록과 프로테옴 특징 행렬", [
        ("VPEC_all.csv", "01", "=", "일반 EV 데이터셋. Vesiclepedia와 ExoCarta를 합친 EV 단백질 11,952개 (Entrez ID, 유전자 기호, 등장 횟수, UniProt ID)"),
        ("VP_Isolation_filter.csv", "01", "=", "엄격한 EV 데이터셋. 분리 방법으로 거른 Vesiclepedia EV 단백질 6,678개"),
        ("VP_pre2014_mapped.csv", "01", "=", "2014년 이전 연구에서 검출된 Vesiclepedia EV 단백질 9,988개"),
        ("Isolation_methods_filtered.txt", "01", "=", "엄격한 EV 데이터셋을 만들 때 인정한 분리 방법 조합 18개"),
        ("Low_confidence_EV_proteins.txt", "01", "=", "저신뢰 EV 단백질 UniProt ID 9,988개 (<code>VP_pre2014_mapped.csv</code>의 ID)"),
        ("High_confidence_EV_proteins.txt", "01", "o", "고신뢰 EV 단백질 UniProt ID 3,243개. 고품질 EV 연구 3편(혈장·소변·세포 배양)의 합집합"),
        ("features_human_proteome.csv", "02", "f", "인간 프로테옴 단백질 20,381개 × 특징 93개 (<code>id</code>, <code>fasta_sequence</code> 열 포함)"),
        ("features_human_proteome_MS_filter.csv", "02", "f", "위 행렬에서 ProteomicsDB 기준 질량분석(MS) 검출이 가능한 단백질 16,790개만 남긴 것"),
        ("EV_proteins.txt", "03", "=", "논문 discovery 데이터셋의 EV 단백질 UniProt ID 5,965개"),
    ]),
    ("training", "Data/Training/", "학습 데이터셋", [
        ("training_data_no_filter.csv", "03", "f", "일반 EV 데이터셋 × 전체 프로테옴. 단백질 16,929개 (EV 8,408 / 비EV 8,521)"),
        ("training_data_MS_filter.csv", "03", "f", "일반 EV 데이터셋 × MS 검출 가능 프로테옴. 단백질 13,709개 (EV 8,198 / 비EV 5,511)"),
        ("training_data_MS_iso_filter.csv", "03", "f", "엄격한 EV 데이터셋 × MS 검출 가능 프로테옴 (논문의 discovery 데이터셋). 단백질 16,255개 (EV 5,965 / 비EV 10,290)"),
    ]),
    ("summary", "Data/", "특징 통계 요약", [
        ("MS_iso_filter_P_values.csv", "04", "=", "discovery 데이터셋에서 특징 93개를 EV와 비EV로 나눠 비교한 p-value와 FDR 보정 p-value (연속형은 Mann-Whitney U, 범주형은 Fisher 정확 검정)"),
        ("Feature_summary.csv", "06", "=", "특징 93개별 보정 p-value, EV 클래스와의 상관계수, 학습 모델·무작위 모델의 특징 중요도"),
    ]),
    ("models", "Models/", "랜덤 포레스트 모델", [
        ("EV_RF_model_no_filter.pkl", "05", "m", "no_filter · 전체 특징 93개 · 학습 13,452 / 테스트 3,364"),
        ("EV_RF_model_no_filter_seq.pkl", "05", "m", "no_filter · 서열 기반 특징 75개 · 학습 13,452 / 테스트 3,364"),
        ("EV_RF_model_MS_filter.pkl", "05", "m", "MS_filter · 전체 특징 93개 · 학습 8,817 / 테스트 2,205"),
        ("EV_RF_model_MS_filter_seq.pkl", "05", "m", "MS_filter · 서열 기반 특징 75개 · 학습 8,817 / 테스트 2,205"),
        ("EV_RF_model_MS_iso_filter.pkl", "05", "m", "MS_iso_filter · 전체 특징 93개 · 학습 9,544 / 테스트 2,386"),
        ("EV_RF_model_MS_iso_filter_seq.pkl", "05", "m", "MS_iso_filter · 서열 기반 특징 75개 · 학습 9,544 / 테스트 2,386"),
        ("EV_scaler_MS_iso_filter.pkl", "05", "=", "MS_iso_filter 학습 데이터에 맞춘 RobustScaler (08에서 사용)"),
    ]),
    ("appendix", "Code/Appendix/", "부록 결과", [
        ("FI_Random_model.csv", "RandomModel", "=", "라벨을 섞어 학습한 무작위 모델의 특징 중요도 93개 (06이 학습 모델과 비교할 때 읽음)"),
        ("Combined_AUC_filter_crossval.png", "CV", "g", "데이터셋 3종 × 전체·서열 기반 특징의 5-fold 교차검증 ROC 곡선과 AUC"),
    ]),
]

CAPTIONS = {
    ("01", 26): "일반 vs 엄격한 EV 데이터셋의 겹침",
    ("01", 41): "상위 EV 단백질의 기능 농축 분석 (KEGG 2019 Human)",
    ("03", 13): "EV 데이터셋과 인간 프로테옴의 겹침 (데이터셋 3종)",
    ("03", 22): "저빈도 단백질 제거 후 EV·비EV 단백질 수",
    ("04", 21): "특징 간 상관 (히트맵)",
    ("04", 22): "특징별 EV 클래스와의 상관",
    ("04", 26): "PTM 보유 비율: 팔미토일화·유비퀴틴화·아세틸화·니트로실화",
    ("04", 27): "PTM 보유 비율: 전체 PTM·메틸화·인산화·당화",
    ("04", 28): "PTM 보유 비율: 프레닐화·미리스토일화·GPI 앵커",
    ("04", 30): "coiled coil 보유 비율",
    ("04", 32): "도메인 보유 비율: EGF·RAS·RRM·WW",
    ("04", 35): "특징 분포: 불안정성 지수·등전점·노출 극성/소수성 잔기 비율",
    ("04", 36): "특징 분포: 알파 나선·베타 시트·턴·무질서도",
    ("04", 38): "분자량 분포와 MS 필터 효과 (1)",
    ("04", 39): "분자량 분포와 MS 필터 효과 (2)",
    ("06", 18): "테스트 세트 ROC 곡선 · 전체 특징",
    ("06", 19): "혼동 행렬 · 전체 특징",
    ("06", 21): "테스트 세트 ROC 곡선 · 서열 기반 특징",
    ("06", 22): "혼동 행렬 · 서열 기반 특징",
    ("06", 24): "ROC 비교: 전체 특징 vs 서열 기반 특징",
    ("06", 28): "특징 중요도 · 전체 특징 · no_filter 모델",
    ("06", 29): "특징 중요도 · 전체 특징 · MS_filter 모델",
    ("06", 30): "특징 중요도 · 전체 특징 · MS_iso_filter 모델",
    ("06", 32): "특징 중요도 · 서열 기반 특징 · no_filter 모델",
    ("06", 33): "특징 중요도 · 서열 기반 특징 · MS_filter 모델",
    ("06", 34): "특징 중요도 · 서열 기반 특징 · MS_iso_filter 모델",
    ("06", 41): "상위 특징의 중요도와 상관 (데이터셋 3종)",
    ("06", 43): "상위 특징의 중요도와 상관 (discovery 모델)",
    ("06", 46): "모델별 특징 중요도 순위",
    ("07", 24): "EV·비EV·고신뢰·저신뢰 비교: 분자량·불안정성 지수·등전점·노출 극성 잔기 비율",
    ("07", 25): "EV·비EV·고신뢰·저신뢰 비교: 알파 나선·베타 시트·턴·무질서도",
    ("07", 28): "EV·비EV·고신뢰·저신뢰 비교: 팔미토일화·아세틸화·메틸화·니트로실화",
    ("07", 29): "EV·비EV·고신뢰·저신뢰 비교: 전체 PTM·유비퀴틴화·당화·인산화",
    ("EVpedia", 19): "discovery 데이터셋과 EVpedia 단백질의 겹침",
    ("EVpedia", 22): "필터에서 빠진 EV 단백질과 EVpedia에만 있는 단백질의 겹침",
    ("EVpedia", 25): "최소 연구 수 기준에 따른 민감도",
    ("RandomModel", 18): "무작위 모델의 테스트 세트 ROC 곡선",
    ("RandomModel", 21): "무작위 모델의 특징 중요도",
}

# file names in Results/figures/ are "<label>_<slug>.png"
SLUGS = {
    ("01", 26): "general_vs_stringent_ev_overlap",
    ("01", 41): "kegg_enrichment_top_ev_proteins",
    ("03", 13): "ev_vs_proteome_overlap",
    ("03", 22): "ev_counts_after_low_count_removal",
    ("04", 21): "feature_correlation_heatmap",
    ("04", 22): "feature_correlation_with_ev",
    ("04", 26): "ptm_palmitoylation_ubiquitination_acetylation_nitrosylation",
    ("04", 27): "ptm_any_methylation_phosphorylation_glycosylation",
    ("04", 28): "ptm_prenylation_myristoylation_gpi_anchor",
    ("04", 30): "coiled_coil",
    ("04", 32): "domains_egf_ras_rrm_ww",
    ("04", 35): "violin_instability_pi_exposed_residues",
    ("04", 36): "violin_secondary_structure_disorder",
    ("04", 38): "molecular_weight_ms_filter_1",
    ("04", 39): "molecular_weight_ms_filter_2",
    ("06", 18): "roc_test_all_features",
    ("06", 19): "confusion_matrix_all_features",
    ("06", 21): "roc_test_sequence_features",
    ("06", 22): "confusion_matrix_sequence_features",
    ("06", 24): "roc_all_vs_sequence_features",
    ("06", 28): "importance_all_features_no_filter",
    ("06", 29): "importance_all_features_ms_filter",
    ("06", 30): "importance_all_features_ms_iso_filter",
    ("06", 32): "importance_sequence_features_no_filter",
    ("06", 33): "importance_sequence_features_ms_filter",
    ("06", 34): "importance_sequence_features_ms_iso_filter",
    ("06", 41): "top_features_importance_correlation_3_datasets",
    ("06", 43): "top_features_importance_correlation_discovery",
    ("06", 46): "importance_rank_by_model",
    ("07", 24): "violin_mw_instability_pi_polar_exposed",
    ("07", 25): "violin_secondary_structure_disorder",
    ("07", 28): "bar_palmitoylation_acetylation_methylation_nitrosylation",
    ("07", 29): "bar_ptm_ubiquitination_glycosylation_phosphorylation",
    ("EVpedia", 19): "discovery_vs_evpedia_overlap",
    ("EVpedia", 22): "filtered_out_vs_evpedia_only_overlap",
    ("EVpedia", 25): "sensitivity_by_min_studies",
    ("RandomModel", 18): "roc_test",
    ("RandomModel", 21): "feature_importance",
}

SUBDIRS = {
    "01": "01_DataCuration", "03": "03_DatasetGeneration_ML_EV", "04": "04_FeatureAnalysis_EV",
    "06": "06_RandomForestAnalysis_ML", "07": "07_Validation", "08": "08_CaseStudy",
    "RandomModel": "Appendix_RandomModel", "EVpedia": "Appendix_EVpedia",
}

SHAP_CASES = {
    "True positive (EV predicted & EV annotated)": ("참양성 (TP)", "실제 EV, EV로 예측", "true_positive"),
    "False negative (non-EV predicted & EV annotated)": ("위음성 (FN)", "실제 EV, 비EV로 예측", "false_negative"),
    "True negative (non-EV predicted & non-EV annotated)": ("참음성 (TN)", "실제 비EV, 비EV로 예측", "true_negative"),
    "False positive (EV predicted & non-EV annotated)": ("위양성 (FP)", "실제 비EV, EV로 예측", "false_positive"),
}

AUC = [  # from the legend of Combined_AUC_filter_crossval.png
    ("필터 없음", "no_filter", "0.87 ± 0.00", "0.82 ± 0.00", False),
    ("MS 필터", "MS_filter", "0.84 ± 0.01", "0.77 ± 0.02", False),
    ("MS + 분리 방법 필터 (discovery)", "MS_iso_filter", "0.84 ± 0.00", "0.77 ± 0.01", True),
]


def walk(path):
    """Yield (cell index, section, subsection, cell) for the code cells of a notebook."""
    h2 = h3 = ""
    for i, cell in enumerate(json.loads((REPO / path).read_text(encoding="utf-8"))["cells"]):
        if cell["cell_type"] == "markdown":
            for line in "".join(cell["source"]).splitlines():
                line = line.strip()
                if re.match(r"^#{1,2} ", line):
                    h2, h3 = line.lstrip("# ").strip(), ""
                elif re.match(r"^#{3,} ", line):
                    h3 = line.lstrip("# ").strip()
            continue
        yield i, h2, h3, cell


def figures(key):
    path = NOTEBOOKS[key][0]
    out = []
    for i, h2, h3, cell in walk(path):
        for o in cell.get("outputs", []):
            png = o.get("data", {}).get("image/png")
            if not png:
                continue
            b64 = "".join(png) if isinstance(png, list) else png
            b64 = b64.replace("\n", "")
            w, h = png_size(base64.b64decode(b64))
            caption = CAPTIONS.get((key, i))
            if caption is None:
                print(f"WARNING: no caption for {key} cell {i} ({h2} > {h3})", file=sys.stderr)
                caption = h3 or h2
            out.append({"b64": b64, "w": w, "h": h, "cell": i, "caption": caption,
                        "section": " › ".join(x for x in (h2, h3) if x)})
    for n, fig in enumerate(out, 1):
        fig["label"] = f"{key}-{n:02d}"
        fig["file"] = f"{fig['label']}_{SLUGS[(key, fig['cell'])]}.png"
        fig["rel"] = f"Results/figures/{SUBDIRS[key]}/{fig['file']}"
    return out


def shap_cases():
    bundle, cases = None, []
    for i, h2, h3, cell in walk(NOTEBOOKS["08"][0]):
        src = "".join(cell["source"])
        if "shap.force_plot" not in src:
            continue
        htmls = ["".join(o["data"]["text/html"]) for o in cell["outputs"] if "text/html" in o.get("data", {})]
        lib, plot = htmls
        if bundle is None:
            bundle = re.sub(r"^\s*<div align='center'>.*?</div>", "", lib, count=1, flags=re.S).strip()
            assert bundle.startswith("<script"), bundle[:80]
        label, truth, slug = SHAP_CASES[h3]
        uniprot = re.search(r'get_instance\("([A-Z0-9]+)"\)', src).group(1)
        code = f"08-{len(cases) + 1:02d}"
        file = f"{code}_shap_{slug}_{uniprot}.html"
        cases.append({
            "label": label, "truth": truth, "section": h3, "uniprot": uniprot, "code": code,
            "file": file, "rel": f"Results/figures/{SUBDIRS['08']}/{file}",
            "out": float(re.search(r'"outValue": ([-0-9.e]+)', plot).group(1)),
            "base": float(re.search(r'"baseValue": ([-0-9.e]+)', plot).group(1)),
            "plot": plot.strip(),
        })
    return bundle, cases


def shap_page(case, bundle):
    """A standalone page with one SHAP force plot (the SHAP JavaScript bundle is embedded)."""
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{case['code']} SHAP · {case['uniprot']}</title>
<style>body{{margin:24px;font:15px/1.6 system-ui,-apple-system,"Segoe UI","Apple SD Gothic Neo","Malgun Gothic",sans-serif;color:#1f2328;background:#fff}}h1{{font-size:1.15rem;margin:0 0 4px}}p{{margin:0 0 16px;color:#5b616b}}</style>
</head>
<body>
<h1>{case['code']} · {esc(case['label'])} · {case['uniprot']}</h1>
<p>{esc(case['truth'])} · 예측 확률 {case['out']:.3f} (기준값 {case['base']:.3f}) · discovery 모델(EV_RF_model_MS_iso_filter) · 08_CaseStudy.ipynb. 빨간색 특징은 EV 확률을 높이고 파란색 특징은 낮춥니다.</p>
{bundle}
{case['plot']}
</body>
</html>
"""


def figures_readme(all_figs, cases):
    lines = [
        "# 노트북 그림", "",
        "노트북 출력에 들어 있던 그림을 파일로 꺼낸 것입니다. 그림 설명은 "
        "[RESULTS.md](../../RESULTS.md)·[RESULTS.html](../../RESULTS.html)과 같습니다.", "",
        "이 폴더는 [`Code/Reproduction/make_results_html.py`](../../Code/Reproduction/make_results_html.py)가 "
        "노트북에서 다시 만듭니다. 실행할 때마다 폴더 전체를 새로 쓰므로 여기에 다른 파일을 두지 마세요.", "",
    ]
    for key in GALLERY_ORDER:
        path, _, title = NOTEBOOKS[key][:3]
        lines += [f"## {key if key.isdigit() else '부록'} · {title}", "", f"노트북: [{Path(path).name}](../../{path})", ""]
        if key == "08":
            lines += ["SHAP force plot은 JavaScript로 그려지므로 GitHub에서는 보이지 않습니다. 내려받아 브라우저로 여세요.", ""]
            lines += [f"- [{c['code']} {c['label']} · {c['uniprot']}]({SUBDIRS[key]}/{c['file']}): "
                      f"{c['truth']}, 예측 확률 {c['out']:.3f}" for c in cases]
            lines.append("")
            continue
        for fig in all_figs[key]:
            lines += [f"**{fig['label']}** {fig['caption']}", "",
                      f"![{fig['label']} {fig['caption']}]({SUBDIRS[key]}/{fig['file']})", ""]
    return "\n".join(lines)


def export_figures(all_figs, bundle, cases):
    if FIG_DIR.exists():
        shutil.rmtree(FIG_DIR)
    for key in GALLERY_ORDER:
        folder = FIG_DIR / SUBDIRS[key]
        folder.mkdir(parents=True)
        if key == "08":
            for case in cases:
                (folder / case["file"]).write_text(shap_page(case, bundle), encoding="utf-8")
        else:
            for fig in all_figs[key]:
                (folder / fig["file"]).write_bytes(base64.b64decode(fig["b64"]))
    (FIG_DIR / "README.md").write_text(figures_readme(all_figs, cases), encoding="utf-8")


def producer_link(key):
    path, label, title = NOTEBOOKS[key][:3]
    text = key if key in ("01", "02", "03", "04", "05", "06", "07", "08") else Path(path).name
    return f'<a href="{GH}{path}" title="{esc(Path(path).name)}">{esc(text)}</a>'


def fmt_p(p):
    if p == 0:
        return "&lt; 10<sup>−300</sup>"
    mant, exp = f"{p:.1e}".split("e")
    return f"{mant}×10<sup>{int(exp)}</sup>".replace("<sup>-", "<sup>−")


def fmt_signed(x):
    return f"{x:+.2f}".replace("-", "−")


# ---------------------------------------------------------------- sections

def section_pipeline(fig_counts):
    rows = []
    for n, key in enumerate(RUN_ORDER, 1):
        path, label, title, does, writes = NOTEBOOKS[key]
        if key == "08":
            figs = "SHAP 4"
        elif key == "CV":
            figs = "파일 1"
        else:
            figs = str(fig_counts.get(key, 0)) if fig_counts.get(key) else "—"
        rows.append(
            f"<tr><td class='num'>{n}</td>"
            f"<td class='file'><a href='{GH}{path}'>{esc(Path(path).name)}</a><div class='sub'>{esc(title)}</div></td>"
            f"<td>{esc(does)}</td><td>{esc(writes)}</td><td class='num'>{figs}</td></tr>")
    return f"""
<section id="pipeline">
  <h2>파이프라인</h2>
  <p class="sub">노트북을 아래 순서로 실행하면 결과 파일이 만들어집니다. 노트북들이 서로의 결과를 정해진 경로에서 읽으므로 파일 위치를 옮기면 안 됩니다.</p>
  <div class="table-wrap"><table>
    <thead><tr><th class="num">순서</th><th>노트북·스크립트</th><th>하는 일</th><th>만드는 파일</th><th class="num">그림</th></tr></thead>
    <tbody>{''.join(rows)}</tbody>
  </table></div>
  <p class="note">07·08·EVpedia는 파일을 쓰지 않고 결과를 노트북 안에만 남깁니다. <code>EVpedia</code>는 05 다음, <code>RandomForest_CV.py</code>는 03 다음이면 언제 실행해도 됩니다.</p>
</section>"""


def section_files():
    parts = []
    total = 0
    for fid, folder, title, files in FOLDERS:
        rows = []
        sizes = 0
        for name, who, st, desc in files:
            size = file_size(folder + name)
            sizes += size
            label, cls = STATUS[st]
            rows.append(
                f"<tr><td class='file'><a href='{GH}{folder}{name}'>{esc(name)}</a></td>"
                f"<td class='num'>{human(size)}</td><td class='num'>{producer_link(who)}</td>"
                f"<td>{desc}</td><td><span class='badge {cls}'>{esc(label)}</span></td></tr>")
        total += sizes
        extra = ""
        if fid == "training":
            extra = ("<p class='note'>세 파일 모두 열은 <code>id</code>, <code>EV</code>(1 = EV 단백질, 0 = 비EV 단백질), 특징 93개입니다. "
                     "EV 목록에 있는 단백질은 EV로, 나머지 프로테옴은 비EV로 표시했고, EV 데이터베이스에 2번 이하로만 등장한 단백질은 애매하다고 보고 뺐습니다.</p>")
        if fid == "curated":
            extra = "<p class='note'>같은 폴더의 <code>EV_proteins_Entrez_to_Uniprot.tsv</code>는 결과물이 아니라 입력 파일(Entrez → UniProt ID 변환표)입니다.</p>"
        if fid == "models":
            extra = """
  <ul class="tight">
    <li>모든 모델은 <code>RandomForestClassifier(n_estimators=1000, max_features=10, random_state=0)</code>입니다.</li>
    <li>다수 클래스를 언더샘플링해 EV와 비EV를 1:1로 맞춘 뒤 80%로 학습하고 20%는 테스트용으로 남겼습니다. 연속형 특징은 RobustScaler로 스케일링했습니다.</li>
    <li><code>_seq</code> 모델은 서열에서 계산하거나 예측한 특징 75개만 씁니다. 나머지 모델은 여기에 데이터베이스 주석 특징 18개(UniProt·PhosphoSitePlus 등의 PTM 주석, HSP, 막관통 주석)를 더한 93개를 씁니다.</li>
    <li>모델은 gzip으로 압축한 pickle, 스케일러는 일반 pickle입니다. scikit-learn 1.0.1로 저장돼 있어 1.3 이상에서는 열리지 않습니다.</li>
  </ul>
  <pre><code>import gzip, pickle

with gzip.open("Models/EV_RF_model_MS_iso_filter.pkl", "rb") as f:
    rf = pickle.load(f)
with open("Models/EV_scaler_MS_iso_filter.pkl", "rb") as f:
    scaler = pickle.load(f)</code></pre>"""
        parts.append(f"""
  <h3 id="files-{fid}"><code>{esc(folder)}</code> {esc(title)} <span class="count">{len(files)}개 · {human(sizes)}</span></h3>
  <div class="table-wrap"><table>
    <thead><tr><th>파일</th><th class="num">크기</th><th class="num">만든 곳</th><th>내용</th><th>재실행 비교</th></tr></thead>
    <tbody>{''.join(rows)}</tbody>
  </table></div>{extra}""")
    return f"""
<section id="files">
  <h2>결과 파일</h2>
  <p class="sub">파일로 저장되는 결과 23개입니다. 크기는 저장소에 커밋된 파일 기준입니다. 결과 파일은 파이프라인을 다시 실행해 만든 것이고, ‘재실행 비교’는 그 파일을 저자 원본과 비교한 결과입니다(<a href="#rerun">설명</a>).</p>
  <details class="tree"><summary>디렉터리 트리로 보기</summary><pre>{esc(tree_from_results_md())}</pre></details>
  {''.join(parts)}
  <h3>결과물이 아닌 파일</h3>
  <p class="note">아래 입력 데이터는 실행 중에 바뀌지 않습니다. 자세한 설명은 <a href="{GH}Data/README.md">Data/README.md</a>에 있습니다.</p>
  <ul class="tight">
    <li><code>Data/Raw/</code>: Vesiclepedia, ExoCarta, EVpedia 원본 데이터</li>
    <li><code>Data/Features/</code>: NetSurfP-2.0, UniProt, PhosphoSitePlus, PROSITE, TMHMM 등 특징 원자료</li>
    <li><code>Data/ProteomicsDB/</code>: 단백질별 질량분석 검출 근거</li>
    <li><code>Data/Validation/Raw/</code>: 고신뢰 EV 세트를 만드는 데 쓴 연구 3편의 데이터</li>
    <li><code>Data/Curated/EV_proteins_Entrez_to_Uniprot.tsv</code>: Entrez → UniProt ID 변환표</li>
  </ul>
</section>""", total


def section_key():
    cv = base64.b64encode((REPO / "Code/Appendix/Combined_AUC_filter_crossval.png").read_bytes()).decode()
    w, h = png_size(base64.b64decode(cv))
    auc_rows = "".join(
        f"<tr{' class=hl' if hl else ''}><td>{esc(name)} <code>{esc(code)}</code></td><td class='num'>{a}</td><td class='num'>{s}</td></tr>"
        for name, code, a, s, hl in AUC)
    df = pd.read_csv(REPO / "Data/Feature_summary.csv", index_col=0)
    top = df.sort_values("Feature importance (Trained model)", ascending=False).head(10)
    feat_rows = "".join(
        f"<tr><td class='num'>{n}</td><td>{esc(name)}</td>"
        f"<td class='num'>{r['Feature importance (Trained model)']:.3f}</td>"
        f"<td class='num'>{r['Feature importance (Random model)']:.3f}</td>"
        f"<td class='num'>{fmt_signed(r['Correlation with EV class'])}</td>"
        f"<td class='num'>{fmt_p(r['Adjusted P-value (EV vs. non-EV)'])}</td></tr>"
        for n, (name, r) in enumerate(top.iterrows(), 1))
    return f"""
<section id="key">
  <h2>주요 결과</h2>
  <p class="sub">결과 파일에서 바로 읽을 수 있는 핵심 수치입니다.</p>
  <h3>교차검증 성능 (ROC-AUC)</h3>
  <p>데이터셋 3종을 5-fold 교차검증한 ROC-AUC(평균 ± 표준편차)입니다. discovery 데이터셋에서 전체 특징 모델 0.84 ± 0.00, 서열 기반 모델 0.77 ± 0.01은 논문 초록의 수치와 같습니다.</p>
  <div class="table-wrap narrow"><table>
    <thead><tr><th>데이터셋</th><th class="num">전체 특징 (93개)</th><th class="num">서열 기반 특징 (75개)</th></tr></thead>
    <tbody>{auc_rows}</tbody>
  </table></div>
  <figure class="single">
    <div class="img"><img src="data:image/png;base64,{cv}" width="{w}" height="{h}" alt="데이터셋 3종의 5-fold 교차검증 ROC 곡선" loading="lazy"></div>
    <figcaption><span class="num">결과 파일</span>Combined_AUC_filter_crossval.png<span class="src">Code/Appendix/RandomForest_CV.py가 저장한 그림</span></figcaption>
  </figure>
  <h3>중요한 특징 상위 10개</h3>
  <p>discovery 데이터셋으로 학습한 전체 특징 모델(<code>EV_RF_model_MS_iso_filter</code>)의 특징 중요도 순서입니다. <code>Data/Feature_summary.csv</code>에서 가져왔습니다.</p>
  <div class="table-wrap"><table>
    <thead><tr><th class="num">순위</th><th>특징</th><th class="num">중요도 (학습 모델)</th><th class="num">중요도 (무작위 모델)</th><th class="num">EV 클래스와의 상관</th><th class="num">보정 p-value</th></tr></thead>
    <tbody>{feat_rows}</tbody>
  </table></div>
  <p class="note">¹ 데이터베이스 주석(UniProt·PhosphoSitePlus 등)에서 온 특징입니다. S·C·H는 해당 아미노산의 조성 특징입니다. 무작위 모델 중요도는 라벨을 섞어 학습한 모델의 값으로, 비교 기준선입니다.</p>
</section>"""


def figure_html(fig):
    wide = fig["w"] / fig["h"] >= 2.2 or (fig["w"] >= 1100 and fig["w"] / fig["h"] >= 1.0)
    return f"""
    <figure{' class="wide"' if wide else ''}>
      <div class="img"><img src="data:image/png;base64,{fig['b64']}" width="{fig['w']}" height="{fig['h']}" alt="{esc(fig['caption'])}" loading="lazy"></div>
      <figcaption><span class="num">{esc(fig['label'])}</span>{esc(fig['caption'])}<span class="src">노트북 섹션: {esc(fig['section'])} · 파일: <a href="{fig['rel']}">{esc(fig['file'])}</a></span></figcaption>
    </figure>"""


def section_figures(all_figs, bundle, cases):
    groups = []
    for key in GALLERY_ORDER:
        path, label, title = NOTEBOOKS[key][:3]
        head = (f'<h3 id="fig-{key}">{esc(key if key.isdigit() else "부록")} · {esc(title)} '
                f'<a class="nblink" href="{GH}{path}">{esc(Path(path).name)} ↗</a></h3>')
        if key == "08":
            cards = "".join(f"""
    <div class="shap-card">
      <div class="shap-head"><h4>{c['code']} · {esc(c['label'])} · <a href="https://www.uniprot.org/uniprotkb/{c['uniprot']}/entry">{c['uniprot']}</a></h4>
        <span class="shap-meta">{esc(c['truth'])} · 예측 확률 <b>{c['out']:.3f}</b> (기준값 {c['base']:.3f}) · 파일: <a href="{c['rel']}">{esc(c['file'])}</a></span></div>
      <div class="shap-plot">{c['plot']}</div>
    </div>""" for c in cases)
            groups.append(f"""
  {head}
  <p class="note">discovery 모델(<code>EV_RF_model_MS_iso_filter</code>)의 예측을 SHAP force plot으로 설명합니다. 기준값(평균 예측)에서 출발해 빨간색 특징은 EV 확률을 높이고, 파란색 특징은 낮춥니다. 사례 단백질은 노트북에서 예측 확률로 정렬한 후보 목록을 보고 고른 것입니다.</p>
  {bundle}
  {cards}""")
            continue
        figs = all_figs[key]
        body = "".join(figure_html(f) for f in figs)
        groups.append(f"""
  {head}
  <div class="gallery">{body}
  </div>""")
    n_png = sum(len(v) for v in all_figs.values())
    return f"""
<section id="figures">
  <h2>노트북 그림</h2>
  <p class="sub">노트북 출력에 저장된 그림 {n_png}개와 SHAP 그림 {len(cases)}개입니다. 같은 그림을 <a href="{GH_TREE}Results/figures">Results/figures/</a>에 파일로도 꺼내 두었습니다(SHAP은 HTML 파일). 그림을 누르면 크게 볼 수 있습니다. 02와 05는 그림 없이 파일만 저장합니다.</p>
  {''.join(groups)}
</section>"""


SECTION_RERUN = """
<section id="rerun">
  <h2>재실행 비교</h2>
  <p class="sub">2026년 11월 27일 Linux(WSL2)에서 모든 노트북과 스크립트를 처음부터 다시 실행하고, 새로 만든 파일을 커밋된 원본과 비교했습니다. 노트북 10개와 결과 파일은 모두 다시 실행한 것으로 커밋했습니다. 결과 파일 중 바이트가 바뀐 것은 아래 표에서 ‘동일’이 아닌 13개이고, 저자 원본은 커밋 <code>0ddfa23</code>에서 볼 수 있습니다.</p>
  <div class="table-wrap"><table>
    <thead><tr><th>표시</th><th class="num">파일 수</th><th>의미</th></tr></thead>
    <tbody>
      <tr><td><span class="badge ok">동일</span></td><td class="num">10</td><td>원본과 바이트까지 같음</td></tr>
      <tr><td><span class="badge eq">줄 순서만 다름</span></td><td class="num">1</td><td>ID 3,243개는 같고 순서만 다름. 01이 파이썬 set을 그대로 저장해서 실행할 때마다 순서가 바뀜</td></tr>
      <tr><td><span class="badge eq">값 차이 ≤5e-15</span></td><td class="num">5</td><td>부동소수점 끝자리만 다름. 이 파일로 다시 학습한 모델이 원본과 같으므로 이후 결과에 영향 없음</td></tr>
      <tr><td><span class="badge eq">트리 동일, 바이트만 다름</span></td><td class="num">6</td><td>1,000개 트리와 예측 확률이 원본과 같고, 저장된 pickle 바이트만 다름</td></tr>
      <tr><td><span class="badge eq">글꼴만 다름</span></td><td class="num">1</td><td>그림 내용은 같고 글꼴만 다름</td></tr>
    </tbody>
  </table></div>
  <p class="note">노트북에 저장된 텍스트 출력(단백질 수, p-value, 특징 중요도 표 등)도 빈 줄 차이를 빼면 원본과 같았습니다.</p>
</section>"""

SECTION_REPRO = """
<section id="repro">
  <h2>재현 조건</h2>
  <p class="sub">위 비교에 쓴 환경입니다.</p>
  <h3>패키지</h3>
  <p>Python 3.8.20, numpy 1.21.6, pandas 1.3.5, scipy 1.6.3, scikit-learn 1.0.1, imbalanced-learn 0.8.1, statsmodels 0.13.5, biopython 1.79, shap 0.41.0, numba 0.56.4, matplotlib 3.5.3, seaborn 0.11.2, gseapy 0.14.0, matplotlib-venn 0.11.10</p>
  <ul class="tight">
    <li>scikit-learn 1.3 이상은 <code>Models/</code>의 pickle을 열지 못합니다.</li>
    <li>scipy 1.7부터 <code>mannwhitneyu</code>의 기본값이 양측 검정으로 바뀌어, 04의 p-value가 원본(단측 값)과 달라집니다.</li>
    <li>최신 numba는 numpy 1.22 이상이 필요해서, numba를 0.56.4로 고정해야 shap을 불러올 수 있습니다.</li>
  </ul>
  <h3>Linux 경로</h3>
  <p>노트북은 <code>Data/raw</code>처럼 소문자 경로를 쓰지만 실제 폴더 이름은 대문자로 시작합니다(Windows에서 작성됨). 그래서 소문자 이름의 심볼릭 링크 7개를 저장소에 넣어 두었고, Linux에서는 따로 할 일이 없습니다.</p>
  <p class="note">링크: <code>Data/raw</code> → <code>Raw</code>, <code>Data/curated</code> → <code>Curated</code>, <code>Data/training</code> → <code>Training</code>, <code>Data/features</code> → <code>Features</code>, <code>Data/validation</code> → <code>Validation</code>, <code>Data/Validation/raw</code> → <code>Raw</code>, <code>Data/Features/Uniprot</code> → <code>UniProt</code>. Windows·macOS처럼 대소문자를 구분하지 않는 파일 시스템에서는 이 링크와 원래 폴더의 이름이 겹칩니다. 그래서 checkout할 때 이름 충돌 경고가 나고, 링크가 만들어지지 않아 git status에 변경으로 보일 수 있습니다.</p>
  <h3>02 수정</h3>
  <p>PROSITE 파일 목록을 정렬하는 수정(커밋 <code>a9d938c</code>)이 있어야 Linux에서도 특징 열 순서가 원본과 같아지고, 모델이 원본과 똑같이 학습됩니다.</p>
  <h3>실행</h3>
  <p>01 → 02 → 03 → 04 → <code>Appendix/RandomModel</code> → 05 → 06 → 07 → 08 순서로 실행합니다. <code>Appendix/EVpedia</code>는 05 다음, <code>Appendix/RandomForest_CV.py</code>는 03 다음이면 언제 실행해도 됩니다. 노트북은 자기 폴더에서 실행해야 경로가 맞습니다.</p>
  <pre><code>(cd Code &amp;&amp; jupyter nbconvert --to notebook --execute --inplace 01_DataCuration.ipynb)
(cd Code/Appendix &amp;&amp; MPLBACKEND=Agg python RandomForest_CV.py)</code></pre>
  <h3>확인용 스크립트</h3>
  <p><a href="{GH_TREE}Code/Reproduction"><code>Code/Reproduction/</code></a>에 이 비교와 결과 정리에 쓴 스크립트가 있습니다. 위 환경의 python으로 저장소 어디에서든 실행합니다.</p>
  <ul class="tight">
    <li><code>compare_nb.py</code>: 노트북 10개의 텍스트 출력을 저자 원본(커밋 <code>0ddfa23</code>)과 셀 단위로 비교</li>
    <li><code>compare_models.py</code>: 모델 6개와 스케일러를 원본과 비교 (트리 구조, 분기값, 예측 확률)</li>
    <li><code>make_results_html.py</code>: 이 페이지(RESULTS.html)와 <code>Results/figures/</code>를 다시 만듦</li>
  </ul>
</section>""".replace("{GH_TREE}", GH_TREE)

CSS = """
:root{--bg:#f6f6f3;--fg:#1f2328;--muted:#5b616b;--line:#e2e2dc;--card:#fff;--subtle:#f0f0eb;--accent:#2b59c3;--accent-soft:#e7edfb;--ok-bg:#e1f3e6;--ok-fg:#1a6534;--eq-bg:#e7edfb;--eq-fg:#2848a0;--code-bg:#efefea;--hl:#f3f6fd;color-scheme:light dark}
@media (prefers-color-scheme:dark){:root{--bg:#14161a;--fg:#e5e5e2;--muted:#a2a7b0;--line:#2b2f35;--card:#1b1e23;--subtle:#22262c;--accent:#8fabff;--accent-soft:#23304e;--ok-bg:#163822;--ok-fg:#a3e2b6;--eq-bg:#1f2c50;--eq-fg:#bccbff;--code-bg:#20242a;--hl:#1e2433}}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.7 system-ui,-apple-system,"Segoe UI","Apple SD Gothic Neo","Malgun Gothic","Noto Sans KR",sans-serif;word-break:keep-all;overflow-wrap:break-word;-webkit-font-smoothing:antialiased}
.wrap{max-width:1120px;margin:0 auto;padding:0 24px}
header.top{padding:56px 0 30px}
.eyebrow{font-size:.85rem;font-weight:600;letter-spacing:.03em;color:var(--accent);margin:0 0 8px}
h1{font-size:2.3rem;line-height:1.25;margin:0 0 12px;letter-spacing:-.01em}
.lede{font-size:1.07rem;color:var(--muted);max-width:780px;margin:0}
.meta{margin:12px 0 0;font-size:.88rem;color:var(--muted)}
.stats{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin:28px 0 0;padding:0}
.stats div{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px 16px}
.stats dt{font-size:.82rem;color:var(--muted)}
.stats dd{margin:2px 0 0;font-size:1.5rem;font-weight:700;font-variant-numeric:tabular-nums;line-height:1.35}
.stats dd small{font-size:.85rem;font-weight:500;color:var(--muted)}
nav.toc{position:sticky;top:0;z-index:10;background:var(--bg);border-bottom:1px solid var(--line)}
nav.toc .wrap{display:flex;gap:4px;overflow-x:auto;padding-top:9px;padding-bottom:9px}
nav.toc a{flex:none;padding:5px 12px;border-radius:999px;color:var(--fg);text-decoration:none;font-size:.9rem}
nav.toc a:hover{background:var(--accent-soft);color:var(--accent)}
section{padding:40px 0 8px;scroll-margin-top:52px}
h2{font-size:1.55rem;line-height:1.3;margin:0 0 6px}
p.sub{color:var(--muted);margin:0 0 18px;max-width:860px}
h3{font-size:1.12rem;line-height:1.4;margin:34px 0 12px;scroll-margin-top:60px}
h3 .count{font-size:.85rem;font-weight:500;color:var(--muted);margin-left:6px}
h3 a.nblink{font-size:.82rem;font-weight:500;margin-left:8px;text-decoration:none}
a{color:var(--accent)}
code,pre{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,"D2Coding",monospace}
code{background:var(--code-bg);padding:.08em .35em;border-radius:5px;font-size:.88em}
pre{background:var(--code-bg);border:1px solid var(--line);border-radius:10px;padding:14px 16px;overflow-x:auto;font-size:.83rem;line-height:1.55;word-break:normal}
pre code{background:none;padding:0;font-size:inherit}
.table-wrap{overflow-x:auto;border:1px solid var(--line);border-radius:12px;background:var(--card)}
.table-wrap.narrow{max-width:720px}
table{width:100%;border-collapse:collapse;font-size:.92rem}
th,td{padding:10px 14px;text-align:left;vertical-align:top;border-bottom:1px solid var(--line)}
thead th{background:var(--subtle);font-weight:600;font-size:.83rem;color:var(--muted);white-space:nowrap}
tbody tr:last-child td{border-bottom:0}
tr.hl td{background:var(--hl);font-weight:600}
.num{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
td.file{white-space:nowrap}
td.file a{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:.86rem;text-decoration:none}
td.file a:hover{text-decoration:underline}
td .sub{font-size:.82rem;color:var(--muted)}
.badge{display:inline-block;padding:2px 9px;border-radius:999px;font-size:.78rem;font-weight:600;white-space:nowrap}
.badge.ok{background:var(--ok-bg);color:var(--ok-fg)}
.badge.eq{background:var(--eq-bg);color:var(--eq-fg)}
.note{color:var(--muted);font-size:.9rem;max-width:880px}
ul.tight{margin:10px 0 14px;padding-left:1.2em}
ul.tight li{margin:3px 0}
details.tree{margin:0 0 8px}
details.tree summary{cursor:pointer;color:var(--accent);font-size:.92rem;margin-bottom:8px}
details.tree pre{font-size:.78rem}
.gallery{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px}
figure{margin:0;background:var(--card);border:1px solid var(--line);border-radius:12px;overflow:hidden;display:flex;flex-direction:column}
figure.wide{grid-column:1/-1}
figure.single{margin-top:18px}
figure .img{background:#fff;padding:14px;display:flex;justify-content:center;align-items:center;flex:1}
figure img{display:block;max-width:100%;width:auto;height:auto;cursor:zoom-in}
figcaption{padding:10px 14px 12px;font-size:.9rem;border-top:1px solid var(--line)}
figcaption .num{font-weight:700;color:var(--accent);margin-right:.5em;text-align:left}
figcaption .src{display:block;color:var(--muted);font-size:.78rem;margin-top:2px}
.shap-card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px 16px;margin:0 0 14px}
.shap-head{display:flex;flex-wrap:wrap;align-items:baseline;gap:4px 14px;margin-bottom:8px}
.shap-head h4{margin:0;font-size:1rem}
.shap-head h4 a{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:.95rem}
.shap-meta{font-size:.88rem;color:var(--muted)}
.shap-plot{background:#fff;color:#111;border-radius:8px;padding:6px 4px;overflow-x:auto}
footer{margin:48px 0 0;padding:22px 0 40px;border-top:1px solid var(--line);color:var(--muted);font-size:.85rem}
#lightbox{position:fixed;inset:0;background:rgba(10,12,16,.88);display:flex;align-items:center;justify-content:center;padding:24px;z-index:100;cursor:zoom-out}
#lightbox[hidden]{display:none}
#lightbox img{max-width:100%;max-height:100%;background:#fff;border-radius:6px}
@media (max-width:860px){.gallery{grid-template-columns:1fr}.stats{grid-template-columns:repeat(2,minmax(0,1fr))}h1{font-size:1.85rem}}
"""

JS = """
(function(){
  var box=document.getElementById('lightbox'),big=box.querySelector('img');
  document.addEventListener('click',function(e){
    var img=e.target.closest('figure img');
    if(img){big.src=img.src;big.alt=img.alt;box.hidden=false;return;}
    if(e.target.closest('#lightbox')){box.hidden=true;big.removeAttribute('src');}
  });
  document.addEventListener('keydown',function(e){if(e.key==='Escape'){box.hidden=true;}});
})();
"""


def main():
    all_figs = {k: figures(k) for k in GALLERY_ORDER if k != "08"}
    bundle, cases = shap_cases()
    fig_counts = {k: len(v) for k, v in all_figs.items()}
    files_html, total = section_files()
    n_png = sum(fig_counts.values())
    page = f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>결과물 정리 · ExtracellularVesicles</title>
<style>{CSS}</style>
</head>
<body>
<header class="top"><div class="wrap">
  <p class="eyebrow">ExtracellularVesicles · 재현 결과</p>
  <h1>결과물 정리</h1>
  <p class="lede">Waury 외(2024) 「Proteome encoded determinants of protein sorting into extracellular vesicles」의 분석 파이프라인을 다시 실행하고, 만들어진 결과 파일과 그림을 한곳에 정리했습니다.</p>
  <p class="meta">재실행 2026-11-27 · Linux (WSL2) · Python 3.8.20 · Markdown 버전: <a href="{GH}RESULTS.md">RESULTS.md</a> · 그림 파일: <a href="{GH_TREE}Results/figures">Results/figures/</a></p>
  <dl class="stats">
    <div><dt>결과 파일</dt><dd>23<small>개</small></dd></div>
    <div><dt>결과 파일 크기</dt><dd>{human(total).split()[0]}<small> {human(total).split()[1]}</small></dd></div>
    <div><dt>노트북 그림</dt><dd>{n_png}<small> + SHAP {len(cases)}</small></dd></div>
    <div><dt>재실행 결과</dt><dd>원본과 일치<small> (내용 기준)</small></dd></div>
  </dl>
</div></header>
<nav class="toc" aria-label="목차"><div class="wrap">
  <a href="#pipeline">파이프라인</a><a href="#files">결과 파일</a><a href="#key">주요 결과</a><a href="#figures">노트북 그림</a><a href="#rerun">재실행 비교</a><a href="#repro">재현 조건</a>
</div></nav>
<main class="wrap">
{section_pipeline(fig_counts)}
{files_html}
{section_key()}
{section_figures(all_figs, bundle, cases)}
{SECTION_RERUN}
{SECTION_REPRO}
</main>
<footer><div class="wrap">Code/Reproduction/make_results_html.py가 만든 페이지입니다. 그림은 커밋된 노트북 출력에서, 표와 수치는 결과 파일에서 가져왔습니다. 그림 파일 링크는 저장소 안의 상대 경로이고, 나머지 링크는 GitHub의 master 브랜치로 연결됩니다.</div></footer>
<div id="lightbox" hidden><img alt=""></div>
<script>{JS}</script>
</body>
</html>
"""
    out = REPO / "RESULTS.html"
    out.write_text(page, encoding="utf-8")
    export_figures(all_figs, bundle, cases)
    n_files = sum(1 for p in FIG_DIR.rglob("*") if p.is_file())
    print(f"wrote {out.relative_to(REPO)} ({out.stat().st_size / 1024 / 1024:.1f} MB): {n_png} figures, "
          f"{len(cases)} SHAP plots, result files total {human(total)}")
    print(f"wrote {FIG_DIR.relative_to(REPO)}/: {n_files} files")
    for c in cases:
        print(f"  SHAP {c['code']} {c['uniprot']} out={c['out']:.3f} base={c['base']:.3f}")


if __name__ == "__main__":
    main()
