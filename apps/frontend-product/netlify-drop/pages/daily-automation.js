import {roleCatalogue} from '../role-presentation.js';
import {api} from '../client.js';
import {esc} from '../ui.js';
const epochs=new WeakMap();
export async function dailyAutomation(ctx,root,settings,onSaved){
 const epoch=(epochs.get(root)||0)+1;epochs.set(root,epoch);let plans,roles;root.innerHTML='<p role="status">Loading daily automation settings…</p>';
 const valid=()=>ctx.isCurrent()&&root.isConnected&&epochs.get(root)===epoch;
 try{const [saved,catalogue]=await Promise.all([api('plans',undefined,'GET',{signal:ctx.signal}),roleCatalogue(ctx)]);plans=saved.plans;roles=catalogue;if(!valid())return;}
 catch(e){if(!valid())return;root.innerHTML=`<p>${esc(e.message)}</p><button type="button" class="button-outline">Retry schedule context</button>`;root.querySelector('button').onclick=()=>dailyAutomation(ctx,root,settings,onSaved);return;}
 const state=settings?.state||(settings?.enabled?'active':'paused'),selected=settings?.scope?.plan_ids||[];
 const time=value=>{if(!value)return 'Not scheduled';try{return new Intl.DateTimeFormat(undefined,{dateStyle:'medium',timeStyle:'short',timeZone:settings?.timezone||ctx.profile.timezone}).format(new Date(value));}catch{return value;}};
 root.innerHTML=`<h2>Daily automation</h2><p>${settings?'Status: '+esc(state):'No daily automation created yet.'}</p><form id="dailyAutomation"><label>Check time<input type="time" name="check_time" required value="${esc(settings?.check_time||'09:00')}"></label><label>Timezone<input name="timezone" required maxlength="120" value="${esc(settings?.timezone||ctx.profile.timezone||'Asia/Kuala_Lumpur')}"></label><fieldset><legend>Plans to include</legend><label><input type="checkbox" name="all_plans" ${selected.length?'':'checked'}> All my saved plans</label>${plans.map(p=>`<label><input type="checkbox" name="plan_id" value="${esc(p.plan_id)}" ${selected.includes(p.plan_id)?'checked':''}> ${esc(roles.find(r=>r.role_id===p.selected_role_id)?.label||'Career name unavailable')} · ${p.tasks.length} activities</label>`).join('')||'<p>No plans saved yet.</p>'}</fieldset><button type="submit" class="button-outline">${settings?'Save schedule changes':'Create daily automation'}</button></form>${settings?`<div class="actions">${state==='active'?'<button type="button" class="button-outline" data-schedule-state="paused">Pause</button>':`<button type="button" class="button-outline" data-schedule-state="active">${state==='cancelled'?'Create again':'Resume'}</button>`}${state!=='cancelled'?'<button type="button" class="button-outline" data-schedule-state="cancelled">Cancel automation</button>':''}</div>`:''}<p>Next run: ${esc(time(settings?.next_run))}</p>${settings?.last_result?`<p>Last result: ${esc(settings.last_result.status)} · ${esc(time(settings.last_result.observed_at))}</p>`:'<p>No saved run result yet.</p>'}<p>Saving settings does not verify a continuously running worker. Run status and results come from the server.</p><p role="status" id="automationSaveStatus"></p>`;
 const form=root.querySelector('form'),all=form.elements.all_plans;
 const syncScope=()=>root.querySelectorAll('[name=plan_id]').forEach(input=>input.disabled=all.checked);all.onchange=syncScope;syncScope();
 let saving=false;
 async function update(changes){
  if(saving)return;saving=true;root.querySelectorAll('button,input').forEach(n=>n.disabled=true);root.querySelector('#automationSaveStatus').textContent='Saving…';
  try{const result=await api('agent-settings',{settings:changes,expected_version:settings?.version||null},'PUT',{signal:ctx.signal});if(!valid())return;if(typeof result.version!=='string'||typeof result.enabled!=='boolean')throw new Error('The saved schedule could not be validated.');await onSaved();}
  catch(e){if(!valid())return;const status=root.querySelector('#automationSaveStatus');status.textContent=e.message+' The requested change is not confirmed. Reload saved state before another change.';const reload=document.createElement('button');reload.type='button';reload.className='button-outline';reload.textContent='Reload saved automation';reload.onclick=onSaved;status.append(' ',reload);}
  finally{saving=false;}
 }
 form.onsubmit=event=>{event.preventDefault();const ids=all.checked?[]:[...root.querySelectorAll('[name=plan_id]:checked')].map(input=>input.value);if(!all.checked&&!ids.length){root.querySelector('#automationSaveStatus').textContent='Select at least one plan, or choose all your saved plans.';return;}update({check_time:form.elements.check_time.value,timezone:form.elements.timezone.value.trim(),scope:{plan_ids:ids},...(settings?{}:{state:'active',enabled:true})});};
 root.querySelectorAll('[data-schedule-state]').forEach(b=>b.onclick=()=>update({state:b.dataset.scheduleState,enabled:b.dataset.scheduleState==='active'}));
}
