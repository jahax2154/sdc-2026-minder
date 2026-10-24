import {api,optional,key} from '../client.js';
import {card,esc,bind,diffLabel,facts} from '../ui.js';
import {svg} from '../icons.js';
import {mindbotChat} from './mindbot-chat.js';
import {dailyAutomation} from './daily-automation.js';
import {reviewCreatedTask} from './task-controls.js';
export async function mindbots(ctx){
 ctx.view.className='page-main agent-page';
 const hasActivity=false,state={};
  const quick=(id,icon,title,detail)=>`<button class="feature-button" type="button" id="${id}"><span class="icon-circle">${svg(icon)}</span><span><strong>${title}</strong><small>${detail}</small></span></button>`;
  ctx.view.innerHTML=`<div class="content-col"><div class="agent-tools"><button class="icon-button" id="botProfileToggle" aria-label="MindBot profile">${svg('sliders-horizontal')}</button></div><div class="agent-hero"><img class="agent-avatar" src="assets/nimo-blue.png" alt="Nimo"><h1>Nimo</h1><p>Your personal agent for a more focused, intentional you.</p><div class="agent-quick-nav">${quick('openSchedule','calendar-days','Schedule','Daily check settings')}${quick('openActivity','database','Activity','Updates & proposals')}${quick('openCustomize','sliders-horizontal','Customize','Not available yet')}</div></div><p id="botWorkspaceStatus" class="workspace-status" role="status">Loading saved activity…</p><div class="chat-scroller" id="botScroll"><section class="agent-new-content ${hasActivity?'hide':''}" id="botWelcome"><h2>What should Nimo help with today?</h2><p>Review your plans, choose your next step, and keep the evidence visible.</p><div class="agent-suggestions">${[['tasks','calendar-days','Review my schedule','See saved tasks and scheduled work'],['roadmap','list-checks','Plan my week','Review or create a preparation path'],['profile','user-round','Update my context','Review availability and your evidence'],['tasks','check-square','Organize tasks','Add and edit your saved activities']].map(([route,icon,title,detail])=>`<button type="button" class="suggest-card" data-bot-prompt="${esc(title+'. '+detail+'. Use my saved plans and profile, and ask before changing anything.')}"><span class="icon-circle">${svg(icon)}</span><span class="suggest-copy"><span class="suggest-title">${title}</span><span class="suggest-description">${detail}</span></span>${svg('chevron-right')}</button>`).join('')}</div></section><div class="agent-thread ${hasActivity?'':'hide'}" id="botActivity"></div></div><footer class="composer-area"><div class="composer-inner"><form class="composer" id="botComposer"><textarea id="botInput" rows="1" maxlength="4000" placeholder="Message Mindbot…" aria-label="Message Mindbot"></textarea><button class="send-button" aria-label="Send Mindbot message" type="submit">${svg('arrow-up')}</button></form><div class="composer-caption">One continuous private history. Review proposed changes before approval.</div></div></footer></div><aside class="profile-popover hide" id="botProfile" aria-label="MindBot profile"><button class="icon-button close-pop" id="closeBotProfile" aria-label="Close profile">${svg('x')}</button><div class="profile-identity"><img src="assets/nimo-blue.png" alt="Nimo"><div><strong>Nimo</strong><small>${state.deployment_scheduler_verified?'Scheduler verified':'Continuous scheduling unverified'}</small></div></div><div id="botSettings"></div></aside>`;
  ctx.view.dataset.frameReady='true';ctx.view.setAttribute('aria-busy','false');
  const panel=ctx.view.querySelector('#botProfile');
  document.querySelector('#openSchedule').onclick=()=>panel.classList.remove('hide');
  document.querySelector('#botProfileToggle').onclick=()=>panel.classList.toggle('hide');
  document.querySelector('#closeBotProfile').onclick=()=>{panel.classList.add('hide');document.querySelector('#botProfileToggle').focus();};document.addEventListener('keydown',event=>{if(event.key==='Escape'&&!panel.classList.contains('hide')){panel.classList.add('hide');document.querySelector('#botProfileToggle').focus();}},{signal:ctx.signal});
  document.querySelector('#openActivity').onclick=()=>{ctx.botHasActivity=true;document.querySelector('#botWelcome').classList.add('hide');document.querySelector('#botActivity').classList.remove('hide');};
  document.querySelector('#openCustomize').disabled=true;document.querySelector('#openCustomize').title='Custom identity, persona and language are not supported by the backend yet.';
  const chatReady=mindbotChat(ctx);

 const activity=ctx.view.querySelector('#botActivity');
 activity.innerHTML='<section id="botProposals"></section><section id="botNotices"></section><section id="botHistory"></section>';
 const valid=()=>ctx.isCurrent?ctx.isCurrent():document.querySelector('#botActivity')===activity;
 const statuses=new Map(),epochs=new Map();let pendingCount=null,settings=null,settingsLoaded=false;
 function reveal(){if(!valid())return;ctx.botHasActivity=true;document.querySelector('#botWelcome').classList.add('hide');activity.classList.remove('hide');}
 function summary(){if(!valid())return;const loading=[...statuses.values()].some(v=>v==='loading'),failed=[...statuses.values()].some(v=>v==='error');document.querySelector('#botWorkspaceStatus').textContent=loading?'Loading saved activity…':failed?'Some saved information could not be loaded. Retry the affected section.':pendingCount===null?'Saved activity loaded.':pendingCount?`${pendingCount} proposed changes ready for review.`:'No pending proposals. Saved activity loaded.';}
 async function section(id,title,read,paint){
  if(!valid())return;const epoch=(epochs.get(id)||0)+1;epochs.set(id,epoch);statuses.set(id,'loading');summary();
  const el=ctx.view.querySelector('#'+id);el.dataset.state='loading';el.setAttribute('aria-busy','true');el.innerHTML=card(title,'<p role="status">Loading saved information…</p>');
  try{const value=await read();if(!valid()||epochs.get(id)!==epoch)return;await paint(value,el);if(!valid())return;el.dataset.state='ready';el.setAttribute('aria-busy','false');statuses.set(id,'ready');}
  catch(e){if(!valid()||e.code==='request_cancelled')return;if([401,403].includes(e.status)){ctx.failAuth?.(e);return;}el.dataset.state='error';el.setAttribute('aria-busy','false');statuses.set(id,'error');el.innerHTML=card(title,`<p>${esc(e.message)}</p><button id="retry-${id}">Retry ${esc(title.toLowerCase())}</button>`);bind('retry-'+id,()=>section(id,title,read,paint));reveal();}
  finally{summary();}
 }
 const readOptions={signal:ctx.signal};
 const reloadProposals=()=>section('botProposals','Proposed changes',()=>api('proposals',undefined,'GET',readOptions),(list,el)=>{
  if(!Array.isArray(list.proposals))throw new Error('Saved proposals could not be read. Retry this section.');
  pendingCount=list.proposals.filter(p=>p.status==='pending').length;const badge=document.querySelector('#proposalBadge');badge.hidden=!pendingCount;badge.textContent=pendingCount>99?'99+':String(pendingCount);badge.setAttribute('aria-label',`${pendingCount} pending proposals`);
  if(list.proposals.length)reveal();
  el.innerHTML=card('Proposed changes',list.proposals.length?'<p>Review the exact differences. Rejection leaves the target unchanged.</p>':'<p>No proposed changes yet.</p>');
  list.proposals.forEach((p,i)=>{
   const req=p.preview.request;el.insertAdjacentHTML('beforeend',card('Proposed change · '+p.status,`<p>${esc(req.reason)}</p>${req.diff.map(diffLabel).join('')}${p.status==='pending'?`<div id="decision-${i}"><button id="approve-${i}">Approve this exact change</button><button class="secondary" id="reject-${i}">Reject</button></div>`:''}`));
   for(const decision of ['approve','reject'])bind(decision+'-'+i,async()=>{
    const controls=document.querySelectorAll(`#decision-${i} button`);controls.forEach(b=>b.disabled=true);
    try{await api('proposal-decision',{proposal_id:p.preview.proposal_id,decision,preview_hash:p.preview_hash,expected_state_version:req.expected_state_version});await refreshSaved(req.kind==='configure_automation');}
    catch(e){if(e.status===409){await reloadProposals();e.message='The proposal state changed. Review the refreshed server status before another decision.';}else if(!e.status||e.status>=500){const scope=ctx.view.querySelector('#decision-'+i);if(scope&&valid()){scope.innerHTML='<p role="status">The decision outcome is not confirmed. Reload saved proposals before another choice.</p><button type="button" class="button-outline" id="reloadDecision-'+i+'">Reload saved proposals</button>';bind('reloadDecision-'+i,reloadProposals);}}else controls.forEach(b=>b.disabled=false);throw e;}
   });
  });
 });
 const reloadAgents=()=>section('botNotices','Recent activity',()=>api('agents',undefined,'GET',readOptions),(result,el)=>{
  if(!Array.isArray(result.notices)||!Array.isArray(result.events))throw new Error('Saved activity could not be read. Retry this section.');
  if(result.notices.length||result.events.length)reveal();
  el.innerHTML=card('Recent activity',result.notices.map(n=>`<p>${esc(n.summary)}</p>${facts(n.statements||[])}`).join('')||'<p>No notices yet. Automatic analysis needs a running worker.</p>')+card('Checks',result.events.map(e=>`<p>${esc(e.kind.replaceAll('_',' '))} · ${esc(e.status)} · attempts ${esc(e.attempts)}</p>`).join('')||'<p>No checks recorded.</p>');
  document.querySelector('#botProfile .profile-identity small').textContent=result.deployment_scheduler_verified?'Scheduler verified':'Continuous scheduling unverified';
 });
 const reloadHistory=()=>section('botHistory','Saved actions',()=>api('action-history',undefined,'GET',readOptions),(result,el)=>{
  if(!Array.isArray(result.history))throw new Error('Saved actions could not be read. Retry this section.');
  if(result.history.length)reveal();el.innerHTML=result.history.length?'':card('Saved actions','<p>No saved actions yet.</p>');
  result.history.forEach((h,i)=>{const a=h.result?.action||h.action||h;el.insertAdjacentHTML('beforeend',card('Saved action · '+a.execution_status,`<p>${esc(a.reason)}</p><small>${esc(h.created_at||'Time unavailable')} · ${esc(a.approval_state)}</small>${(a.diff||[]).map(diffLabel).join('')}${a.execution_status==='applied'&&a.kind==='create_task'&&h.result?.target?.plan_id?`<button type="button" class="button-outline" id="reviewCreated-${i}">Review created activity</button><div id="createdActivity-${i}"></div>`:''}${a.execution_status==='applied'&&!['complete_task','create_task','schedule_task','configure_automation'].includes(a.kind)?`<button id="undo-${i}" class="secondary">Undo this change</button>`:''}`));const review=ctx.view.querySelector('#reviewCreated-'+i);if(review){const task=a.diff.find(change=>change.after&&typeof change.after==='object'&&change.after.task_id)?.after;review.onclick=()=>reviewCreatedTask(ctx,ctx.view.querySelector('#createdActivity-'+i),h.result.target.plan_id,task.task_id);}const idempotency_key=key();bind('undo-'+i,async()=>{await api('undo',{action_id:a.action_id,expected_state_version:a.resulting_state_version,idempotency_key});await refreshSaved();});});
 });
 async function paintSettings(){
  if(!valid()||!settingsLoaded)return;const el=document.querySelector('#botSettings');
  if(ctx.profileStatus==='loading'){el.innerHTML=card('Daily check','<p role="status">Loading saved profile context…</p>');return;}
  if(ctx.profileError){el.innerHTML=card('Daily check','<p>Profile context could not be loaded. Other saved sections remain available.</p><button id="retryBotProfile">Retry profile context</button>');bind('retryBotProfile',()=>ctx.refreshProfile());return;}
  if(!ctx.profile){el.innerHTML=card('Daily check','<p>Save a partial profile to configure your daily check.</p><a href="#profile">My profile →</a>');return;}
  el.innerHTML=card('Daily automation','<div id="dailyAutomationRoot"></div>');await dailyAutomation(ctx,el.querySelector('#dailyAutomationRoot'),settings,reloadSettings);
 }
 const reloadSettings=()=>section('botSettings','Daily check',()=>optional('agent-settings',readOptions),async value=>{settings=value;settingsLoaded=true;await ctx.profileReady;await paintSettings();});
 ctx.onProfileLoaded=()=>{if(!ctx.view.querySelector('#dailyAutomation'))paintSettings();};
 ctx.onBotResult=turn=>Promise.allSettled([reloadProposals(),reloadAgents(),reloadHistory(),...(turn?.response?.action_status==='applied'&&turn.response.actions?.some(item=>(item.action||item).kind==='configure_automation')?[reloadSettings()]:[])]);
 async function refreshSaved(automation=false){await Promise.allSettled([reloadProposals(),reloadAgents(),reloadHistory(),ctx.refreshProfile(),...(automation?[reloadSettings()]:[])]);}
 // Render the approved frame first; these ordinary reads never request a model/job.
 await Promise.allSettled([chatReady,reloadProposals(),reloadAgents(),reloadHistory(),reloadSettings()]);
}
