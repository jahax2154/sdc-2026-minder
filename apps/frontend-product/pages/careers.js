import {api,key} from '../client.js';
import {esc,facts,showError,sourceAttribution} from '../ui.js';
import {svg} from '../icons.js';
const link=(tab,label)=>`<a href="#careers/${tab}">${label}</a>`;
export async function careers(ctx,tab='matches'){
 const view=ctx.view;view.className='morning-explore';
 view.innerHTML=`<header class="page-heading"><p class="eyebrow">EXPLORE / YOUR DIRECTION</p><h1>Careers</h1><p>Explore directions that connect with your interests and goals.</p></header><nav class="tabs" aria-label="Careers">${[['matches','Matches'],['compare','Compare'],['outlook','Outlook']].map(([id,label])=>`<a href="#careers/${id}" class="${tab===id?'active':''}" ${tab===id?'aria-current="page"':''}>${label}</a>`).join('')}</nav><div id="careerBody" class="view" role="region" aria-label="Career content"><p role="status">Loading careers…</p></div>${sourceAttribution()}`;
 const body=view.querySelector('#careerBody');
 const read=(path,value)=>api(path,value,value===undefined?'GET':'POST',{signal:ctx.signal});
 if(tab==='outlook'){
   const context=await read('career-context',ctx.selectedRole?{selected_role_ids:[ctx.selectedRole]}:{});if(!ctx.isCurrent())return;
   body.innerHTML=`<div class="section-title"><div><h2>Explore what could change</h2><p>Current observations and source-supported outlook.</p></div></div><section class="panel panel-pad">${facts(context.statements)}</section>`;return;
 }
 const catalog=await read('roles',{query:sessionStorage.getItem('minder-product-search')||'',limit:50});if(!ctx.isCurrent())return;
 sessionStorage.removeItem('minder-product-search');
 let roles=catalog.roles;
 const roleLabel=id=>roles.find(r=>r.role_id===id)?.label||id;
 const empty=()=>`<div class="panel empty"><span class="icon-disc large">${svg('compass')}</span><h2>Discover directions worth exploring</h2><p>Start with your interests, experience, and goals. You can update your profile as you learn more.</p><a class="button primary" href="#profile">Review my profile</a></div>`;
 if(tab==='compare'){
  if(roles.length<2){body.innerHTML=empty();return;}
  let ids=[ctx.selectedRole||roles[0].role_id,roles.find(r=>r.role_id!==ctx.selectedRole)?.role_id||roles[1].role_id];
  async function compare(){
   body.innerHTML='<p role="status">Loading the selected directions…</p>';
   const requirements=await Promise.all(ids.map(role_id=>read('role-requirements',{role_id})));if(!ctx.isCurrent())return;
   body.innerHTML=`<section class="panel panel-pad"><div class="section-title"><div><h2>Compare your directions</h2><p>Choose the work you want to explore.</p></div></div><div class="comparison-wrap" tabindex="0" aria-label="Scrollable career comparison"><table class="comparison"><thead><tr><th scope="col">What matters</th>${ids.map((id,i)=>`<th scope="col">${esc(roleLabel(id))}<br><select data-compare="${i}" aria-label="Career ${i+1}">${roles.map(r=>`<option value="${esc(r.role_id)}" ${r.role_id===id?'selected':''}>${esc(r.label)}</option>`).join('')}</select></th>`).join('')}</tr></thead><tbody><tr><th scope="row">Occupational requirements</th>${requirements.map(r=>`<td>${(r.role.requirements||[]).map(s=>`<p>${esc(s.subject_id)} · ${esc(s.state)}</p>`).join('')||'Not available'}</td>`).join('')}</tr><tr><th scope="row">Evidence scope</th>${requirements.map(r=>`<td>${esc(r.limitation)}</td>`).join('')}</tr><tr><th scope="row">Explore next</th>${ids.map(id=>`<td><button class="button" data-open-role="${esc(id)}">View career ${svg('arrow-right')}</button></td>`).join('')}</tr></tbody></table></div></section>`;
   body.querySelectorAll('[data-compare]').forEach(select=>select.onchange=()=>{ids[Number(select.dataset.compare)]=select.value;compare().catch(showError);});bindRoles();
  }
  function bindRoles(){body.querySelectorAll('[data-open-role]').forEach(b=>b.onclick=()=>openRole(b.dataset.openRole).catch(showError));}
  await compare();return;
 }
 if(tab.startsWith('role/')){await openRole(decodeURIComponent(tab.slice(5)));return;}
 let recommendation=null;
 const recommendationPromise=ctx.profile?read('product/views/career-match',{}).then(result=>({result})).catch(error=>({error})):null;
 function matchingMarkup(){
 const groups=recommendation?.ranking_groups||[];
 return groups.map(group=>{
  const options=(recommendation.options||[]).filter(o=>o.ranking_group===group.group_id);
  if(!options.length)return '';
  const [first,...rest]=options;
  return `<section aria-label="${esc(group.label||'Career matches')}"><div class="panel match-hero"><div class="match-copy"><p class="eyebrow">${esc(group.label||'YOUR MATCHES')}</p><h2>${esc(roleLabel(first.role_id))}</h2><p class="muted">${esc(first.explanation)}</p><div class="actions"><button class="button primary" data-open-role="${esc(first.role_id)}">View career ${svg('arrow-right')}</button><details><summary>How matching works</summary><p>${esc(group.limitation)}</p><p>${Math.round(first.evidence_coverage*100)}% of skill criteria assessed. This describes evidence coverage.</p></details></div></div></div>${rest.length?`<div class="list-heading"><h3>Other directions to explore</h3>${link('compare','Compare careers')}</div><div class="panel">${rest.map(o=>`<div class="career-row"><span class="icon-disc">${svg('compass')}</span><div class="role-link"><strong>${esc(roleLabel(o.role_id))}</strong><p>${esc(o.explanation)}</p></div><button class="text-link" data-open-role="${esc(o.role_id)}">View ${svg('arrow-right')}</button></div>`).join('')}</div>`:''}</section>`;
 }).join('')+(recommendation?.targeted_questions||[]).map(q=>`<div class="callout"><div><strong>A little more context will help</strong><p>${esc(q)}</p></div><a class="button" href="#profile">Update profile</a></div>`).join('');
 }
 body.innerHTML=`<div id="careerMatches">${ctx.profile?'<p role="status">Loading your matches…</p>':empty()}</div><div class="list-heading"><h3>Explore the career catalogue</h3><small>Catalogue order</small></div><form id="careerSearch" class="actions"><label>Find a career <input name="query" type="search" maxlength="200"></label><button class="button" type="submit">Search</button></form><div class="panel" id="careerCatalogue"></div>`;
 function drawCatalogue(){body.querySelector('#careerCatalogue').innerHTML=roles.length?roles.map(r=>`<div class="career-row"><span class="icon-disc">${svg('compass')}</span><div class="role-link"><strong>${esc(r.label)}</strong><p>${esc(r.eligibility)}</p></div><button class="text-link" data-open-role="${esc(r.role_id)}">View career ${svg('arrow-right')}</button></div>`).join(''):'<p class="panel-pad muted">No careers found. Try a broader term.</p>';bindRoles();}
 function bindRoles(){body.querySelectorAll('[data-open-role]').forEach(b=>b.onclick=()=>{location.hash='careers/role/'+encodeURIComponent(b.dataset.openRole);});}
 body.querySelector('#careerSearch').onsubmit=async event=>{event.preventDefault();const b=event.currentTarget.querySelector('button');b.disabled=true;try{const result=await read('roles',{query:event.currentTarget.elements.query.value,limit:50});if(ctx.isCurrent()){roles=result.roles;drawCatalogue();}}catch(e){showError(e);}finally{b.disabled=false;}};
 drawCatalogue();
 if(recommendationPromise){
  const outcome=await recommendationPromise;if(!ctx.isCurrent())return;
  const root=body.querySelector('#careerMatches');
  if(outcome.error){root.innerHTML=`<section class="panel panel-pad"><h3>Your matches could not be loaded</h3><p>${esc(outcome.error.message)}</p><button class="button" id="retryMatches">Retry matches</button></section>`;root.querySelector('#retryMatches').onclick=()=>ctx.render();}
  else{recommendation=outcome.result.data.recommendation;root.innerHTML=matchingMarkup()||'<section class="panel panel-pad"><h3>No supported matches yet</h3><p>Update your profile evidence or explore the catalogue below.</p></section>';bindRoles();}
 }
 async function openRole(id){
  ctx.selectedRole=id;const [requirements,context,directionState]=await Promise.all([read('role-requirements',{role_id:id}),ctx.profile?read('career-context',{selected_role_ids:[id]}):Promise.resolve({statements:[]}),read('product/direction')]);if(!ctx.isCurrent())return;
  body.innerHTML=`<a class="text-link back" href="#careers/matches">${svg('arrow-left')}Back to matches</a><section class="panel panel-pad"><div class="detail-header"><div><h2>${esc(requirements.role.label||roleLabel(id))}</h2><p>${esc(requirements.limitation)}</p></div></div><div class="detail-row"><span class="icon-disc">${svg('compass')}</span><h3>What the work asks for</h3><div>${(requirements.role.requirements||[]).map(r=>`<p>${esc(r.subject_id)} · ${esc(r.state)}</p>`).join('')||'<p>Requirements unavailable.</p>'}</div></div><div class="detail-row"><span class="icon-disc">${svg('user-round')}</span><h3>Your profile connection</h3><div>${ctx.profile?facts(context.statements):'<p>Save a partial profile to connect this career with your background.</p><a class="text-link" href="#profile">Open My profile</a>'}</div></div><div class="callout"><div><strong>Build a path in this direction</strong><p>Your saved plans stay available when you change direction.</p></div><button class="button primary" id="chooseCareer" ${ctx.profile?'':'disabled'}>Choose this direction</button></div><p role="status" id="careerSaveStatus"></p></section>`;
  let exactBody=null;
  body.querySelector('#chooseCareer').onclick=async event=>{const b=event.currentTarget;b.disabled=true;exactBody??={role_id:id,expected_version:directionState.direction?.version||null,idempotency_key:key()};try{await api('product/direction',exactBody,'PUT');if(ctx.isCurrent())location.hash='my-path/next';}catch(e){if([413,415,422].includes(e.status))exactBody=null;body.querySelector('#careerSaveStatus').textContent=e.message;showError(e);}finally{b.disabled=false;}};
 }
}
