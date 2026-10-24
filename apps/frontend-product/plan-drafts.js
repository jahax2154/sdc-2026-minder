import {api,key} from './client.js';
import {esc} from './ui.js';
import {assistant} from './chat-renderer.js';
import {history,sendTurn} from './conversations.js';
const reviewEpochs=new WeakMap();
const read=(ctx,path,body)=>api(path,body,body===undefined?'GET':'POST',{signal:ctx.signal});
export async function reviewDraft(ctx,root,draftId,roleId){
 const epoch=(reviewEpochs.get(root)||0)+1;reviewEpochs.set(root,epoch);root.innerHTML='<p role="status">Loading the saved draft…</p>';
 let record,roles,selected=roleId||'',exact=null;
 const valid=()=>ctx.isCurrent()&&root.isConnected&&reviewEpochs.get(root)===epoch;
 try{await ctx.refreshProfile();if(!valid())return;const [saved,catalog,direction]=await Promise.all([read(ctx,'product/generation',{draft_id:draftId}),read(ctx,'roles',{query:'',limit:50}),read(ctx,'product/direction')]);selected=roleId||direction.direction?.role_id||'';if(!valid())return;record=saved.generation;roles=catalog.roles;if(selected&&!roles.some(r=>r.role_id===selected)){const requirement=await read(ctx,'role-requirements',{role_id:selected});if(!valid())return;roles.push(requirement.role);}if(typeof record?.version!=='string'||!record.generation?.advice)throw new Error('The saved draft could not be validated.');draw();}
 catch(e){if(!valid())return;root.innerHTML=`<p role="alert">${esc(e.message)}</p><button class="button-outline" data-reload-draft>Retry saved draft</button>`;root.querySelector('button').onclick=()=>reviewDraft(ctx,root,draftId,selected);}
 function draw(){
  const stale=record.generation.profile_version!==ctx.profile?.version;
  root.innerHTML=`<section class="saved-draft-review"><h3>Review your roadmap draft</h3>${record.status==='accepted'?'':assistant({generation:record.generation})}<label>Save for this career<select id="draftRole-${esc(draftId)}" aria-label="Career for this roadmap"><option value="">Choose a career</option>${roles.map(r=>`<option value="${esc(r.role_id)}" ${r.role_id===selected?'selected':''}>${esc(r.label)}</option>`).join('')}</select></label><p role="status" data-draft-status>${record.status==='accepted'?'This draft is already saved as a roadmap.':stale?'Your profile has changed since this draft was generated. Request and review a new draft before saving.':'Review the activities and selected career before saving.'}</p>${record.status==='accepted'?'<button class="button-outline" data-use-saved>Review saved roadmap</button>':`<button class="button-outline" data-accept-draft ${stale||!selected||!ctx.profile?'disabled':''}>Save this draft as a roadmap</button>`}<button class="button-outline" data-refresh-draft>Reload saved state</button></section>`;
  const select=root.querySelector('select');select.onchange=()=>{selected=select.value;draw();};root.querySelector('[data-refresh-draft]').onclick=()=>reviewDraft(ctx,root,draftId,selected);
  const accept=root.querySelector('[data-accept-draft]');if(accept)accept.onclick=()=>acceptDraft();
  const saved=root.querySelector('[data-use-saved]');if(saved)saved.onclick=async()=>{saved.disabled=true;try{const plans=await read(ctx,'plans');const plan=plans.plans.find(p=>p.plan_id===record.accepted_plan_id);if(!plan)throw new Error('The accepted roadmap is unavailable. Reload saved state.');await savedPlan(ctx,root,plan);}catch(e){root.querySelector('[data-draft-status]').textContent=e.message;saved.disabled=false;}};
 }
 async function acceptDraft(){
  root.querySelectorAll('button,select').forEach(n=>n.disabled=true);
  exact??={draft_id:draftId,role_id:selected,expected_profile_version:ctx.profile.version,expected_generation_version:record.version,idempotency_key:key()};
  try{const result=await api('product/generation-accept',exact,'POST',{signal:ctx.signal});if(!valid())return;if(!result.plan?.plan_id||result.generation?.status!=='accepted'||result.activated!==false)throw new Error('The save outcome could not be validated. Reload saved state.');await savedPlan(ctx,root,result.plan);}
  catch(e){if(!valid())return;const status=root.querySelector('[data-draft-status]');status.textContent=e.message+' No automatic retry was made.';const reload=root.querySelector('[data-refresh-draft]');reload.disabled=false;if(!e.status||e.status>=500){const retry=document.createElement('button');retry.type='button';retry.className='button-outline';retry.textContent='Retry exact save';retry.onclick=acceptDraft;status.append(' ',retry);}else if([413,415,422].includes(e.status)){exact=null;root.querySelectorAll('button,select').forEach(n=>n.disabled=false);}}
 }
}
export async function savedPlan(ctx,root,plan){
 const [state,career]=await Promise.all([read(ctx,'product/direction'),read(ctx,'role-requirements',{role_id:plan.selected_role_id})]);if(!ctx.isCurrent()||!root.isConnected)return;
 root.innerHTML=`<section class="saved-draft-review"><h3>Roadmap saved</h3><p>${esc(career.role.label)} · ${plan.tasks.length} saved activities</p><p>${state.direction?.plan_id===plan.plan_id?'This is your active roadmap.':'Your active direction has not changed.'}</p><ol>${plan.tasks.map(t=>`<li><strong>${esc(t.title||'Activity')}</strong><p>${esc(t.description||'')}</p><small>${esc(t.state)}</small></li>`).join('')}</ol>${state.direction?.plan_id===plan.plan_id?'<a class="button-outline" href="#my-path/next" data-open-my-path>Open My Path</a>':'<button class="button-outline" data-activate-draft>Use this roadmap</button>'}<p role="status" data-activation-status></p></section>`;
 const open=root.querySelector('[data-open-my-path]');if(open)open.onclick=event=>{if(location.hash==='#my-path/next'){event.preventDefault();ctx.render();}};
 const activate=root.querySelector('[data-activate-draft]');if(activate){const body={role_id:plan.selected_role_id,plan_id:plan.plan_id,expected_version:state.direction?.version||null,idempotency_key:key()};activate.onclick=async()=>{activate.disabled=true;try{await api('product/direction',body,'PUT',{signal:ctx.signal});if(ctx.isCurrent())await savedPlan(ctx,root,plan);}catch(e){if(!ctx.isCurrent())return;const status=root.querySelector('[data-activation-status]');status.textContent=e.message+' Reload saved state before another change.';const reload=document.createElement('button');reload.type='button';reload.className='button-outline';reload.textContent='Reload saved state';reload.onclick=()=>savedPlan(ctx,root,plan);status.append(' ',reload);}};}
}
export function bindDraftReviews(ctx,root){
 root.querySelectorAll('[data-review-generation]').forEach(button=>button.onclick=()=>{let target=button.nextElementSibling;if(!target?.matches('[data-draft-review-root]')){target=document.createElement('div');target.dataset.draftReviewRoot='true';button.after(target);}reviewDraft(ctx,target,button.dataset.reviewGeneration);});
}
export async function listDrafts(ctx,root,roleId){
 root.innerHTML='<p role="status">Loading saved roadmap drafts…</p>';
 try{const result=await read(ctx,'product/generations');if(!ctx.isCurrent()||!root.isConnected)return;const records=result.generations.filter(r=>r.generation?.advice?.stages?.length&&r.generation.advice.operation?.kind==='none').sort((a,b)=>String(b.created_at).localeCompare(String(a.created_at)));
 root.innerHTML=records.length?`<div class="section-title"><div><h3>Your saved drafts</h3><p>Drafts are separate from accepted roadmaps.</p></div></div><label>Choose a draft<select aria-label="Saved roadmap drafts"><option value="">Choose a saved draft</option>${records.map(r=>`<option value="${esc(r.draft_id)}">${esc(r.generation.advice.stages[0].title)} · ${esc(r.status)}</option>`).join('')}</select></label><div data-selected-draft></div>`:'<p class="muted">No roadmap drafts yet.</p>';
 if(records.length)root.querySelector('select').onchange=event=>{const target=root.querySelector('[data-selected-draft]');if(event.target.value)reviewDraft(ctx,target,event.target.value,roleId);else target.replaceChildren();};
 }catch(e){if(!ctx.isCurrent())return;root.innerHTML=`<p>${esc(e.message)}</p><button class="button-outline">Retry saved drafts</button>`;root.querySelector('button').onclick=()=>listDrafts(ctx,root,roleId);}
}
export function generateDraftButton(ctx,root,roleId,roleLabel){
 let exact=null,pending=false;
 root.innerHTML='<button class="button primary" type="button" data-generate-roadmap>Generate a roadmap with Mindbot</button><p role="status" data-generate-status></p><div data-generated-review></div>';
 const button=root.querySelector('[data-generate-roadmap]'),status=root.querySelector('[data-generate-status]');
 button.onclick=async()=>{
  if(pending)return;pending=true;button.disabled=true;status.textContent='Working…';
  try{
   if(!exact){const saved=await history('mindbot',null,{signal:ctx.signal});exact={conversation_id:saved.conversation.conversation_id,message:`Create a practical learning roadmap for ${roleLabel||roleId}. Use my saved background, give concrete learning phases and activities, and ask about missing capacity. Do not save or change my plan.`,expected_profile_version:ctx.profile.version,idempotency_key:key()};}
   const turn=await sendTurn(exact,{signal:ctx.signal});if(!ctx.isCurrent())return;
   if(['processing','uncertain'].includes(turn.turn.status)){status.textContent='The earlier request is not final. Refresh Mindbot history before issuing a new request.';button.textContent='Check exact request';return;}
   const generation=turn.response?.generation;
   if(!generation?.draft_id||!generation.advice?.stages?.length){status.textContent=turn.response?.answer||'No valid roadmap draft was returned. Your plan remains unchanged.';root.querySelector('[data-generated-review]').innerHTML=assistant(turn.response);exact=null;button.textContent='Request a new draft';return;}
   status.textContent='Draft generated. Review it before saving. This request is also in your Mindbot history.';button.textContent='Request a new draft';exact=null;await reviewDraft(ctx,root.querySelector('[data-generated-review]'),generation.draft_id,roleId);
  }catch(e){if(!ctx.isCurrent())return;status.textContent=e.message+' The request was not automatically retried.';button.textContent=exact?'Retry exact draft request':'Try again';if(e.status&&e.status<500){exact=null;button.textContent='Review and request a new draft';if(e.status===409)await ctx.refreshProfile();}}
  finally{pending=false;if(ctx.isCurrent())button.disabled=false;}
 };
}
