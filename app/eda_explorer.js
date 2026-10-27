"use strict";
(function(){
 const Q=window.NINOSALUD_EDA_V07;
 if(!Q)throw new Error('Missing EDA weekly source data');
 const psel=document.getElementById('edaProvinceV07'),ysel=document.getElementById('edaYearV07'),msel=document.getElementById('edaModelYearV07');
 const mprov=document.getElementById('edaModelProvinceV07');
 Q.provinces.forEach(p=>{for(const el of [psel,mprov]){const op=document.createElement('option');op.value=p;op.textContent=p;el.appendChild(op);}});
 const all=Q.provinces.includes('PIURA')?'PIURA':Q.provinces[0];psel.value=all;mprov.value=all;
 for(let y=2018;y<=2025;y++){const op=document.createElement('option');op.value=y;op.textContent=y;ysel.appendChild(op)}ysel.value='2024';
 for(let y=2023;y<=2025;y++){const op=document.createElement('option');op.value=y;op.textContent=y;msel.appendChild(op)}msel.value='2024';
 function num(x){return Number(x||0).toLocaleString('en-US',{maximumFractionDigits:1})}
 function drawCases(){
  const p=psel.value,y=+ysel.value,rows=Q.series.filter(r=>r.p===p && r.y===y).sort((a,b)=>a.w-b.w);
  const valid=rows.filter(r=>r.eda!==null);
  lineChart('edaWeeklyCasesV07',[{name:'Reported diarrheal episodes',color:'#087f76',points:valid.map(r=>[r.w,r.eda])}],{xStep:6,label:'EDA province-week reports'});
  const rain=rows;
  lineChart('edaWeeklyRainV07',[{name:'Observed precipitation',color:'#bf6d2f',points:rain.map(r=>[r.w,r.rain])}],{xStep:6,label:'Observed weekly mean precipitation mm'});
  const nMissing=rows.filter(r=>r.rain===null||r.temp===null||r.humidity===null).length;
  document.getElementById('edaWeeklyFactsV07').innerHTML=`<div class="row-split"><span>Reported EDA episodes · ${y}</span><strong>${num(valid.reduce((a,r)=>a+r.eda,0))}</strong></div><div class="row-split"><span>Weekly EDA observations</span><strong>${valid.length}</strong></div><div class="row-split"><span>Weeks with incomplete observed climate</span><strong>${nMissing}</strong></div><p class="mini">This is the reported number of episodes across all ages, not laboratory-confirmed incidence or unique patients.</p>`;
 }
 function drawModels(){
  const p=mprov.value,y=+msel.value,rows=Q.predictions.filter(r=>r.p===p&&r.y===y).sort((a,b)=>a.w-b.w);
  if(!rows.length){document.getElementById('edaModelChartV07').innerHTML='<p>No eligible holdout observations for this selection.</p>';return;}
  lineChart('edaModelChartV07',[{name:'Observed',color:'#153d62',points:rows.map(r=>[r.w,r.obs]),width:3}, {name:'Persistence (last observed)',color:'#087f76',dash:true,points:rows.map(r=>[r.w,r.persist])}, {name:'Random forest + weather',color:'#bf6d2f',dash:true,points:rows.map(r=>[r.w,r.rf])}],{xStep:6,label:'Historical four-week-ahead model backtest'});
  const mae=k=>rows.reduce((s,r)=>s+Math.abs(r[k]-r.obs),0)/rows.length;
  document.getElementById('edaModelFactsV07').innerHTML=`<div class="row-split"><span>Eligible historical predictions</span><strong>${rows.length}</strong></div><div class="row-split"><span>Persistence MAE</span><strong>${mae('persist').toFixed(1)}</strong></div><div class="row-split"><span>Climate Random Forest MAE</span><strong>${mae('rf').toFixed(1)}</strong></div><p class="mini">Errors are weekly episodes for ${p}. These are retrospective predictions, not live forecasts.</p>`;
 }
 const held=Q.metrics.filter(r=>r.period==='2023-2025 holdout');
 document.getElementById('edaHeldoutV07').innerHTML=`<div class="row-split"><span>Matched prediction rows</span><strong>${held[0]?.n||0}</strong></div>`+held.map(r=>`<div class="row-split"><span>${r.model}</span><strong>${r.mae.toFixed(2)} MAE</strong></div>`).join('')+`<p class="mini">2019–2022 training; 2023–2025 retrospective evaluation, already inspected in development. Matched complete-case sample. Lower MAE is better.</p>`;
 for(const el of [psel,ysel])el.addEventListener('change',drawCases);
 for(const el of [mprov,msel])el.addEventListener('change',drawModels);
 drawCases();drawModels();
})();
