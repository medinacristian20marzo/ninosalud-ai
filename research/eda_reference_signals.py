"""Retrospective seasonal reference, NOT an operational outbreak alert.
Only 2018-2022 reference data, 2023-2025 inspection. Weekly 90th percentile
from matching calendar week +/- 2 using 5 years, 25 values.
"""
from pathlib import Path
from collections import defaultdict
from statistics import median
import csv, math
dest=Path(__file__).resolve().parent.parent
source=dest/'data'/'eda_clima_piura_provincia_semanal_2018_2025.csv'
rows=list(csv.DictReader(source.open(encoding='utf-8',newline='')))
provinces=sorted(set(r['provincia'] for r in rows))
byprov=defaultdict(list)
for r in rows:
    byprov[r['provincia']].append({'year':int(r['ano']),'week':int(r['semana']),'count':int(r['casos'])})

def quantile(vals,frac):
    s=sorted(vals); x=(len(s)-1)*frac; lo=math.floor(x); hi=math.ceil(x)
    return s[lo]*(hi-x)+s[hi]*(x-lo) if hi!=lo else float(s[lo])

def circ_week(w):
    return min(52,w)

def near(w,q):
    w=circ_week(w);q=circ_week(q)
    d=abs(w-q)
    return min(d,52-d)<=2

signal_rows=[]
for p in provinces:
    reference=[r for r in byprov[p] if 2018<=r['year']<=2022]
    assert len(reference)>=260
    for r in sorted(byprov[p], key=lambda q:(q['year'],q['week'])):
        if r['year']<2023: continue
        candidates=[q['count'] for q in reference if near(q['week'],r['week'])]
        assert len(candidates)>=24, (p,r,len(candidates))
        base=median(candidates)
        q75=quantile(candidates,.75)
        q90=quantile(candidates,.90)
        signal_rows.append({'province':p,'year':r['year'],'week':r['week'],
                            'reported_episodes':r['count'], 'reference_median':round(base,2),
                            'reference_q75':round(q75,2),'reference_q90':round(q90,2),
                            'above_reference_q90':int(r['count']>q90),
                            'ratio_to_q90':round(r['count']/q90,3) if q90>0 else '',
                            'reference_sample_n':len(candidates)})

fields=list(signal_rows[0])
outpath=dest/'data'/'eda_piura_reference_signals_2023_2025.csv'
with outpath.open('w',encoding='utf-8',newline='') as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(signal_rows)

summary=[]
for p in provinces:
 for y in (2023,2024,2025):
  group=[r for r in signal_rows if r['province']==p and r['year']==y]
  summary.append({'province':p,'year':y,'weeks':len(group),
                  'weeks_above_q90':sum(r['above_reference_q90'] for r in group),
                  'share_above_q90':round(sum(r['above_reference_q90'] for r in group)/len(group),3),
                  'max_ratio_to_q90':max(float(r['ratio_to_q90']) for r in group if r['ratio_to_q90']!='')})
spath=dest/'data'/'eda_piura_reference_signals_summary.csv'
with spath.open('w',encoding='utf-8',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(summary[0]));w.writeheader();w.writerows(summary)

