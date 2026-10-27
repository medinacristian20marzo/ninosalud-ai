'use strict';
const D = window.NINOSALUD_DATA;
if(!D) throw new Error('Missing dashboard_data.js');
const fmt=n=>Number(n||0).toLocaleString('en-US',{maximumFractionDigits:1});
const val=(r,k)=>Number(r?.[k]||0);
const indicators={dengue_notifications:'Dengue notifications',leptospirosis_notifications:'Leptospirosis notifications',eda_episodes_under5:'Diarrheal episodes, under 5',eda_episodes_age5plus:'Diarrheal episodes, age 5+'};
const riskColors={'Muy alto':'#b3424d','Alto':'#e39151','Medio':'#e6c479','Bajo':'#75aea1','Muy bajo':'#438c90'};
function escapeHTML(s){return String(s??'').replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));}
function table(head,rows){return `<table><thead><tr>${head.map(x=>`<th>${escapeHTML(x)}</th>`).join('')}</tr></thead><tbody>${rows.map(row=>`<tr>${row.map(x=>`<td>${escapeHTML(x)}</td>`).join('')}</tr>`).join('')}</tbody></table>`}
function lineChart(container,series,options={}){
 const el=document.getElementById(container), W=800,H=295,pad={left:65,right:15,top:20,bottom:42};
 const xs=series.flatMap(x=>x.points.map(p=>p[0])); const ys=series.flatMap(x=>x.points.filter(p=>p[1]!==null&&p[1]!==undefined&&p[1]!=='').map(p=>Number(p[1]))).filter(Number.isFinite);
 if(!xs.length||!ys.length){el.innerHTML='<p>No data available.</p>';return;}
 const xmin=Math.min(...xs),xmax=Math.max(...xs),ymin=0,peak=Math.max(1,...ys);const power=Math.pow(10,Math.floor(Math.log10(peak/4||1)));const nice=[1,2,2.5,5,10].map(v=>v*power).find(v=>v*4>=peak*1.05)||10*power;const ymax=nice*4;
 const px=x=>pad.left+(x-xmin)*((W-pad.left-pad.right)/(xmax-xmin||1));
 const py=y=>H-pad.bottom-(y-ymin)*((H-pad.top-pad.bottom)/(ymax-ymin));
 let inner='';
 for(let j=0;j<=4;j++){const y=ymax*j/4; inner+=`<line x1="${pad.left}" y1="${py(y)}" x2="${W-pad.right}" y2="${py(y)}" stroke="#e6edf2"/><text x="${pad.left-10}" y="${py(y)+4}" text-anchor="end" font-size="11" fill="#718397">${y>=1000?Math.round(y).toLocaleString('en-US'):Number(y.toFixed(2)).toLocaleString('en-US',{maximumFractionDigits:2})}</text>`}
 const step=options.xStep||Math.max(1,Math.ceil((xmax-xmin)/7));
 for(let x=xmin;x<=xmax;x+=step)inner+=`<text x="${px(x)}" y="${H-15}" font-size="11" text-anchor="middle" fill="#718397">${x}</text>`;
 for(const s of series){
  const pts=s.points.filter(p=>p[1]!==null&&p[1]!==undefined&&p[1]!==''&&Number.isFinite(Number(p[1])));
  if(!pts.length)continue;
  const segments=[];let segment=[];let prev=null;
  for(const p of s.points){
   if(p[1]===null||p[1]===undefined||p[1]===''||!Number.isFinite(Number(p[1]))){if(segment.length)segments.push(segment);segment=[];prev=null;continue;}
   if(prev!==null && Number(p[0])-prev>1.1){if(segment.length)segments.push(segment);segment=[];}
   segment.push(p);prev=Number(p[0]);
  }
  if(segment.length)segments.push(segment);
  for(const seg of segments)inner+=`<polyline points="${seg.map(p=>`${px(p[0]).toFixed(1)},${py(Number(p[1])).toFixed(1)}`).join(' ')}" fill="none" stroke="${s.color}" stroke-width="${s.width||2.5}" stroke-linejoin="round" stroke-linecap="round" ${s.dash?'stroke-dasharray="6 4"':''}/>`;
  if(pts.length<25)for(const p of pts)inner+=`<circle cx="${px(p[0])}" cy="${py(Number(p[1]))}" r="3" fill="${s.color}"><title>${escapeHTML(s.name)}: ${fmt(p[1])} at ${p[0]}</title></circle>`;
 }
 inner+=`<line x1="${pad.left}" y1="${H-pad.bottom}" x2="${W-pad.right}" y2="${H-pad.bottom}" stroke="#b4c8d4"/>`;
 el.innerHTML=`<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="${escapeHTML(options.label||'time series chart')}">${inner}</svg>`;
}
function setEpi(){const k=document.getElementById('indicator').value;const pts=D.annual.filter(r=>!(k==='eda_episodes_age5plus' && r.ano==='2024')).map(r=>[val(r,'ano'),val(r,k)]);
 lineChart('epiChart',[{name:indicators[k],color:'#087f76',points:pts}],{label:indicators[k],xStep:2});
 const a=D.annual.find(r=>r.ano==='2017'),b=D.annual.find(r=>r.ano==='2023');const x=val(a,k),y=val(b,k);
 document.getElementById('epiCompare').innerHTML=`<div class="row-split"><span>2017</span><strong>${fmt(x)}</strong></div><div class="row-split"><span>2023</span><strong>${fmt(y)}</strong></div><div class="row-split"><span>Difference</span><strong>${y-x>=0?'+':''}${fmt(y-x)} (${x?(((y-x)/x)*100).toFixed(1):'n/a'}%)</strong></div><p class="mini">Two-year change in reported counts. No causal attribution.</p>`;
 document.getElementById('annualTable').innerHTML=table(['Year','Dengue','Leptospirosis','EDA under 5','EDA age 5+'],D.annual.map(r=>[r.ano,fmt(r.dengue_notifications),fmt(r.leptospirosis_notifications),fmt(r.eda_episodes_under5),r.ano==='2024'?'Incomplete*':fmt(r.eda_episodes_age5plus)]));
}
function setBacktest(){const y=document.getElementById('testYear').value,rs=D.backtest.filter(r=>r.year===y),mt=D.metrics.metrics[y];
 const points=k=>rs.map(r=>[val(r,'target_week_plus4'),val(r,k)]);
 lineChart('backtestChart',[{name:'Observed',color:'#153d62',points:points('observed_dengue_notifications'),width:3.3},{name:'Persistence',color:'#087f76',points:points('persistence_prediction'),dash:true},{name:'ML + climate',color:'#bf6d2f',points:points('ML_case_climate_prediction'),dash:true}],{label:'Dengue reported notifications, observed and predicted',xStep:6});
 const winner=mt.persistence_MAE<mt.climate_plus_case_MAE?'simple persistence':'ML + climate';
 document.getElementById('scorecard').innerHTML=`<div class="row-split"><span>Simple persistence</span><strong>${fmt(mt.persistence_MAE)}</strong></div><div class="row-split"><span>ML, case counts only</span><strong>${fmt(mt.case_only_MAE)}</strong></div><div class="row-split"><span>ML, including climate</span><strong>${fmt(mt.climate_plus_case_MAE)}</strong></div><p class="mini">In ${y}, the more accurate of the two highlighted methods is <strong>${winner}</strong>. ${mt.observations} test weeks.</p>`;
}
function setRain(){let y=document.getElementById('rainYear').value,rows=D.climate.filter(r=>r.ano===+y);lineChart('rainChart',[{name:'Population-weighted rainfall',color:'#087f76',points:rows.map(r=>[+r.semana,+r.ptot])}],{label:'Weekly precipitation mm',xStep:7});let total=rows.reduce((a,b)=>a+Number(b.ptot||0),0),temp=rows.reduce((a,b)=>a+Number(b.tmean||0),0)/Math.max(1,rows.length);document.getElementById('rainFacts').innerHTML=`<div class="row-split"><span>Epidemiological weeks</span><strong>${rows.length}</strong></div><div class="row-split"><span>Sum of weekly mean rain</span><strong>${fmt(total)} mm</strong></div><div class="row-split"><span>Mean population-weighted temperature</span><strong>${temp.toFixed(1)} °C</strong></div><p class="mini">Regional aggregation is an approximation; rainfall values should not be interpreted as direct local flood measurements.</p>`}
const recentFacilities={};for(const f of D.active_facilities)recentFacilities[f.ubigeo]=(recentFacilities[f.ubigeo]||0)+1;
let selectedDistrict=null;
function geomRings(g){return g.type==='Polygon'?[g.coordinates]:g.type==='MultiPolygon'?g.coordinates:[];}
function drawMap(){let dep=document.getElementById('department').value,type=document.getElementById('riskType').value;let rows=D.risk.filter(r=>r.departamento===dep),labelKey=type==='flood'?'flood_NRiesgo_In':'landslide_NRiesgo_MM';
 const geo=rows.flatMap(r=>geomRings(D.geometry[r.ubigeo]||{type:'None'})).flat(2);
 if(!geo.length){document.getElementById('map').innerHTML='No map data';return}
 const xs=geo.map(p=>+p[0]),ys=geo.map(p=>+p[1]),x0=Math.min(...xs),x1=Math.max(...xs),y0=Math.min(...ys),y1=Math.max(...ys),W=880,H=475,pad=20,scale=Math.min((W-pad*2)/(x1-x0),(H-pad*2)/(y1-y0)),offx=(W-(x1-x0)*scale)/2,offy=(H-(y1-y0)*scale)/2;
 const pt=p=>[(offx+(p[0]-x0)*scale).toFixed(1),(offy+(y1-p[1])*scale).toFixed(1)];
 let paths='';for(const r of rows){const geom=D.geometry[r.ubigeo];if(!geom)continue;let d='';for(const poly of geomRings(geom))for(const ring of poly){if(!ring.length)continue;d+=ring.map((p,i)=>`${i?'L':'M'}${pt(p).join(' ')}`).join(' ')+'Z';}
 const risk=r[labelKey],color=riskColors[risk]||'#cfd8dc';paths+=`<path data-code="${r.ubigeo}" d="${d}" fill="${color}" fill-rule="evenodd" class="${selectedDistrict===r.ubigeo?'selected':''}"><title>${escapeHTML(r.distrito)} · ${escapeHTML(risk||'Unknown')}</title></path>`;}
 document.getElementById('map').innerHTML=`<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="CENEPRED ${type} risk classifications for ${dep}">${paths}</svg>`;
 document.querySelectorAll('#map path').forEach(path=>path.addEventListener('click',()=>{selectedDistrict=path.dataset.code;drawMap();districtDetail();}));
 document.getElementById('mapLegend').innerHTML=['Muy alto','Alto','Medio','Bajo','Muy bajo'].map(r=>`<span><i class="swatch" style="background:${riskColors[r]}"></i>${r}</span>`).join('');
 const rank={'Muy alto':0,Alto:1,Medio:2,Bajo:3,'Muy bajo':4};rows.sort((a,b)=>(rank[a[labelKey]]??5)-(rank[b[labelKey]]??5)||a.distrito.localeCompare(b.distrito));
 document.getElementById('districtTable').innerHTML=table(['District','Flood risk','Mass-movement risk','CENEPRED centres exposed'],rows.map(r=>[r.distrito,r.flood_NRiesgo_In,r.landslide_NRiesgo_MM,r.flood_eess_sinu||'0']));
 if(!rows.some(r=>r.ubigeo===selectedDistrict)){selectedDistrict=rows[0]?.ubigeo||null;districtDetail()}
}
function districtDetail(){const r=D.risk.find(r=>r.ubigeo===selectedDistrict);if(!r)return;
 const p=D.population.find(x=>x.ubigeo===r.ubigeo)||{},c=D.district_cases[r.ubigeo]||{};
 document.getElementById('districtInfo').innerHTML=`<h2>${escapeHTML(r.distrito)}</h2><p>${escapeHTML(r.provincia)}, ${escapeHTML(r.departamento)} · UBIGEO ${r.ubigeo}</p>
 <div class="row-split"><span>Flood risk · 2026 scenario</span><strong>${escapeHTML(r.flood_NRiesgo_In)}</strong></div>
 <div class="row-split"><span>Mass movement risk · 2026</span><strong>${escapeHTML(r.landslide_NRiesgo_MM)}</strong></div>
 <div class="row-split"><span>CENEPRED healthcare sites in susceptible areas</span><strong>${fmt(r.flood_eess_sinu)}</strong></div>
 <div class="row-split"><span>Active geocoded RENIPRESS listings · 2026</span><strong>${fmt(recentFacilities[r.ubigeo]||0)}</strong></div>
 <div class="row-split"><span>INEI estimated 2023 population</span><strong>${fmt(p.pop_2023)}</strong></div>
 ${r.departamento==='PIURA'?`<div class="row-split"><span>Dengue notifications · 2017</span><strong>${fmt(c.dengue_2017)}</strong></div><div class="row-split"><span>Dengue notifications · 2023</span><strong>${fmt(c.dengue_2023)}</strong></div>`:''}<p class="mini">Historical disease notifications and 2026 geospatial exposure are distinct measures. Absence of a disease record is not evidence of zero infections.</p>`;
}
for(const tab of document.querySelectorAll('.tab'))tab.addEventListener('click',()=>{document.querySelectorAll('.tab').forEach(n=>n.classList.toggle('active',n===tab));document.querySelectorAll('.view').forEach(v=>v.classList.toggle('active',v.id===tab.dataset.tab));if(tab.dataset.tab==='territory')drawMap();});
document.getElementById('indicator').addEventListener('change',setEpi);
document.getElementById('testYear').addEventListener('change',setBacktest);
document.getElementById('rainYear').addEventListener('change',setRain);
document.getElementById('department').addEventListener('change',()=>{selectedDistrict=null;drawMap()});
document.getElementById('riskType').addEventListener('change',drawMap);
setEpi();setBacktest();setRain();drawMap();
