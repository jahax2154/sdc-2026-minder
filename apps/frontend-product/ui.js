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
export const diffLabel=d=>`<div class="diff"><strong>${esc(d.path)}</strong><div><del>${esc(d.before??'Not set')}</del> → <ins>${esc(d.after??'Not set')}</ins></div></div>`;
