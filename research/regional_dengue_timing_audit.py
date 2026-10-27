#!/usr/bin/env python3
"""Privacy-minimizing GORE Piura dengue data audit. Standard library only.

Example: python research/regional_dengue_timing_audit.py --csv /path/dataset.csv --output /tmp/summary

Never publish patient-level records from input; output consists only of province/year aggregates.
"""
import argparse
import collections
import csv
import datetime as dt
import json
import pathlib
import statistics

PROVINCES=('AYABACA','HUANCABAMBA','MORROPON','PAITA','PIURA','SECHURA','SULLANA','TALARA')
COHORTS=('2023','2025','2026')
BANDS=('negative','0','1-2','3-7','8-14','15-30','31-90','>90')

def parsedate(value):
    try: return dt.datetime.strptime(value,'%Y%m%d').date()
    except (TypeError, ValueError): return None

def band(days):
    if days<0:return 'negative'
    if days==0:return '0'
    if days<=2:return '1-2'
    if days<=7:return '3-7'
    if days<=14:return '8-14'
    if days<=30:return '15-30'
    if days<=90:return '31-90'
    return '>90'

def quantile(values,q):
    if not values:return None
    x=sorted(values);return x[round((len(x)-1)*q)]

def export(path,rows):
    with open(path,'w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def audit(csv_path,output):
    output=pathlib.Path(output);output.mkdir(parents=True,exist_ok=True)
    data=collections.defaultdict(lambda:{'counts':collections.Counter(),'delays':[],'bands':collections.Counter()})
    months=collections.Counter();row_year=collections.Counter();cut=collections.Counter();excluded_geo=0;outside_dept=0
    with open(csv_path,newline='',encoding='utf-8-sig') as f:
        reader=csv.DictReader(f)
        fields={'ANO','FECHA_CORTE','DEPARTAMENTO','PROVINCIA','UBIGEO','FECHA_INICIO_SINTOMAS','FECHA_NOTIFICACION','FECHA_INGRESO'}
        assert fields.issubset(set(reader.fieldnames)),f'Absent columns: {fields-set(reader.fieldnames)}'
        for r in reader:
            year=r['ANO'];province=r['PROVINCIA'];dept=r['DEPARTAMENTO'];ub=r['UBIGEO']
            row_year[year]+=1;cut[(year,r['FECHA_CORTE'])]+=1
            if dept!='PIURA':outside_dept+=1
            if year not in COHORTS or dept!='PIURA' or province not in PROVINCES or not (ub.startswith('20') and len(ub)==6):
                excluded_geo+=1;continue
            z=data[(year,province)];z['counts']['rows']+=1
            onset=parsedate(r['FECHA_INICIO_SINTOMAS']);attendance=parsedate(r['FECHA_NOTIFICACION']);entry=parsedate(r['FECHA_INGRESO']);cut_date=parsedate(r['FECHA_CORTE'])
            if not (onset and attendance):z['counts']['missing_or_invalid_dates']+=1;continue
            delay=(attendance-onset).days;z['bands'][band(delay)]+=1
            if delay<0:z['counts']['negative_delay']+=1
            elif delay>90:z['counts']['over90_delay']+=1
            else:
                z['delays'].append(delay)
                if delay>=8:z['counts']['more_than_7']+=1
                if delay>=15:z['counts']['more_than_14']+=1
            if entry and entry<attendance:z['counts']['system_before_visit']+=1
            if entry and entry>attendance:z['counts']['system_after_visit']+=1
            if cut_date and attendance>cut_date:z['counts']['visit_after_cut']+=1
            if attendance.year==int(year):months[(year,province,attendance.month)]+=1
            else:z['counts']['attendance_other_calendar_year']+=1
    summary=[];distribution=[];monthly=[];total=collections.Counter()
    for year in COHORTS:
        for province in PROVINCES:
            z=data[(year,province)];v=z['delays'];n=len(v);c=z['counts'];total.update(c)
            summary.append(dict(cohort_year=int(year),province=province,record_rows=c['rows'],eligible_delay_0_90=n,excluded_negative=c['negative_delay'],excluded_gt90=c['over90_delay'],median_days=statistics.median(v) if v else None,p90_days=quantile(v,.9),within7_count=n-c['more_than_7'],within7_pct=round(100*(n-c['more_than_7'])/n,2) if n else None,over7_count=c['more_than_7'],over7_pct=round(100*c['more_than_7']/n,2) if n else None,over14_count=c['more_than_14'],negative_entry_to_visit=c['system_before_visit'],visit_after_cut=c['visit_after_cut'],visit_in_other_calendar_year=c['attendance_other_calendar_year']))
            for label in BANDS:distribution.append(dict(cohort_year=int(year),province=province,band_days=label,count=z['bands'][label]))
            for m in range(1,13):monthly.append(dict(cohort_year=int(year),province=province,visit_calendar_year=int(year),month=m,visit_records=months[(year,province,m)]))
    export(output/'regional_dengue_timing_by_province_2023_2026.csv',summary)
    export(output/'regional_dengue_delay_distribution_2023_2026.csv',distribution)
    export(output/'regional_dengue_visits_monthly_2023_2026.csv',monthly)
    report={'year_row_counts':dict(row_year),'year_cut_snapshots':[{'cohort_year':a,'cut_date':b,'rows':n} for (a,b),n in sorted(cut.items())], 'piura_region_filtered_count':total['rows'],'geographic_exclusions':excluded_geo,'outside_piura_department_count':outside_dept,'negative_onset_to_attendance':total['negative_delay'],'delay_over90':total['over90_delay'],'entry_before_attendance':total['system_before_visit'],'visit_after_cut':total['visit_after_cut'],'no_patient_level_rows_in_output':True}
    (output/'regional_dengue_audit_summary.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps(report,indent=2,ensure_ascii=False))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--csv',required=True);p.add_argument('--output',required=True);args=p.parse_args();audit(args.csv,args.output)
