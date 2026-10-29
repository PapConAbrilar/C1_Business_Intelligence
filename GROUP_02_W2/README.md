# Workshop 2 · From exploratory analysis to credible validation

**Group 02:** Benjamín Pinto and Sebastián Herrera · Business Intelligence IIB423T-1, Universidad del Desarrollo · Due 29 October 2026.

W2 continues the W1/C1 project on **recorded respiratory emergency visits in Chile's DEIS emergency network, 2020-2024**. The question, KPI and observation unit are unchanged:

- **Decision (proposed user: public-network winter planners):** when to intensify review of weekly demand by care setting before and during the Winter Campaign.
- **KPI:** weekly respiratory share (%) = 100 × respiratory visits (`IdCausa = 2`) / all emergency visits (`IdCausa = 1`).
- **Source unit:** one aggregate count per facility × date × cause (not a patient).

## Open and run

The deliverable is `notebooks/W2_project.ipynb`. It is saved with all outputs visible. This folder is self-contained.

From the `GROUP_02_W2` folder:

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python analysis/execute_notebook.py   # restarts a kernel, runs every cell, saves outputs
```

Alternatively, open the notebook in Jupyter and choose *Restart & Run All*. Runtime is under one minute. All randomness uses `SEED = 2026`. `analysis/build_w2_notebook.py` is the editable source that regenerates the notebook's cells, and `execute_notebook.py` re-runs it.

## Data provenance

| Item | Detail |
|---|---|
| Input (read-only) | `data/input/emergency_id1_id2_all_dates_2020_2024.csv.gz`, an unchanged copy of the uncleaned C1 extract (`GROUP_02_C1/data/input/` in the C1 repository) with every date in 2020-2024 for cause IDs 1 and 2 (2,169,824 rows). The notebook verifies SHA-256 `8132dc6b…af390` before any analysis. |
| Original sources | Five DEIS *AtencionesUrgenciaYYYY.zip* archives (repositoriodeis.minsal.cl), retrieved 24 September 2026. URLs, sizes and SHA-256 hashes are in `data/source_manifest.csv`. The large ZIPs are not included. `GROUP_02_C1/analysis/download_required_sources.py` and `build_all_year_case.py` in the C1 repository (<https://github.com/PapConAbrilar/C1_Business_Intelligence>) download them and rebuild the extract. |
| Reference | `data/reference/Diccionario_AtencionesUrgencia.xlsx` (official DEIS dictionary; the *Anexo 2* facility register dated 08-07-2022 is used for the join-coverage check) and `data/reference/c1_annual_summary.csv` (C1's annual totals, used to assert that W2 reproduces them). |
| Confidentiality | Public, aggregated open data. No patient-level or confidential records. |

## Outputs

| Path | Content |
|---|---|
| `figures/fig1`-`fig6_*.png` | Distribution, relationship, seasonal/segment, coverage, sampling and split figures. |
| `data/processed/validation_checks.csv`, `row_count_log.csv` | 11 validation checks with action and row counts, plus the row log of every derived table. |
| `data/processed/annual_descriptives_w2.csv`, `coupling_levels_vs_changes.csv` | Updated descriptive statistics and the revised correlation check. |
| `data/processed/sampling_comparison.csv`, `sample25_keys.csv.gz` | Reproducible 25% stratified sample (keys) and its KPI/segment comparison. |
| `data/processed/leakage_audit.csv` | Eight leakage risks with status, evidence, consequence and mitigation. |
| `data/splits/train.csv.gz`, `validation.csv.gz`, `test.csv.gz` | Chronological facility-week holdout (targets 2020-2022 / 2023 / 2024). |
| `data/processed/split_manifest.csv`, `cv_folds.csv`, `preprocessing_parameters.csv`, `robustness_check.csv` | Split counts, rolling-origin folds, train-only preprocessing parameters and the frozen-threshold robustness check. |

## Relationship to earlier work

W1 and C1 live in the C1 repository (`GROUP_02_W1/`, `GROUP_02_C1/`) and are unchanged; their history is in that repository's git log. The notebook's §1 contains the feedback-to-action table and a table of the C1 conclusions that W2 retains, revises or withdraws.
