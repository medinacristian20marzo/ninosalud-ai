
'use strict';
(function(){
 const ds=window.NINOSALUD_DENGUE_UPDATE;
 const sel=document.getElementById('dengueYearV06');
 if(!ds||!sel)return;
 function draw(){
   const y=sel.value, r=ds.annual[y]||{}, series=ds.weekly[y]||[];
   lineChart('dengueChartV06',[{name:'Dengue notifications',color:'#087f76',points:series,width:3.2}],
     {label:'MINSA dengue notifications Piura: weekly symptom-onset date, '+y,xStep:5});
   const desc='Total '+Number(r.registros_csv_total||0).toLocaleString('en-US')+
    ' · confirmed '+Number(r.confirmados_C||0).toLocaleString('en-US')+
    ' · probable '+Number(r.probables_P||0).toLocaleString('en-US')+
    ' · severe dengue records '+Number(r.dengue_grave||0).toLocaleString('en-US');
   document.getElementById('dengueFactsV06').textContent=desc;
 }
 sel.addEventListener('change',draw);draw();
})();
