# Release verification record — 1.2
Prepared 27 October 2026. This is an execution record, not a peer-review certificate.

## Completed checks
| Check | Observed result |
|---|---|
| Primary EDA workbook extraction | 3,344 rows exactly matched the bundled province-week CSV |
| EDA forest refit | Both saved prediction and metric tables reproduced exactly |
| Bootstrap and date sensitivity | Four CSVs and cluster-uncertainty JSON reproduced exactly |
| Regional aggregate audit | Three province/distribution/monthly CSVs reproduced exactly |
| Auxiliary historical dengue refit | Combined MAE reproduced: 805.9 persistence; 925.7 case-only; 911.5 climate |
| Automated consistency suite | 10 tests passed |
| JavaScript syntax | Every bundled JS file passed Node syntax checking |
| Chromium interface checks | 7 dynamic sections, 71 selector-option changes, separate evidence page; no JavaScript exceptions |
| Mobile initial viewport | 390 px viewport; 390 px document width after long-code wrapping fix |
| Missingness presentation | 2025 Piura shows 4 weeks with incomplete observed climate, including humidity |
| Documents | Brief 1 page; research note 4 pages; private guide 2 pages; editable Devpost text 2 rendered pages; all visually reviewed |
| Demo video | Actual scripted interface demonstration; 123.12 s, H.264, 1280 x 840; English captions, no audio |
| Privacy scope | No original case-level regional or national health CSVs distributed |

The browser loads the exact bundled HTML and JavaScript into Chromium using a DOM harness. Direct local URL navigation is blocked in the preparation environment. This does not establish that a future hosted deployment, account-side video link or Safari navigation has passed. Individual selector options were tested; all possible combinations were not exhaustively tested.

## Reproduction scope
Run `python -m unittest discover -s tests -v`; see REPRODUCIBILITY.md for fitting and audit commands. The optional `tests/browser_smoke.py` provides a smaller repeatable DOM smoke test. `scripts/check_manifest.py` checks immutable release hashes. CI is configured but no successful remote GitHub Actions run is claimed before publication.

## Remaining release gates
The final Devpost rules and Additional info form were not accessible during preparation. Generic Devpost instructions were consulted, but event-specific eligibility, time limits, required files, AI declarations and deadlines must be checked in the participant account. GitHub repository, Pages and video URLs do not exist merely because the files exist. Publish and verify access, then submit separately.

The package has no secrets or original individual case files. Upstream data terms are source-specific; the code licence is not a blanket permission for government data. The report does not certify all upstream redistribution conditions.

## Scientific limits remain
Repeated inspection of evaluation years, complete-case selection, uncertain historical reporting vintages, correlated province-year clusters, unresolved source-date semantics and contextual 2026 maps limit interpretation. No prospective accuracy, causal effect, clinical value, official collaboration, prize or submission status is claimed.
