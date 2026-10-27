# Model card and analysis protocol — release 1.2

## Purpose and target
This is an exploratory retrospective benchmark, not a deployable prediction service. The primary outcome is the **reported all-age EDA count for province p at source epidemiological week t+4**. The target is one future week's count, not the sum of the next four weeks. Source year/week labels are retained; no independent calendar reconstruction is claimed.

## Data and sample selection
The CDC Observatorio workbook supplies 3,344 province-week rows, 2018–2025, across Ayabaca, Huancabamba, Morropon, Paita, Piura, Sechura, Sullana and Talara. EDA annual provincial sums agree with participant-supplied CDC annual age-group totals in 2020–2025. The province table, not a zero-filled reconstruction of district records, is the input.

For origin t, the script requires same-year observations at t, t−1, t−2, t−3 and t−4, a target at t+4, and the same target week in the previous year. The current/lagged case and weather fields, target and previous-year value must be present. Selection checks all five lagged tmean/humr/ptot triplets and three climate-reference fields, even though the actual fitted feature subset is smaller. This is a conservative legacy complete-case rule, not an optimized missing-data method.

Rows spanning year boundaries are excluded. The resulting train set has **1,408 rows (2019–2022)**; evaluation has **352 in 2023, 352 in 2024 and 288 in 2025**. Four missing humidity weeks in 2025 affect eight forecast origins per province. The selected evaluation therefore does not cover every calendar week. This eligibility restriction is applied identically to all five methods.

## Features
EDA-only: five current/lagged counts, mean of the current and preceding three counts, the previous-year count for the target week, sine/cosine of the origin week with period 52.18, and eight province indicators (17 features).

Climate-augmented: the same 17 features plus current mean temperature, relative humidity and precipitation; four-week precipitation sum and mean temperature; and current temperature and precipitation departures from the source's climatological reference (24 features). No weather after origin t is used. Source climatology and reporting availability were not reconstructed as real-time historical vintages; this is not an operational backtest.

## Models and evaluation
Both Random Forests use 140 trees, maximum depth 12, minimum leaf size 5, random seed 42 and n_jobs=2. They fit the same training rows. No claim is made that these settings are optimal. Comparators are persistence, trailing four-week mean and previous-year target week. Aggregate MAE weights each retained province-week equally; larger-count provinces can still dominate absolute errors. RMSE and province/year results are also distributed. No random train/test split is used.

The 2023–2025 evaluation was already inspected in earlier experiments. Accordingly all comparisons, subgroup analyses and subsequent sensitivity checks are exploratory. A future assessment should freeze the protocol and use genuinely new observations or independent regions.

## Matched results
MAE: persistence 45.088; four-week mean 46.673; climate forest 50.294; EDA-only forest 52.763; seasonal naive 71.954. Climate-forest minus persistence MAE = +5.206. Lower is better. There is no demonstrated overall gain over persistence.

Paired uncertainty: 5,000 draws resampling the 24 complete province-year sequences, seed 20261027; approximate percentile interval −0.474 to +13.349. This retains within-cluster serial structure but assumes more independence between clusters than may be justified. It is neither a prospective interval for a future week's outcome nor a formal equivalence test.

## Supplementary analyses (separate from the primary model)
**Historical dengue benchmark:** Piura department-wide counts, train 2018–2022, evaluate 88 rows in 2023–2024; two 200-tree forests fit log1p counts. Combined MAE: persistence 805.9; case-only forest 925.7; climate forest 911.5. This different target/geographic unit is not pooled with EDA performance.

**Seasonal-reference exceedances:** compare observed EDA with the 2018–2022 same-week ±2-week historical sample. Week 53 maps to 52; median and 90th percentile are descriptive. Pandemic years remain in this reference. There are no independent outbreak labels; sensitivity, specificity, lead time and clinical benefit cannot be estimated from these plots.

**Regional dengue date audit:** ANO is used as the supplied cohort code. FECHA_NOTIFICACION is described in the supplied dictionary as the recorded health-centre attendance date, not verified central notification time. Summaries use nonnegative onset-to-attendance differences with cutoff sensitivity at 30, 60, 90, 180 and 365 days, and a same-calendar-year attendance restriction. A numerically plausible interval is not proof of valid clinical timing. No patient-level files are released.

**Territorial context:** 116 district snapshots and 1,729 active geocoded registry listings are included as contextual inventory, not historical explanatory variables or proof of service capacity. A site inside a susceptible area is not known to be damaged, closed or inaccessible.

## Appropriate and inappropriate use
Appropriate: teaching, reviewing source consistency, reproducing published calculations, exploring hypotheses.
Inappropriate: clinical advice, resource-allocation decisions, outbreak declaration, automated triage, claims about causal effects of El Nino, or any validated 2027 prediction.
