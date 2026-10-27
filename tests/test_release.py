"""Release checks from distributed aggregate data; no patient-level input required."""
import csv,json,math,re,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def rows(name):
    with (ROOT/'data'/name).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))
def payload(name):return json.loads((ROOT/'app'/name).read_text(encoding='utf-8').split('=',1)[1].strip().rstrip(';'))

class ReleaseChecks(unittest.TestCase):
    def test_province_week_uniqueness(self):
        r=rows('eda_clima_piura_provincia_semanal_2018_2025.csv')
        self.assertEqual(len(r),3344)
        self.assertEqual(len({(x['provincia'],x['ano'],x['semana']) for x in r}),3344)
        self.assertEqual(len({x['provincia'] for x in r}),8)
    def test_annual_totals_reconcile(self):
        r=rows('eda_clima_piura_provincia_semanal_2018_2025.csv')
        age=rows('eda_piura_cdc_annual_agegroups_2020_2025.csv')
        for x in age:
            total=sum(int(q['casos']) for q in r if q['ano']==x['year'])
            self.assertEqual(total,int(x['all_episodes']))
            self.assertEqual(total,int(x['under5_episodes'])+int(x['age5plus_episodes']))
    def test_missing_humidity_preserved(self):
        r=rows('eda_clima_piura_provincia_semanal_2018_2025.csv')
        missing=[x for x in r if any(x[k]=='' for k in ('tmean','humr','ptot'))]
        self.assertEqual(len(missing),32)
        self.assertEqual({(x['ano'],x['semana']) for x in missing},{('2025',str(w)) for w in range(19,23)})
    def test_prediction_sample(self):
        r=rows('eda_climate_ablation_predictions_2023_2025.csv')
        self.assertEqual(len(r),992)
        self.assertEqual(len({(x['province'],x['year'],x['target_week']) for x in r}),992)
        self.assertEqual({int(x['year']) for x in r},{2023,2024,2025})
        for x in r:
            self.assertGreaterEqual(int(x['target_week'])-4,5)
            self.assertTrue(all(math.isfinite(float(x[k])) for k in ('observed','last_week','RF_EDA_only','RF_EDA_plus_climate')))
    def test_metrics_from_predictions(self):
        r=rows('eda_climate_ablation_predictions_2023_2025.csv')
        pairs={'Last observed week':'last_week','Four-week trailing mean':'trailing_4week_avg','Same week prior year':'same_week_prior_year','Random Forest - EDA only':'RF_EDA_only','Random Forest - EDA + observed climate':'RF_EDA_plus_climate'}
        m=rows('eda_climate_ablation_metrics.csv')
        for label,k in pairs.items():
            score=sum(abs(float(x['observed'])-float(x[k])) for x in r)/len(r)
            ref=next(x for x in m if x['period']=='2023-2025 exploratory holdout' and x['model']==label)
            self.assertAlmostEqual(score,float(ref['MAE']),places=3)
    def test_ui_uses_same_forecasts(self):
        q=payload('eda_explorer_data.js');r=rows('eda_climate_ablation_predictions_2023_2025.csv')
        lookup={(x['province'],int(x['year']),int(x['target_week'])):x for x in r}
        self.assertEqual(len(q['predictions']),992)
        for p in q['predictions']:
            self.assertAlmostEqual(p['rf'],float(lookup[p['p'],p['y'],p['w']]['RF_EDA_plus_climate']),places=8)
        self.assertEqual(sum(v['humidity'] is None for v in q['series']),32)
    def test_sensitivity_results(self):
        with (ROOT/'research/robustness_v11/dengue_2025_sensitivity.csv').open() as f:r=list(csv.DictReader(f))
        pi=[float(x['median_days']) for x in r if x['province']=='PIURA']
        hu=[float(x['median_days']) for x in r if x['province']=='HUANCABAMBA']
        self.assertEqual(pi,[3,3,3,3,3]);self.assertEqual(hu,[5,10,15,18,19])
    def test_raw_case_files_absent(self):
        prohibited={'dataset_dengue_actualizado.csv','datos_abiertos_vigilancia_dengue_2000_2025_0.csv','datos_abiertos_vigilancia_edas_2000_2024.csv'}
        self.assertFalse(any(p.name in prohibited for p in ROOT.rglob('*') if p.is_file()))
    def test_territorial_snapshot_sizes(self):
        d=payload('dashboard_data.js')
        self.assertEqual(len(d['risk']),116);self.assertEqual(len(d['active_facilities']),1729)
        self.assertEqual(len(d['geometry']),116)
    def test_nonclinical_scope_visible(self):
        h=(ROOT/'app/index.html').read_text(encoding='utf-8')
        self.assertIn('not an operational warning system',h)
        self.assertIn('offline in Python',h)
        self.assertIn('AI-assisted',h)
if __name__=='__main__':unittest.main()
