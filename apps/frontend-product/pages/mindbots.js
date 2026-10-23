import {api,optional,key} from '../client.js';
import {card,esc,bind,diffLabel,facts} from '../ui.js';
import {hydrateIcons,svg} from '../icons.js';
export async function mindbots(ctx) {
  ctx.view.className='page-main agent-page';
  const [state,list,history,settings]=await Promise.all([api('agents'),api('proposals'),api('action-history'),optional('agent-settings')]);
  const hasActivity=list.proposals.length||state.notices?.length||history.history.length;
  const quick=(id,icon,title,detail)=>`<button class="feature-button" type="button" id="${id}"><span class="icon-circle">${svg(icon)}</span><span><strong>${title}</strong><small>${detail}</small></span></button>`;
  ctx.view.innerHTML=`<div class="content-col"><div class="agent-tools"><button class="icon-button" id="botProfileToggle" aria-label="MindBot profile">${svg('sliders-horizontal')}</button></div><div class="agent-hero"><img class="agent-avatar" src="assets/nimo-blue.png" alt="Nimo"><h1>Nimo</h1><p>Your personal agent for a more focused, intentional you.</p><div class="agent-quick-nav">${quick('openSchedule','calendar-days','Schedule','Daily check settings')}${quick('openActivity','database','Activity','Updates & proposals')}${quick('openCustomize','sliders-horizontal','Customize','Not available yet')}</div></div><div class="chat-scroller" id="botScroll"><section class="agent-new-content ${hasActivity?'hide':''}" id="botWelcome"><h2>What should Nimo help with today?</h2><p>Review your plans, choose your next step, and keep the evidence visible.</p><div class="agent-suggestions">${[['tasks','calendar-days','Review my schedule','See saved tasks and scheduled work'],['roadmap','list-checks','Plan my week','Review or create a preparation path'],['profile','user-round','Update my context','Review availability and your evidence'],['tasks','check-square','Organize tasks','Add and edit your saved activities']].map(([route,icon,title,detail])=>`<a class="suggest-card" href="#${route}"><span class="icon-circle">${svg(icon)}</span><span class="suggest-copy"><span class="suggest-title">${title}</span><span class="suggest-description">${detail}</span></span>${svg('chevron-right')}</a>`).join('')}</div></section><div class="agent-thread ${hasActivity?'':'hide'}" id="botActivity"></div></div><footer class="composer-area"><div class="composer-inner"><form class="composer" id="botComposer"><a class="icon-button" href="#tasks" aria-label="Manage tasks">${svg('plus')}</a><textarea id="botInput" rows="1" maxlength="4000" placeholder="Think it through with Minder…" aria-label="Question to continue in Minder"></textarea><button class="send-button" aria-label="Continue in Minder" type="submit">${svg('arrow-up')}</button></form><div class="composer-caption">Questions continue in Minder. Changes use the exact task and proposal controls.</div></div></footer></div><aside class="profile-popover hide" id="botProfile" aria-label="MindBot profile"><button class="icon-button close-pop" id="closeBotProfile" aria-label="Close profile">${svg('x')}</button><div class="profile-identity"><img src="assets/nimo-blue.png" alt="Nimo"><div><strong>Nimo</strong><small>${state.deployment_scheduler_verified?'Scheduler verified':'Continuous scheduling unverified'}</small></div></div><div id="botSettings"></div></aside>`;
  const panel=ctx.view.querySelector('#botProfile');
  document.querySelector('#openSchedule').onclick=()=>panel.classList.remove('hide');
  document.querySelector('#botProfileToggle').onclick=()=>panel.classList.toggle('hide');
  document.querySelector('#closeBotProfile').onclick=()=>panel.classList.add('hide');
  document.querySelector('#openActivity').onclick=()=>{document.querySelector('#botWelcome').classList.add('hide');document.querySelector('#botActivity').classList.remove('hide');};
  document.querySelector('#openCustomize').disabled=true;document.querySelector('#openCustomize').title='Custom identity, persona and language are not supported by the backend yet.';
  bind('botComposer',()=>{ctx.chatDraft=document.querySelector('#botInput').value;location.hash='minder';});
  const activity=ctx.view.querySelector('#botActivity');const append=s=>activity.insertAdjacentHTML('beforeend',s);
  if(!ctx.profile) {document.querySelector('#botSettings').innerHTML=card('Start with your profile','<p>Save a partial profile to configure your daily check.</p><a href="#profile">My profile →</a>');return;}
  document.querySelector('#botSettings').innerHTML=card('Daily check',`<form id="dailySettings"><label>Check time (${esc(ctx.profile.timezone)})<input name="check_time" type="time" value="${esc(settings?.check_time||'08:00')}" required></label><label><input name="enabled" type="checkbox" ${settings?.enabled?'checked':''}> Enable daily check</label><button type="submit">Save daily check</button></form><p>Saving settings does not start a background worker.</p>`);
  bind('dailySettings',async()=>{const form=document.querySelector('#dailySettings');await api('agent-settings',{settings:{enabled:form.elements.enabled.checked,check_time:form.elements.check_time.value},expected_version:settings?.version||null},'PUT');await ctx.render();});
  append(card('Proposed changes',list.proposals.length?'<p>Review each exact difference before approval. Rejection preserves the target state.</p>':'<p>No proposed changes yet.</p>'));
  for(const [i,p] of list.proposals.entries()) {
    const req=p.preview.request;
    append(card('Proposed change · '+p.status,`<p>${esc(req.reason)}</p>${req.diff.map(diffLabel).join('')}${p.status==='pending'?`<div id="decision-${i}"><button id="approve-${i}">Approve this exact change</button><button class="secondary" id="reject-${i}">Reject</button></div>`:''}`));
    for(const decision of ['approve','reject'])bind(decision+'-'+i,async()=>{
      const controls=document.querySelectorAll(`#decision-${i} button`);controls.forEach(b=>b.disabled=true);
      try {await api('proposal-decision',{proposal_id:p.preview.proposal_id,decision,preview_hash:p.preview_hash,expected_state_version:req.expected_state_version});await ctx.render();}
      catch(e){if(e.status===409){await ctx.render();e.message='This proposal is stale. Review the refreshed state; it was not approved.';}else controls.forEach(b=>b.disabled=false);throw e;}
    });
  }
  append(card('Recent activity',(state.notices||[]).map(n=>`<p>${esc(n.summary)}</p>${facts(n.statements||[])}`).join('')||'<p>No notices yet. Automatic analysis needs a running worker.</p>'));
  append(card('Checks',(state.events||[]).map(e=>`<p>${esc(e.kind.replaceAll('_',' '))} · ${esc(e.status)} · attempts ${esc(e.attempts)}</p>`).join('')||'<p>No checks recorded.</p>'));
  for(const [i,h] of history.history.entries()) {
    const action=h.result?.action||h.action||h;
    append(card('Saved action · '+action.execution_status,`<p>${esc(action.reason)}</p><small>${esc(h.created_at||'Time unavailable')} · ${esc(action.approval_state)}</small>${(action.diff||[]).map(diffLabel).join('')}${action.execution_status==='applied'&&action.kind!=='complete_task'?`<button id="undo-${i}" class="secondary">Undo this change</button>`:''}`));
    const idempotency_key=key();bind('undo-'+i,async()=>{await api('undo',{action_id:action.action_id,expected_state_version:action.resulting_state_version,idempotency_key});await ctx.render();});
  }
}
