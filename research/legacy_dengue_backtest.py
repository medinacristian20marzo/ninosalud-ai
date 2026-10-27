"""Experimental four-week-ahead dengue forecasting benchmark for Piura.
Train years: 2018-2022; test years: 2023 and 2024.
No random train/test split, no CENEPRED 2026 features, no future climate features.
Two ML variants: +climate vs case-count-only, persistence baseline.
This is a research benchmark, not a live public-health alert.
"""
import csv, collections, math, json, pathlib
import numpy as np
from sklearn.ensemble import RandomForestRegressor
ROOT=pathlib.Path(__file__).resolve().parents[1]
O=ROOT/'research'/'legacy_dengue_reproduced'; O.mkdir(exist_ok=True)
epi={};clim={}
with (ROOT/'data'/'legacy_dengue_inputs_2018_2024.csv').open(encoding='utf-8',newline='') as f:
 for r in csv.DictReader(f):
  key=(int(r['ano']),int(r['semana']))
  epi[key]={'dengue_notifications':int(r['dengue_notifications'])}
  clim[key]={'tmean':float(r['tmean']),'ptot':float(r['ptot'])}
features=[];years=[];weeks=[];targets=[];baselines=[];future=[]
for y in range(2018,2025):
 countweeks=53 if y==2020 else 52
 for w in range(5,countweeks-3):
  dates=[(y,w-j) for j in range(4)]
  if any(key not in clim or key not in epi for key in dates) or (y,w+4) not in epi:continue
  now=[epi[key]['dengue_notifications'] for key in dates]
  rains=[clim[key]['ptot'] for key in dates]
  temps=[clim[key]['tmean'] for key in dates]
  basic=[math.log1p(now[0]),math.log1p(sum(now)/4),math.log1p(now[1]),math.log1p(now[3]),math.sin(2*math.pi*w/52.18),math.cos(2*math.pi*w/52.18)]
  extra=[math.log1p(max(0,rains[0])),math.log1p(max(0,sum(rains)/4)),temps[0],sum(temps)/4]
  features.append((basic,extra));years.append(y);weeks.append(w);targets.append(epi[(y,w+4)]['dengue_notifications']);baselines.append(now[0])
features=np.array([a+b for a,b in features]);yeara=np.array(years);targeta=np.array(targets);pers=np.array(baselines)
train=yeara<=2022;test=yeara>=2023
print('examples total',len(targets),'training',train.sum(),'testing',test.sum())
models={}
for variant,columns in [('case_only',6),('climate_plus_case',10)]:
 model=RandomForestRegressor(n_estimators=200,min_samples_leaf=3,max_features=1.0,random_state=42,n_jobs=-1)
 model.fit(features[train,:columns],np.log1p(targeta[train]));pred=np.expm1(model.predict(features[test,:columns]));pred=np.maximum(pred,0)
 models[variant]=pred
with (O/'forecast_backtest_2023_2024.csv').open('w',encoding='utf-8',newline='') as f:
 w=csv.writer(f);w.writerow(['year','predictor_week','target_week_plus4','observed_dengue_notifications','persistence_prediction','ML_case_only_prediction','ML_case_climate_prediction'])
 for i,idx in enumerate(np.where(test)[0]):w.writerow([years[idx],weeks[idx],weeks[idx]+4,int(targeta[idx]),int(pers[idx]),round(models['case_only'][i],1),round(models['climate_plus_case'][i],1)])
metrics={};
for y in [2023,2024,'combined']:
 local=(yeara[test]==y) if y!='combined' else np.ones(test.sum(),dtype=bool)
 obs=targeta[test][local];s=pers[test][local]
 metrics[str(y)]={'observations':len(obs),'observed_notifications_sum':int(obs.sum()),'persistence_MAE':round(float(np.mean(abs(s-obs))),1)}
 for name,p in models.items():
  pp=p[local];metrics[str(y)][f'{name}_MAE']=round(float(np.mean(abs(pp-obs))),1)
  metrics[str(y)][f'{name}_WAPE']=round(float(100*np.sum(abs(pp-obs))/max(1,np.sum(obs))),1)
 metrics[str(y)]['persistence_WAPE']=round(float(100*np.sum(abs(s-obs))/max(1,np.sum(obs))),1)
report={'method':'4 epidemiological weeks ahead; model uses current and preceding 3 weeks of dengue reports and observed rain/temp; train 2018-2022, held-out test 2023 and 2024','units':'weekly reported records, not confirmed cases or individual risk','warning':'District-level climate is population-weighted across Piura; historical surveillance can be revised and differs across years. Experimental not clinical, causal or real-time.','n_train':int(train.sum()),'n_test':int(test.sum()),'metrics':metrics}
(O/'model_backtest_metrics.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
