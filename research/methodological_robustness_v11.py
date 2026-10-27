#!/usr/bin/env python3
"""NinoSalud 1.1: reproducible exploratory audit of matched forecasting
and the GORE Piura dengue 2025 onset-to-recorded-attendance interval.

Requires only Python standard library. User-supplied regional case-level CSV is
NOT copied or exported. All published summaries are province-level aggregates.

Examples:
 python research/methodological_robustness_v11.py --regional-csv /path/dataset_dengue_actualizado.csv
 python research/methodological_robustness_v11.py --no-regional
"""
import argparse, csv, collections, datetime as dt, json, random, statistics
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PROVINCES=('AYABACA','HUANCABAMBA','MORROPON','PAITA','PIURA','SECHURA','SULLANA','TALARA')
THRESHOLDS=(30,60,90,180,365)


def write_csv(path, rows):
    if not rows: raise ValueError('No rows: '+str(path))
    with path.open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0].keys()))
        writer.writeheader();writer.writerows(rows)


def read_date(s):
    try: return dt.datetime.strptime(s,'%Y%m%d').date()
    except (ValueError,TypeError): return None


def percentile(seq,p):
    if not seq: return None
    vals=sorted(seq)
    return vals[round((len(vals)-1)*p)]


def median(seq):
    return statistics.median(seq) if seq else None


def forecast_analysis(output,seed=20261027,bootstrap=5000):
    path=ROOT/'data'/'eda_climate_ablation_predictions_2023_2025.csv'
    obs=[]; groups=collections.defaultdict(list)
    with path.open(encoding='utf-8',newline='') as f:
        for r in csv.DictReader(f):
            o=float(r['observed']);p=float(r['last_week']);e=float(r['RF_EDA_only']);c=float(r['RF_EDA_plus_climate'])
            record={'province':r['province'],'year':int(r['year']),'target_week':int(r['target_week']),
                    'abs_persistence':abs(o-p),'abs_eda_rf':abs(o-e),'abs_climate_rf':abs(o-c),
                    'observed':o,'last_week':p,'eda_rf':e,'climate_rf':c}
            obs.append(record);groups[(record['province'],record['year'])].append(record)
    keys=[(r['province'],r['year'],r['target_week']) for r in obs]
    assert len(keys)==len(set(keys)), 'duplicate province-year-target_week rows'
    assert len(obs)==992 and len(groups)==24,'Unexpected archived experimental evaluation sample'
    def mae(rows,key):return sum(r[key] for r in rows)/len(rows)
    aggregate=[]
    for label,rows in [('2023-2025',obs)]+[(str(y),[r for r in obs if r['year']==y]) for y in (2023,2024,2025)]:
        mp=mae(rows,'abs_persistence');me=mae(rows,'abs_eda_rf');mc=mae(rows,'abs_climate_rf')
        aggregate.append(dict(period=label,n=len(rows),persistence_MAE=round(mp,3),EDA_only_RF_MAE=round(me,3),climate_RF_MAE=round(mc,3),climate_RF_minus_persistence_MAE=round(mc-mp,3),climate_RF_minus_EDA_only_RF_MAE=round(mc-me,3)))
    write_csv(output/'forecast_matched_evaluation.csv',aggregate)
    province=[]
    for (p,y),rows in sorted(groups.items()):
        mp=mae(rows,'abs_persistence');me=mae(rows,'abs_eda_rf');mc=mae(rows,'abs_climate_rf')
        province.append(dict(province=p,year=y,n=len(rows),persistence_MAE=round(mp,3),EDA_only_RF_MAE=round(me,3),climate_RF_MAE=round(mc,3),climate_RF_minus_persistence_MAE=round(mc-mp,3)))
    write_csv(output/'forecast_province_year_evaluation.csv',province)

    rng=random.Random(seed)
    cluster_keys=list(groups.keys());pairs=[]
    # Resample whole province-year sequences to avoid treating adjacent
    # epidemiological weeks as independent. Still exploratory: only 24 clusters.
    for _ in range(bootstrap):
        sampled=[groups[cluster_keys[rng.randrange(len(cluster_keys))]] for _ in cluster_keys]
        a=b=c=n=0
        for g in sampled:
            n+=len(g)
            a+=sum(r['abs_persistence'] for r in g)
            b+=sum(r['abs_eda_rf'] for r in g)
            c+=sum(r['abs_climate_rf'] for r in g)
        pairs.append(((c-a)/n,(c-b)/n))
    def ci(vals):
        s=sorted(vals);return [round(s[int((len(s)-1)*q)],3) for q in (.025,.975)]
    point_p=aggregate[0]['climate_RF_minus_persistence_MAE']
    point_e=aggregate[0]['climate_RF_minus_EDA_only_RF_MAE']
    unc={'dataset':'Matched historic forecasts (archived 2023-2025 test; previously inspected)',
         'bootstrap':'resampling entire province-year clusters with replacement',
         'cluster_count':len(groups),'n_rows':len(obs),'bootstrap_iterations':bootstrap,'random_seed':seed,
         'climate_RF_minus_persistence_MAE':point_p,'CI95_cluster_bootstrap_climate_RF_minus_persistence_MAE':ci([p[0] for p in pairs]),
         'climate_RF_minus_EDA_only_RF_MAE':point_e,'CI95_cluster_bootstrap_climate_RF_minus_EDA_only_RF_MAE':ci([p[1] for p in pairs]),
         'limitations':['Only 24 province-year clusters, possibly correlated between provinces and years.',
                        'Intervals are approximate, not clinical or prospective validation.',
                        'Holdout has already been inspected, so comparisons are exploratory.',
                        'No choice of model or threshold should be justified by this dataset alone.']}
    (output/'forecast_cluster_uncertainty.json').write_text(json.dumps(unc,indent=2),encoding='utf-8')
    return aggregate,unc


def dengue_analysis(input_path,output):
    data=collections.defaultdict(list);issues=collections.Counter();cut=collections.Counter();years=collections.Counter()
    required={'ANO','DEPARTAMENTO','PROVINCIA','UBIGEO','FECHA_INICIO_SINTOMAS','FECHA_NOTIFICACION','FECHA_CORTE','FECHA_INGRESO'}
    with Path(input_path).open(newline='',encoding='utf-8-sig') as f:
        rd=csv.DictReader(f)
        if not required.issubset(rd.fieldnames):raise ValueError('Required fields absent: '+str(required-set(rd.fieldnames)))
        for r in rd:
            if r['ANO']!='2025': continue
            if r['DEPARTAMENTO']!='PIURA' or r['PROVINCIA'] not in PROVINCES or not (r['UBIGEO'].startswith('20') and len(r['UBIGEO'])==6):
                issues['2025_rows_other_geography']+=1;continue
            p=r['PROVINCIA']; onset=read_date(r['FECHA_INICIO_SINTOMAS']);visit=read_date(r['FECHA_NOTIFICACION']);entry=read_date(r['FECHA_INGRESO'])
            delay=(visit-onset).days if onset and visit else None
            data[p].append({'days':delay,'visit_in_year':bool(visit and visit.year==2025), 'entry_before':bool(entry and visit and entry<visit),'valid_dates':bool(onset and visit)})
            years['records']+=1
            cut[r['FECHA_CORTE']]+=1
    out=[];quality=[]
    for p in PROVINCES:
        rr=data[p]; known=[x['days'] for x in rr if x['days'] is not None]
        valid=[x for x in known if x>=0]
        quality.append(dict(province=p,year=2025,raw_rows=len(rr),missing_or_invalid_dates=len(rr)-len(known),negative_onset_to_visit=sum(x<0 for x in known),
            positive_over_90=sum(x>90 for x in known),entry_before_visit=sum(x['entry_before'] for x in rr),visit_outside_2025=sum(not x['visit_in_year'] for x in rr)))
        for cutoff in THRESHOLDS:
            a=[x for x in valid if x<=cutoff]
            sam=[x['days'] for x in rr if x['days'] is not None and 0<=x['days']<=cutoff and x['visit_in_year']]
            out.append(dict(province=p,cohort_year=2025,max_interval_days=cutoff,total_rows=len(rr),valid_observations=len(a),excluded_above_cutoff=sum(x>cutoff for x in valid),median_days=median(a),p90_days=percentile(a,.9),within_7_pct=round(100*sum(x<=7 for x in a)/len(a),2) if a else None,
                same_calendar_year_n=len(sam),same_calendar_year_median_days=median(sam)))
    write_csv(output/'dengue_2025_sensitivity.csv',out)
    write_csv(output/'dengue_2025_quality_by_province.csv',quality)
    a={'year':'2025 year-coded data ONLY','scoped_rows':years['records'],'cut_dates':dict(cut),'sensitivity_thresholds_days':list(THRESHOLDS),
       'source_denomination':'reported regional confirmed plus possible dengue records, no diagnostic status in CSV',
       'variable_meaning':'FECHA_NOTIFICACION defined by source dictionary as visit to health centre',
       'privacy':'only province-level summaries exported; no raw person-level records in release',
       'warning':'The interval is neither a validated attendance delay nor a report lag. Thresholds are exploratory, not clinical cutoffs. Within-year restriction is an additional sensitivity check.'}
    (output/'dengue_2025_manifest.json').write_text(json.dumps(a,indent=2),encoding='utf-8')
    return out, quality

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--regional-csv',help='Local raw regional file, never included in output')
    parser.add_argument('--no-regional',action='store_true',help='Skip case-level regional analysis')
    parser.add_argument('--output',default=str(ROOT/'research'/'robustness_v11'))
    args=parser.parse_args()
    output=Path(args.output);output.mkdir(parents=True,exist_ok=True)
    res,unc=forecast_analysis(output)
    print('Matched forecast results:',res[0]);print('Cluster uncertainty:',unc)
    if args.regional_csv and not args.no_regional:
        d,q=dengue_analysis(args.regional_csv,output)
        for p in ('PIURA','HUANCABAMBA'):
            print(p,[(r['max_interval_days'],r['valid_observations'],r['median_days']) for r in d if r['province']==p])
    else:
        print('Regional audit not run: provide --regional-csv path to reproduce local only')
