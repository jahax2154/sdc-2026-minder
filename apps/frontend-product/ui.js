export const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
export const card=(heading,content)=>`<article class="rail-card product-card"><h2>${esc(heading)}</h2>${content}</article>`;
export const safeURL=value=>{try{const u=new URL(value);return u.protocol==='https:'?u.href:null;}catch{return null;}};
export function source(s) {
  const url=safeURL(s.uri||s.url);
  return `<details class="source"><summary>${esc(s.title||s.publisher||s.source_id||'Source details')}</summary><p>${url?`<a href="${esc(url)}" target="_blank" rel="noreferrer">Open source ↗</a>`:'Source link unavailable'}</p><p>${esc(s.geography||'Scope not supplied')} · available ${esc(s.available_at||'date unknown')} · edition ${esc(s.version||'unknown')}</p></details>`;
}
export function facts(items=[]) {
  const category={external_fact:'Source evidence',user_reported:'You reported',calculated_assessment:'Calculated assessment',proposed_action:'Suggestion',limitation:'Limitations'};
  return items.map(f=>`<section class="statement"><small>${esc(category[f.category]||'Saved evidence')}${f.measurement_type?' · '+esc(f.measurement_type.replaceAll('_',' ')):''}</small><p>${esc(f.text)}</p>${f.period?`<small>Period: ${esc(f.period.label||[f.period.start,f.period.end].filter(Boolean).join(' – ')||'unknown')}</small>`:''}${f.published_at!==undefined?`<small>Published: ${esc(f.published_at||'unknown')}</small>`:''}${f.mapping?.scope?`<p>${esc(f.mapping.scope)}</p>`:''}${(f.limitations||[]).map(l=>`<p class="secondary">${esc(l)}</p>`).join('')}${(f.sources||[]).map(source).join('')}</section>`).join('');
}
export function showError(e) {const el=document.querySelector('#error');el.textContent=e.message;el.hidden=false;if(e.status===409){const b=document.createElement('button');b.textContent='Refresh and review';b.className='button-outline';b.onclick=()=>window.dispatchEvent(new Event('minder-refresh'));el.append(' ',b);}}
export function bind(id,handler) {
  const el=document.getElementById(id);if(!el)return;
  el.addEventListener(el.tagName==='FORM'?'submit':'click',async e=>{
    e.preventDefault();if(el.dataset.pending)return;el.dataset.pending='true';
    const controls=[...el.querySelectorAll('button,input,select,textarea'),...(el.matches('button')?[el]:[])].map(n=>[n,n.disabled]);controls.forEach(([n])=>n.disabled=true);
    document.querySelector('#error').hidden=true;
    try{await handler(e);}catch(err){if(err.code!=='request_cancelled')showError(err);}finally{delete el.dataset.pending;controls.forEach(([n,d])=>{if(n.isConnected)n.disabled=d;});}
  });
}
function diffValue(value){
 if(value===null||value===undefined)return '<p>Not set</p>';
 if(typeof value!=='object')return `<p>${esc(value)}</p>`;
 let friendly='';
 if(!Array.isArray(value)&&typeof value.task_id==='string'){
  const fields=[['Task',value.title||value.task_id],['Description',value.description||'Not supplied'],['Status',value.state||'Not supplied'],['Schedule',value.scheduled_at||'Unscheduled'],['Estimated effort',value.estimated_hours==null?'Unknown':value.estimated_hours+' hours'],['Prerequisites',(value.prerequisite_task_ids||[]).join(', ')||'None']];
  friendly=`<dl>${fields.map(([label,text])=>`<dt>${label}</dt><dd>${esc(text)}</dd>`).join('')}</dl>`;
 }else if(!Array.isArray(value)&&Array.isArray(value.plan_ids)){
  friendly=value.plan_ids.length?`<p>Only these saved plans:</p><ul>${value.plan_ids.map(id=>`<li>${esc(id)}</li>`).join('')}</ul>`:'<p>All saved plans in your workspace.</p>';
 }else if(Array.isArray(value)){friendly=value.length?`<ul>${value.map(item=>`<li>${esc(typeof item==='object'?JSON.stringify(item):item)}</li>`).join('')}</ul>`:'<p>Empty list</p>';}
 return friendly+`<details><summary>Complete value</summary><pre class="diff-json">${esc(JSON.stringify(value,null,2))}</pre></details>`;
}
export const diffLabel=d=>`<div class="diff"><strong>${esc(d.path)}</strong><div class="diff-columns"><section class="diff-before"><small>Before</small>${diffValue(d.before)}</section><section class="diff-after"><small>After</small>${diffValue(d.after)}</section></div></div>`;

export const sourceAttribution=()=>`<details class="source occupational-attribution"><summary>Occupational reference and attribution</summary><p>O*NET 31.0 Database, U.S. Department of Labor, Employment and Training Administration / National Center for O*NET Development. <a href="https://www.onetcenter.org/database.html" target="_blank" rel="noreferrer">Database source</a> · <a href="https://creativecommons.org/licenses/by/4.0/" target="_blank" rel="noreferrer">CC BY 4.0</a>.</p><p>Original CSV bytes remain unchanged. Minder namespaces identifiers and projects occupational ratings into evidence. U.S. occupational ratings are separate from Malaysian labour demand and individual competence. Other sources retain their own links, dates and scope.</p></details>`;
