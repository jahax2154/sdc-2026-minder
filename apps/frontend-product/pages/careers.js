import {beginPanelRefresh} from '../panel-refresh.js';
import {api,key} from '../client.js';
import {esc,facts,showError,sourceAttribution,source} from '../ui.js';
import {svg} from '../icons.js';
let filters={query:'',comparison:null,recommendation:null,profileVersion:null};
window.addEventListener('minder-private-clear',()=>{filters={query:'',comparison:null,recommendation:null,profileVersion:null};});
const link=(tab,label)=>`<a href="#careers/${tab}">${label}</a>`;
export async function careers(ctx,tab='matches'){
 const view=ctx.view;view.className='morning-explore';
 if(!view.querySelector('#careerBody'))view.innerHTML=`<header class="page-heading"><p class="eyebrow">EXPLORE / YOUR DIRECTION</p><h1>Careers</h1><p>Explore directions that connect with your interests and goals.</p></header><nav class="tabs" aria-label="Careers">${[['matches','Matches'],['compare','Compare'],['outlook','Outlook']].map(([id,label])=>`<a href="#careers/${id}" class="${tab===id?'active':''}" ${tab===id?'aria-current="page"':''}>${label}</a>`).join('')}</nav><div id="careerBody" class="view" role="region" aria-label="Career content"><p role="status">Loading careers…</p></div>${sourceAttribution()}`;
 view.querySelectorAll('.tabs a').forEach(a=>{const active=a.hash==='#'+ctx.page+'/'+tab;a.classList.toggle('active',active);if(active)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current');});
 const previousTab=view.dataset.panelTab;view.dataset.panelTab=tab;
 const body=view.querySelector('#careerBody');
 if(previousTab!==undefined&&previousTab!==tab){delete body.dataset.ready;body.innerHTML='<p role="status">Loading this section…</p>';view.scrollTop=0;}
 beginPanelRefresh(ctx,body,previousTab===tab);
 const read=(path,value)=>api(path,value,value===undefined?'GET':'POST',{signal:ctx.signal});
 if(tab==='outlook'){
   const direction=ctx.selectedRole?null:(await read('product/direction')).direction;
   const roleId=ctx.selectedRole||direction?.role_id;
   if(!roleId){body.innerHTML='<section class="panel empty"><h2>Choose a career to review its outlook</h2><p>Open a career or choose a direction to inspect the available observations and their scope.</p><a class="button primary" href="#careers/matches">Explore careers</a></section>';return;}
   const [requirements,evidence]=await Promise.all([read('role-requirements',{role_id:roleId}),read('role-evidence',{role_id:roleId})]);if(!ctx.isCurrent())return;
   const labels={employer_observation:'Employer observations',published_offering_activity:'Published occupation-category activity',occupation_shortage:'Occupation shortage context',sector_context:'Related sector context'};
   body.innerHTML=`<div class="section-title"><div><h2>Explore what could change</h2><p>Current observations, with their source dates and scope.</p></div><span class="chip">${esc(requirements.role.label||roleId)}</span></div><section class="panel panel-pad"><h2>Future Explorer</h2><div class="scenario-grid"><div><div class="scenario-heading"><h3>Current observations</h3></div>${evidence.records.map(r=>`<section class="outlook-observation"><h3>${esc(labels[r.measurement_type]||r.measurement_type)}</h3><p>${r.status==='available'?`${esc(r.value==='listed_in_national_MyCOL'?'Related source group is listed':typeof r.value==='number'?r.value.toLocaleString():r.value)} ${esc(r.value==='listed_in_national_MyCOL'?'':r.unit)}`:'Unavailable or unmapped.'}</p>${r.status==='available'?`<p>${esc(r.mapping?.scope||'Source scope not supplied.')}</p><p>Period: ${esc(r.observation_period?.label||[r.observation_period?.start,r.observation_period?.end].filter(Boolean).join(' – ')||'not supplied')}</p>${r.ranking_eligibility==='context_only'?'<p>Context only; this is not a role-level quantity.</p>':''}`:''}${r.source?source(r.source):''}</section>`).join('')||'<p>No source observations were returned.</p>'}</div><div><div class="scenario-heading"><h3>Forecast status</h3></div><p>No validated forecast was returned by the available source contract. Current observations do not establish a future trend.</p><p class="build-next">You can compare career requirements while future evidence is unavailable.</p><a class="button" href="#careers/compare">Compare careers</a></div></div></section>`;return;
 }
 filters.query=sessionStorage.getItem('minder-product-search')??filters.query;
 const catalog=await read('roles',{query:filters.query,limit:50});if(!ctx.isCurrent())return;
 sessionStorage.removeItem('minder-product-search');
 let roles=catalog.roles;
 const roleLabel=id=>roles.find(r=>r.role_id===id)?.label||id;
 const empty=()=>`<div class="panel empty"><span class="icon-disc large">${svg('compass')}</span><h2>Discover directions worth exploring</h2><p>Start with your interests, experience, and goals. You can update your profile as you learn more.</p><div class="actions" style="justify-content:center"><a class="button" href="#profile">Review my profile</a>${ctx.profile?'<button type="button" class="button primary" id="findMatches">Find my matches</button>':''}</div></div>`;
 if(tab==='compare'){
  if(roles.length<2){body.innerHTML=empty();return;}
  let ids=filters.comparison||[ctx.selectedRole||roles[0].role_id,roles.find(r=>r.role_id!==ctx.selectedRole)?.role_id||roles[1].role_id];
  async function compare(){
   body.setAttribute('aria-busy','true');const focused=document.activeElement?.dataset.compare;
   const requirements=await Promise.all(ids.map(role_id=>read('role-requirements',{role_id})));if(!ctx.isCurrent())return;
   body.innerHTML=`<section class="panel panel-pad"><div class="section-title"><div><h2>Compare your directions</h2><p>Choose the work you want to explore.</p></div></div><div class="comparison-wrap" tabindex="0" aria-label="Scrollable career comparison"><table class="comparison"><thead><tr><th scope="col">What matters</th>${ids.map((id,i)=>`<th scope="col">${esc(roleLabel(id))}<br><select data-compare="${i}" aria-label="Career ${i+1}">${roles.map(r=>`<option value="${esc(r.role_id)}" ${r.role_id===id?'selected':''}>${esc(r.label)}</option>`).join('')}</select></th>`).join('')}</tr></thead><tbody><tr><th scope="row">Occupational requirements</th>${requirements.map(r=>`<td>${(r.role.requirements||[]).map(s=>`<p>${esc(s.subject_id)} · ${esc(s.state)}</p>`).join('')||'Not available'}</td>`).join('')}</tr><tr><th scope="row">Evidence scope</th>${requirements.map(r=>`<td>${esc(r.limitation)}</td>`).join('')}</tr><tr><th scope="row">Explore next</th>${ids.map(id=>`<td><button class="button" data-open-role="${esc(id)}">View career ${svg('arrow-right')}</button></td>`).join('')}</tr></tbody></table></div></section>`;
   body.setAttribute('aria-busy','false');if(focused!==undefined)body.querySelector(`[data-compare="${focused}"]`)?.focus();
   body.querySelectorAll('[data-compare]').forEach(select=>select.onchange=()=>{ids[Number(select.dataset.compare)]=select.value;filters.comparison=[...ids];compare().catch(showError);});bindRoles();
  }
  function bindRoles(){body.querySelectorAll('[data-open-role]').forEach(b=>b.onclick=()=>openRole(b.dataset.openRole).catch(showError));}
  await compare();return;
 }
 if(tab.startsWith('role/')){await openRole(decodeURIComponent(tab.slice(5)));return;}
 let recommendation=filters.profileVersion===ctx.profile?.version?filters.recommendation:null;
 let matching=false;
 function matchingMarkup(){
 const groups=recommendation?.ranking_groups||[];
 return groups.map(group=>{
  const options=(recommendation.options||[]).filter(o=>o.ranking_group===group.group_id);
  if(!options.length)return '';
  const [first,...rest]=options;
  return `<section aria-label="${esc(group.label||'Career matches')}"><div class="panel match-hero"><div class="match-copy"><p class="eyebrow">${esc(group.label||'YOUR MATCHES')}</p><h2>${esc(roleLabel(first.role_id))}</h2><p class="muted">${esc(first.explanation)}</p><div class="actions"><button class="button primary" data-open-role="${esc(first.role_id)}">View career ${svg('arrow-right')}</button><details><summary>How matching works</summary><p>${esc(group.limitation)}</p><p>${Math.round(first.evidence_coverage*100)}% of skill criteria assessed. This describes evidence coverage.</p></details></div></div></div>${rest.length?`<div class="list-heading"><h3>Other directions to explore</h3>${link('compare','Compare careers')}</div><div class="panel">${rest.map(o=>`<div class="career-row"><span class="icon-disc">${svg('compass')}</span><div class="role-link"><strong>${esc(roleLabel(o.role_id))}</strong><p>${esc(o.explanation)}</p></div><button class="text-link" data-open-role="${esc(o.role_id)}">View ${svg('arrow-right')}</button></div>`).join('')}</div>`:''}</section>`;
 }).join('')+(recommendation?.targeted_questions||[]).map(q=>`<div class="callout"><div><strong>A little more context will help</strong><p>${esc(q)}</p></div><a class="button" href="#profile">Update profile</a></div>`).join('');
 }
 body.innerHTML=`<div id="careerMatches">${recommendation?matchingMarkup():empty()}</div><div class="list-heading"><h3>Explore the career catalogue</h3><small>Catalogue order</small></div><form id="careerSearch" class="actions"><label>Find a career <input id="careerQuery" name="query" type="search" maxlength="200" value="${esc(filters.query)}"></label><button class="button" type="submit">Search</button></form><div class="panel" id="careerCatalogue"></div>`;
 function drawCatalogue(){body.querySelector('#careerCatalogue').innerHTML=roles.length?roles.map(r=>`<div class="career-row"><span class="icon-disc">${svg('compass')}</span><div class="role-link"><strong>${esc(r.label)}</strong><p>${esc(r.eligibility)}</p></div><button class="text-link" data-open-role="${esc(r.role_id)}">View career ${svg('arrow-right')}</button></div>`).join(''):'<p class="panel-pad muted">No careers found. Try a broader term.</p>';bindRoles();}
 function bindRoles(){body.querySelectorAll('[data-open-role]').forEach(b=>b.onclick=()=>{location.hash='careers/role/'+encodeURIComponent(b.dataset.openRole);});}
 body.querySelector('#careerSearch').onsubmit=async event=>{event.preventDefault();const b=event.currentTarget.querySelector('button');b.disabled=true;try{const result=await read('roles',{query:event.currentTarget.elements.query.value,limit:50});if(ctx.isCurrent()){roles=result.roles;drawCatalogue();}}catch(e){showError(e);}finally{b.disabled=false;}};
 drawCatalogue();
 body.querySelector('#careerSearch input').oninput=e=>filters.query=e.target.value;
 const find=body.querySelector('#findMatches');if(find)find.onclick=loadMatches;
 async function loadMatches(){
  if(matching)return;matching=true;const root=body.querySelector('#careerMatches');root.innerHTML='<p role="status">Finding matches from your saved profile…</p>';
  try{const result=await read('product/views/career-match',{});if(!ctx.isCurrent())return;recommendation=result.data.recommendation;filters.recommendation=recommendation;filters.profileVersion=ctx.profile?.version;root.innerHTML=(matchingMarkup()||'<section class="panel panel-pad"><h3>No supported matches yet</h3><p>Update your profile evidence or explore the catalogue below.</p></section>')+'<button type="button" class="text-link" id="refreshMatches">Refresh my matches</button>';root.querySelector('#refreshMatches').onclick=loadMatches;bindRoles();}
  catch(e){if(!ctx.isCurrent())return;root.innerHTML=`<section class="panel panel-pad"><h3>Your matches could not be loaded</h3><p>${esc(e.message)}</p><button class="button" id="retryMatches">Retry matches</button></section>`;root.querySelector('#retryMatches').onclick=loadMatches;}
  finally{matching=false;}
 }
 async function openRole(id){
  ctx.selectedRole=id;const [requirements,context,directionState]=await Promise.all([read('role-requirements',{role_id:id}),ctx.profile?read('career-context',{selected_role_ids:[id]}):Promise.resolve({statements:[]}),read('product/direction')]);if(!ctx.isCurrent())return;
  body.innerHTML=`<a class="text-link back" href="#careers/matches">${svg('arrow-left')}Back to matches</a><section class="panel panel-pad"><div class="detail-header"><div><h2>${esc(requirements.role.label||roleLabel(id))}</h2><p>${esc(requirements.limitation)}</p></div></div><div class="detail-row"><span class="icon-disc">${svg('compass')}</span><h3>What the work asks for</h3><div>${(requirements.role.requirements||[]).map(r=>`<p>${esc(r.subject_id)} · ${esc(r.state)}</p>`).join('')||'<p>Requirements unavailable.</p>'}</div></div><div class="detail-row"><span class="icon-disc">${svg('user-round')}</span><h3>Your profile connection</h3><div>${ctx.profile?facts(context.statements):'<p>Save a partial profile to connect this career with your background.</p><a class="text-link" href="#profile">Open My profile</a>'}</div></div><div class="callout"><div><strong>Build a path in this direction</strong><p>Your saved plans stay available when you change direction.</p></div><button class="button primary" id="chooseCareer" ${ctx.profile?'':'disabled'}>Choose this direction</button></div><p role="status" id="careerSaveStatus"></p></section>`;
  let exactBody=null;
  body.querySelector('#chooseCareer').onclick=async event=>{const b=event.currentTarget;b.disabled=true;exactBody??={role_id:id,expected_version:directionState.direction?.version||null,idempotency_key:key()};try{await api('product/direction',exactBody,'PUT');if(ctx.isCurrent())location.hash='my-path/next';}catch(e){if([413,415,422].includes(e.status))exactBody=null;body.querySelector('#careerSaveStatus').textContent=e.message;showError(e);}finally{b.disabled=false;}};
 }
}
