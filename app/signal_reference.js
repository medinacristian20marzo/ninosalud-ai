"use strict";
(function(){
 const D=window.NINOSALUD_REFERENCE_SIGNALS;
 if(!D) throw Error('Missing reproducible historical reference series');
 const prov=document.getElementById('signalProvinceV09');
 const year=document.getElementById('signalYearV09');
 const info=document.getElementById('signalInfoV09');
 const records=document.getElementById('signalRecordsV09');
 const num=n=>Number(n).toLocaleString('en-US',{maximumFractionDigits:1});
 D.provinces.forEach(p=>{const o=document.createElement('option');o.value=p;o.textContent=p;prov.appendChild(o)});
 prov.value='PIURA';year.value='2023';
 function render(){
   const p=prov.value,y=Number(year.value);
   const data=D.series.filter(r=>r[0]===p && r[1]===y).sort((a,b)=>a[2]-b[2]);
   const count=data.filter(r=>r[6]).length;
   const share=Math.round(count/data.length*100);
   const high=data.filter(r=>r[6]).sort((a,b)=>Number(b[7])-Number(a[7]));
   lineChart('signalChartV09',[
    {name:'Observed weekly episodes',color:'#123a56',points:data.map(r=>[r[2],r[3]]),width:2.5},
    {name:'Historical 90th-percentile reference',color:'#bf6d2f',dash:true,points:data.map(r=>[r[2],r[5]]),width:2.2},
    {name:'2018-2022 historical median',color:'#087f76',dash:true,points:data.map(r=>[r[2],r[4]])}
   ],{xStep:6,label:'Retrospective reference comparison (not an outbreak alarm)'});
   info.innerHTML=`<div class="row-split"><span>Weeks above historical reference</span><strong>${count} / ${data.length}</strong></div><div class="row-split"><span>Share of selected year's weeks</span><strong>${share}%</strong></div><div class="row-split"><span>Comparison reference</span><strong>2018-2022, same season</strong></div><div class="row-split"><span>Historical reference window</span><strong>±2 weeks</strong></div><div class="row-split"><span>Highest observed ratio</span><strong>${high.length ? num(high[0][7])+'×':'No exceedances'}</strong></div>`;
   document.getElementById('signalLoadV09').textContent=share>=50?'Many weeks exceed the historical reference. This is a warning that the 2018-2022 baseline is not sufficiently calibrated for operational use; possible surveillance or regime shifts must be examined.':'An exceedance is a statistical comparison only. It does not confirm an outbreak or estimate the probability of an outbreak.';
   records.innerHTML='<table><thead><tr><th>Epi week</th><th>Reported EDA</th><th>Historical p90</th><th>Observed / p90</th></tr></thead><tbody>'+high.slice(0,12).map(r=>`<tr><td>${r[2]}</td><td>${num(r[3])}</td><td>${num(r[5])}</td><td>${num(r[7])}×</td></tr>`).join('')+'</tbody></table>'+(high.length?'':'<p class="mini">No weekly count above the historical reference.</p>');
 }
 prov.addEventListener('change',render);year.addEventListener('change',render);render();
})();
