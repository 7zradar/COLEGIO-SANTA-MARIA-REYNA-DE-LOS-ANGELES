
if(new URLSearchParams(location.search).has('auditoria')){
  const s=document.createElement('script');s.src='/axe.min.js';document.head.append(s);
  const panel=document.createElement('aside');panel.id='qualityTools';panel.setAttribute('aria-label','Herramientas de comprobación');
  const link=document.createElement('link');link.rel='stylesheet';link.href='/audit-tools.css';document.head.append(link);
  panel.innerHTML='<button id="runAudit">Ejecutar auditoría automática</button> <button id="applySpacing">Probar espaciado de texto</button><output id="auditState" role="status"></output><pre id="apf3AuditResult" hidden></pre>';
  document.body.append(panel);panel.querySelector('#runAudit').disabled=true;s.onload=()=>{panel.querySelector('#runAudit').disabled=false;panel.querySelector('#auditState').textContent='Motor listo';};s.onerror=()=>{panel.querySelector('#auditState').textContent='No se pudo cargar axe-core';};
  panel.querySelector('#runAudit').onclick=async()=>{
    panel.querySelector('#auditState').textContent='Analizando';
    try{
      const result=await axe.run(document,{exclude:[['#qualityTools']],runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa']}});
      const data={tool:'axe-core',version:axe.version,url:location.href,timestamp:new Date().toISOString(),violations:result.violations,incomplete:result.incomplete,passes:result.passes.map(x=>({id:x.id,tags:x.tags,nodes:x.nodes.map(n=>({html:n.html,target:n.target}))})),inapplicable:result.inapplicable.map(x=>({id:x.id,tags:x.tags}))};
      panel.querySelector('#apf3AuditResult').textContent=JSON.stringify(data);
      panel.querySelector('#auditState').textContent=result.violations.length+' reglas con incidencias; '+result.incomplete.length+' revisiones manuales';
    }catch(e){panel.querySelector('#auditState').textContent=e.message;}
  };
  panel.querySelector('#applySpacing').onclick=()=>{
    const style=document.createElement('link');style.rel='stylesheet';style.href='/spacing-test.css';document.head.append(style);
    panel.querySelector('#auditState').textContent='Espaciado WCAG 1.4.12 aplicado';
  };
}
