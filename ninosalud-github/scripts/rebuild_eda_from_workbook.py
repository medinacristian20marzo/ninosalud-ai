#!/usr/bin/env python3
"""Extract the Piura province-week table from a participant-supplied CDC workbook.

Reads stored OOXML values only; does not evaluate formulas, alter the workbook,
fill missing observations, or infer case counts. Uses the Python standard library.
The raw workbook is intentionally not distributed in the public repository.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,re,zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

NS={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
    'r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
ROOT=Path(__file__).resolve().parents[1]
FIELDS=['departamento','provincia','tmean','tmax','tmin','humr','ptot','ano','semana',
        'tmean_clima','tmax_clima','tmin_clima','humr_clima','ptot_clima','tipo_caso','casos']

def column_index(ref: str)->int:
    out=0
    for ch in re.match(r'[A-Z]+',ref).group():out=out*26+ord(ch)-64
    return out-1

def source_rows(path: Path, sheet_name: str='Provincia'):
    with zipfile.ZipFile(path) as z:
        strings=[]
        if 'xl/sharedStrings.xml' in z.namelist():
            strings=[''.join(n.text or '' for n in x.iter() if n.tag.endswith('}t')) for x in ET.fromstring(z.read('xl/sharedStrings.xml'))]
        links={r.attrib['Id']:r.attrib['Target'] for r in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
        book=ET.fromstring(z.read('xl/workbook.xml'))
        sheets=book.find('s:sheets',NS)
        sheet=next((s for s in sheets if s.get('name','').lower()==sheet_name.lower()),None)
        if sheet is None:raise ValueError('Missing Provincia worksheet')
        target=links[sheet.get('{'+NS['r']+'}id')]
        member=target.lstrip('/') if target.startswith('/') else 'xl/'+target
        with z.open(member) as f:
            for _,row in ET.iterparse(f,events=('end',)):
                if not row.tag.endswith('}row'):continue
                values=['']*16
                for c in row:
                    if not c.tag.endswith('}c'):continue
                    idx=column_index(c.get('r','A1'))
                    if idx>=len(values):raise ValueError('Unexpected column outside verified schema')
                    if c.get('t')=='inlineStr':v=''.join(n.text or '' for n in c.iter() if n.tag.endswith('}t'))
                    else:
                        ve=c.find('s:v',NS);v=ve.text if ve is not None and ve.text else ''
                        if c.get('t')=='s' and v:v=strings[int(v)]
                    values[idx]=v
                yield values
                row.clear()

def rebuild(source: Path,output: Path)->dict:
    rows=source_rows(source);header=next(rows)
    normal=[v.strip().lower().replace(' ','_') for v in header]
    if normal!=FIELDS:raise ValueError(f'Unexpected source fields: {normal}')
    selected=[];keys=set()
    for vals in rows:
        if not vals[0]:continue
        row=dict(zip(FIELDS,vals))
        if row['departamento']!='PIURA' or row['tipo_caso']!='eda_total':continue
        y=int(row['ano']);w=int(row['semana'])
        if not 2018<=y<=2025:continue
        key=(row['provincia'],y,w)
        if key in keys:raise ValueError(f'Duplicate province-year-week: {key}')
        keys.add(key);selected.append(row)
    output.parent.mkdir(parents=True,exist_ok=True)
    with output.open('w',encoding='utf-8',newline='') as f:
        wr=csv.DictWriter(f,fieldnames=FIELDS);wr.writeheader();wr.writerows(selected)
    result={'source_file':source.name,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
            'rows':len(selected),'provinces':sorted({r['provincia'] for r in selected}),
            'missing_observed_climate_rows':sum(any(not r[k] for k in ('tmean','humr','ptot')) for r in selected),
            'scope':'Piura, all-age EDA, province-week; source week labels retained, not calendar-remapped',
            'missing_data':'Empty source fields remain empty, never changed to zero.'}
    output.with_suffix('.provenance.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    return result

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--workbook',type=Path,required=True)
    ap.add_argument('--output',type=Path,default=ROOT/'verification_local/eda_rebuilt.csv')
    a=ap.parse_args();print(json.dumps(rebuild(a.workbook,a.output),indent=2))
