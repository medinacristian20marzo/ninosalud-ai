# Data sources and provenance

All data were supplied during project development from public Peruvian portals. This release verifies the supplied local snapshots; it does not certify that they are the newest online versions. The original-file SHA-256 fingerprints are recorded in `data/SOURCE_FILE_HASHES.json`.

| ID | Source and supplied material | Scope and use | Main caveat |
|---|---|---|---|
| S1 | CDC Peru, Observatorio de Clima y Salud; `clima_departamento.xlsx` | Province-week all-age EDA with weather, 2018–2025 for primary study | Missing humidity in weeks 19–22 of 2025; source week labels retained |
| S2 | CDC Peru, Sala Situacional EDA; exported age-group indicator tables and participant-pasted 2025 table | Annual reconciliation, Piura | Annual summaries cannot reconstruct missing weekly counts |
| S3 | MINSA dengue surveillance CSV 2000–2025 | Historical counts and auxiliary dengue benchmark | Absence of records is not proof of zero infections; status fields and vintages differ |
| S4 | MINSA historical EDA and zoonosis CSVs 2000–2024 | Legacy disease-history comparison and source discrepancy audit | 2024 age-5+ EDA zero sequence conflicts with updated CDC export |
| S5 | GORE Piura `dataset_dengue_actualizado.csv` and `Formato_DiccionarioDatos_DENGUE_0.xlsx` | Recorded date-interval audit, cohorts 2023, 2025, partial 2026 | Not homogeneous annual coverage; no per-row diagnostic-status field; chronology conflicts |
| S6 | CENEPRED risk tables/shapes and data dictionary | Flood/mass-movement snapshots labelled 2026 | Exposure is not an epidemiological forecast or realized damage |
| S7 | INEI district population projections 2018–2026 | Context and older population-weighted climate summary | Not age-specific denominators; district boundaries may change |
| S8 | SUSALUD RENIPRESS September 2026 | Counts of active geocoded facilities | Administrative registration is not measured operational capacity |

## Original catalogue and dashboard links
- S1: https://app7.dge.gob.pe/maps2/shiny_observatorio_web/
- S2: https://app7.dge.gob.pe/maps2/shiny_eda_web/
- S3: https://www.datosabiertos.gob.pe/dataset/vigilancia-epidemiol%C3%B3gica-de-dengue
- S4 EDA: https://www.datosabiertos.gob.pe/dataset/vigilancia-epidemiol%C3%B3gica-de-enfermedad-diarreica-aguda-eda
- S4 zoonoses: https://www.datosabiertos.gob.pe/dataset/vigilancia-epidemiol%C3%B3gica-de-las-zoonosis
- S5: https://www.datosabiertos.gob.pe/dataset/casos-de-dengue-en-la-regi%C3%B3n-piura-gobierno-regional-piura
- S6: https://sigrid.cenepred.gob.pe/sigridv3/documento/22169
- S7: https://www.gob.pe/institucion/inei/informes-publicaciones/6894980-peru-poblacion-total-proyectada-al-30-de-junio-de-cada-ano-segun-departamento-provincia-y-distrito-2018-2026
- S8: https://www.datosabiertos.gob.pe/dataset/registro-nacional-de-entidades-prestadoras-de-servicios-de-salud-renipress

## Evidence hierarchy
The headline model metrics are computed from the bundled province-week CSV and reproduced by the release scripts. The regional timing results are computed from the separately supplied source CSV; only province aggregates are released. Historic map payloads and older source-discrepancy summaries are retained reference extracts; not all original geospatial processing is rebuilt from raw shapefiles by the public quick-start command.

## External methodological references (not data for the models)
- S9. WHO/TDR (2017). *Operational Guide: The Early Warning and Response Systems (EWARS) for Dengue Outbreaks*. ISBN 9789241512053. https://www.who.int/publications/i/item/9789241512053
- S10. US CDC Center for Forecasting and Outbreak Analytics (2026). *How to assess a modeling framework and its results*. https://www.cdc.gov/cfa-modeling-and-forecasting/modeling-handbook/mh-modelappraisal.html

S9 and S10 were accessible during release preparation on 27 October 2026. They motivate careful appraisal; they do not validate NinoSalud or endorse its method. No current ENFEN forecast is reproduced as an established project result.
