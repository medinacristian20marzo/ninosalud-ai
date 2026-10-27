# Distributed analytical data: reading guide

## Primary EDA input
`data/eda_clima_piura_provincia_semanal_2018_2025.csv` contains one province-year-epidemiological-week record. `departamento` and `provincia` identify the geographic unit. `ano` and `semana` are source epidemiological labels. `casos` is all-age reported diarrheal episodes, not laboratory diagnoses or unique patients. `tmean`, `tmax`, `tmin` are source weekly temperature fields; `humr` is relative humidity; `ptot` is weekly precipitation. Fields ending `_clima` are supplied historical reference fields. Blank observed humidity is preserved; no blank is silently made zero. For exact units and construction, consult the CDC source documentation linked in DATA_SOURCES.md.

## Predictions and metrics
`eda_climate_ablation_predictions_2023_2025.csv` preserves the same province and target-week sample for all five methods. Error metrics are in reported episodes per province-week, not percentages or clinical accuracy. `eda_climate_ablation_metrics.csv` includes overall and year-level summaries. See MODEL_CARD.md for exact feature definitions and eligibility rules.

## Regional dengue summaries
`regional_dengue_*` files and `research/robustness_v11/dengue_2025_*` contain aggregates, not individual records. Counts are not necessarily confirmed cases or distinct patients. Year-coded cohorts are not always calendar-year attendance cohorts. Dates and exclusion windows are described in MODEL_CARD.md.

## Territorial context
District shapes and counts are archived JSON/JavaScript extracts from CENEPRED, INEI and RENIPRESS sources. A registered active facility is not a measured service capacity. Risk classes are physical exposure/context classifications, not probabilities of infection.

## Reproducibility and provenance
SOURCE_FILE_HASHES.json identifies the original inputs retained outside this public repository. PROVENANCE.json records the public analytical release. Source-specific rights are not replaced by the software MIT licence.
