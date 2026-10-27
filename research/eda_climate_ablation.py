"""Exploratory retrospective climate-feature ablation for NinoSalud AI.
Same eligible province-weeks, fixed algorithm and hyperparameters.
No diagnostic, public health or prospective validation claim.
"""
import csv, math, json, os
from collections import defaultdict
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC=os.path.join(ROOT,'data','eda_clima_piura_provincia_semanal_2018_2025.csv')
OUT=os.path.join(ROOT,'research','ablation_reproduced')
os.makedirs(OUT,exist_ok=True)
with open(SRC,encoding='utf-8',newline='') as f:
    rows={}
    for r in csv.DictReader(f):
        rows[r['provincia'],int(r['ano']),int(r['semana'])]=r
provinces=sorted(set(p for p,y,w in rows))

def val(r,k):
    try: return float(r[k]) if r[k] not in ('',None) else None
    except: return None

X_no_climate=[];X_with_climate=[];Y=[];bs_last=[];bs_last4=[];bs_year=[];years=[];prov=[];ww=[]
for (p,y,t),r in sorted(rows.items()):
    if not 2019<=y<=2025 or (p,y,t+4) not in rows or (p,y-1,t+4) not in rows: continue
    lag=[rows.get((p,y,t-i)) for i in range(5)]
    if any(q is None for q in lag): continue
    epi=[val(q,'casos') for q in lag]
    clim=[val(q,k) for q in lag for k in ('tmean','humr','ptot')]
    tar=val(rows[p,y,t+4],'casos')
    prior=val(rows[p,y-1,t+4],'casos')
    clim_reference=[val(lag[0],k) for k in ('tmean_clima','humr_clima','ptot_clima')]
    if any(v is None for v in epi+clim+[tar,prior]+clim_reference):continue
    seasonal=[math.sin(2*math.pi*t/52.18),math.cos(2*math.pi*t/52.18)]
    geo=[float(p==q) for q in provinces]
    nclim=epi+[sum(epi[:4])/4,prior]+seasonal+geo
    cl=clim[:3]+[sum(clim[z*3+2] for z in range(4)),sum(clim[z*3] for z in range(4))/4]+[clim[0]-clim_reference[0],clim[2]-clim_reference[2]]
    X_no_climate.append(nclim);X_with_climate.append(nclim+cl)
    Y.append(tar);bs_last.append(epi[0]);bs_last4.append(sum(epi[:4])/4);bs_year.append(prior)
    years.append(y);prov.append(p);ww.append(t+4)
Y=np.array(Y);years=np.array(years); X_no_climate=np.asarray(X_no_climate);X_with_climate=np.asarray(X_with_climate)
bs_last=np.array(bs_last);bs_last4=np.array(bs_last4);bs_year=np.array(bs_year)
train=years<=2022; test=years>=2023
config=dict(n_estimators=140,max_depth=12,min_samples_leaf=5,random_state=42,n_jobs=2)
model_epi=RandomForestRegressor(**config).fit(X_no_climate[train],Y[train]);p_epi=np.maximum(0,model_epi.predict(X_no_climate))
model_clim=RandomForestRegressor(**config).fit(X_with_climate[train],Y[train]);p_clim=np.maximum(0,model_clim.predict(X_with_climate))
models={'Last observed week':bs_last,'Four-week trailing mean':bs_last4,'Same week prior year':bs_year,'Random Forest - EDA only':p_epi,'Random Forest - EDA + observed climate':p_clim}
rows_metrics=[]
for label,mask in [('2019-2022 training',train),('2023-2025 exploratory holdout',test),('2023',years==2023),('2024',years==2024),('2025',years==2025)]:
    for name,pred in models.items():
        rows_metrics.append({'period':label,'model':name,'n':int(mask.sum()),'MAE':round(float(mean_absolute_error(Y[mask],pred[mask])),3),'RMSE':round(float(np.sqrt(mean_squared_error(Y[mask],pred[mask]))),3)})
with open(os.path.join(OUT,'eda_climate_ablation_metrics.csv'),'w',encoding='utf-8',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows_metrics[0]));w.writeheader();w.writerows(rows_metrics)
with open(os.path.join(OUT,'eda_climate_ablation_predictions_2023_2025.csv'),'w',encoding='utf-8',newline='') as f:
    fields=['province','year','target_week','observed','last_week','trailing_4week_avg','same_week_prior_year','RF_EDA_only','RF_EDA_plus_climate']
    w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
    for i in np.where(test)[0]:
        w.writerow(dict(zip(fields,[prov[i],int(years[i]),int(ww[i]),Y[i],round(bs_last[i],2),round(bs_last4[i],2),round(bs_year[i],2),round(p_epi[i],2),round(p_clim[i],2)])))
with open(os.path.join(OUT,'experiment_manifest.json'),'w') as f:
    json.dump({'records_train':int(train.sum()),'records_test':int(test.sum()),'model_hyperparameters':config,'models':list(models),'features_EDA_only':X_no_climate.shape[1],'features_EDA_and_climate':X_with_climate.shape[1],'years_training':[2019,2020,2021,2022],'years_evaluation':[2023,2024,2025], 'important':'Exploratory retrospective ablation only. The 2023-2025 holdout was previously inspected for the original RF; not a fresh untouched test. Does not evaluate clinical value, threshold sensitivity, or prospective performance.'},f,indent=2)
print('Train:',int(train.sum()),'test:',int(test.sum()))
for a in rows_metrics:
    if a['period'] in ('2023-2025 exploratory holdout','2023','2024','2025'):
        print(a)
