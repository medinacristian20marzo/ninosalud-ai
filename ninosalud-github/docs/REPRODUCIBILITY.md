# Reproducibility guide

## Three levels of reproducibility
**1. Distributed aggregate inputs:** EDA feature ablation, matched metrics, descriptive seasonal reference, bootstrap and auxiliary dengue benchmark can be rerun from this repository. This is the supported public quick start.

**2. Separately acquired source inputs:** the original CDC workbook can rebuild the primary province-week CSV; the regional dengue audit requires its original case-level CSV. Source hashes identify exactly which snapshots were used. Newer source versions may produce different results. Never commit local raw files.

**3. Archived contextual views:** territorial geometry, legacy source-history summaries and some chart payloads are preserved extracts. A full automatic rebuild of every map from every original government file is not claimed.

## Environment
Release verification: Python 3.13.5, NumPy 2.3.5, scikit-learn 1.8.0. Reproduced values may have tiny floating-point differences on other platforms. The app itself requires only a modern browser.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python research/eda_climate_ablation.py
python research/methodological_robustness_v11.py --no-regional
python research/eda_reference_signals.py
python research/legacy_dengue_backtest.py
```

The ablation writes to `research/ablation_reproduced/`; compare its CSVs to `data/eda_climate_ablation_*.csv`. The auxiliary dengue script writes to `research/legacy_dengue_reproduced/`. Robustness results are written to `research/robustness_v11/` unless `--output` is provided. The `_v11` filename identifies an unchanged analysis design, not a different release number.

## Rebuild primary input from the original workbook
```bash
python scripts/rebuild_eda_from_workbook.py \
  --workbook /LOCAL/PATH/clima_departamento.xlsx \
  --output verification_local/eda_rebuilt.csv
```
The script reads stored cell values using standard-library OOXML parsing, verifies the schema and duplicate keys, selects Piura/EDA total/2018–2025, and preserves blanks. It does not evaluate formulas or modify the workbook. Release verification found all 3,344 resulting rows equal to the distributed CSV.

## Repeat the regional audit locally
```bash
python research/regional_dengue_timing_audit.py \
  --csv /LOCAL/PATH/dataset_dengue_actualizado.csv \
  --output verification_local/regional
python research/methodological_robustness_v11.py \
  --regional-csv /LOCAL/PATH/dataset_dengue_actualizado.csv \
  --output verification_local/robustness
```
No patient-level data are copied to outputs. Preserve the original data dictionary when interpreting `FECHA_NOTIFICACION`. Thresholds are sensitivity choices, not clinically certified validity limits.

## Integrity and browser checks
`python scripts/check_manifest.py` checks all release file hashes. The browser harness, when Playwright is installed, loads the exact bundled HTML and JavaScript into Chromium to test controls. A direct hosted URL still needs testing after GitHub Pages deployment. Source-site availability, final Devpost form eligibility and external account publishing are outside offline tests.
