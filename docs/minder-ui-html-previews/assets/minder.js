/* Interactive, dependency-free frontend prototype. No production services are connected. */
(()=>{
'use strict';
const paths={
 'plus':'M12 5v14 M5 12h14','arrow-right':'M5 12h14 M13 6l6 6-6 6','arrow-up':'M12 19V5 M5 12l7-7 7 7',
 'chevron-right':'m9 18 6-6-6-6','chevron-left':'m15 18-6-6 6-6','x':'M18 6 6 18M6 6l12 12',
 'grid':'M3 3h7v7H3z M14 3h7v7h-7z M3 14h7v7H3z M14 14h7v7h-7z',
 'compass':'M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20z M16 8l-2.7 5.3L8 16l2.7-5.3z',
 'message-circle':'M20 11.5a8.5 8.5 0 0 1-8.5 8.5 9 9 0 0 1-4-.9L3 21l1.9-4.5a9 9 0 0 1-.9-4A8.5 8.5 0 1 1 20 11.5z',
 'bot':'M12 2v4 M9 2h6 M5 9h14v11H5z M2 12v5M22 12v5 M9 13v1M15 13v1 M9 17h6',
 'user-round':'M20 21a8 8 0 0 0-16 0 M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8z',
 'target':'M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20z M12 6a6 6 0 1 0 0 12 6 6 0 0 0 0-12z M12 10a2 2 0 1 0 0 4 2 2 0 0 0 0-4z',
 'circle-check':'M12 22a10 10 0 1 0 0-20 10 10 0 0 0 0 20z M8 12l2.5 2.5 5-5',
 'sprout':'M12 21v-9 M12 13c0-5-4-7-9-7 0 6 4 8 9 7z M12 15c0-5 4-8 9-8 0 6-4 8-9 8z',
 'ellipsis':'M5 12h.01 M12 12h.01 M19 12h.01',
 'search':'M11 19a8 8 0 1 0 0-16 8 8 0 0 0 0 16z m10 2-4.35-4.35',
 'sparkles':'M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8z M20 18l.6 1.4L22 20l-1.4.6L20 22l-.6-1.4L18 20l1.4-.6z M4 2l.6 1.4L6 4l-1.4.6L4 6l-.6-1.4L2 4l1.4-.6z',
 'calendar-days':'M8 2v4M16 2v4M3 10h18M5 4h14a2 2 0 0 1 2 2v14H3V6a2 2 0 0 1 2-2z M7 14h2 M12 14h2 M17 14h0 M7 18h2 M12 18h2',
 'calendar-check':'M8 2v4 M16 2v4 M3 10h18 M5 4h14a2 2 0 0 1 2 2v14H3V6a2 2 0 0 1 2-2z M8 15l3 3 5-5',
 'calendar-plus':'M8 2v4 M16 2v4 M3 10h18 M5 4h14a2 2 0 0 1 2 2v14H3V6a2 2 0 0 1 2-2z M12 13v5 M9.5 15.5h5',
 'chart-no-axes-column':'M4 20V12h3v8 M10 20V7h3v13 M16 20V3h3v17',
 'list-checks':'M10 6h11 M10 12h11 M10 18h11 M3 6l2 2 3-4 M3 12l2 2 3-4 M3 18l2 2 3-4',
 'route':'M4 4h5v5H4z M15 15h5v5h-5z M9 6h4a5 5 0 0 1 5 5v4 M6 9v4a5 5 0 0 0 5 5h4',
 'panel-right':'M3 4h18v16H3z M15 4v16', 'square-pen':'M4 5v15h15 M6 11l10-8 4 4-10 8-5 1z',
 'briefcase-business':'M3 7h18v13H3z M8 7V4h8v3 M3 12h18',
 'layers':'m12 2 9 5-9 5-9-5 9-5z m-9 10 9 5 9-5 m-18 5 9 5 9-5',
 'map-pin':'M20 10c0 6-8 12-8 12S4 16 4 10a8 8 0 1 1 16 0z M12 10a2 2 0 1 0 0-4 2 2 0 0 0 0 4z',
 'clock':'M12 22a10 10 0 1 0 0-20 10 10 0 0 0 0 20z M12 6v6l4 2',
 'clock-3':'M12 22a10 10 0 1 0 0-20 10 10 0 0 0 0 20z M12 6v6h5',
 'book-open':'M12 6c-3-3-7-3-10-2v15c4-2 8-1 10 1 2-2 6-3 10-1V4c-3-1-7-1-10 2z M12 6v14',
 'triangle-alert':'M12 3 2 21h20z M12 9v5 M12 18h.01',
 'graduation-cap':'m2 10 10-5 10 5-10 5-10-5z M6 12v5c4 3 8 3 12 0v-5 M22 10v6',
 'file-text':'M6 2h9l5 5v15H6z M15 2v5h5 M9 12h8 M9 16h8',
 'database':'M4 6c0-5 16-5 16 0s-16 5-16 0z M4 6v12c0 5 16 5 16 0V6 M4 12c0 5 16 5 16 0',
 'sliders-horizontal':'M3 7h8 M15 7h6 M11 4v6 M3 17h2 M9 17h12 M7 14v6',
 'phone':'M5 3l4 4-2 3c1 3 5 7 8 8l3-2 4 4-2 3c-11 1-21-12-20-18z',
 'blocks':'M3 3h8v8H3z M13 3h8v8h-8z M3 13h8v8H3z M13 13h8v8h-8z',
 'slack':'M10 3v8 M6 7h8 M14 13v8 M10 17h8 M3 10h8 M7 14v7 M13 3h8 M17 7v8',
 'monitor':'M2 4h20v14H2z M8 22h8 M12 18v4','mic':'M9 4a3 3 0 0 1 6 0v8a3 3 0 0 1-6 0z M5 11a7 7 0 0 0 14 0 M12 18v4 M9 22h6',
 'check-square':'M4 4h16v16H4z M8 12l3 3 5-6','copy':'M8 8h12v13H8z M4 17H3V3h13v2','check':'M5 12l4 4L19 6',
 'refresh-cw':'M21 12a9 9 0 0 1-15.5 6.3 M3 12A9 9 0 0 1 18.5 5.7 M17 3l2 3 3-2 M2 20l3-2 2 3'
};
function svg(name){const d=paths[name]||paths['circle-check'];return `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="${d}"/></svg>`;}
function hydrateIcons(root=document){root.querySelectorAll('[data-icon]').forEach(el=>{el.innerHTML=svg(el.dataset.icon);el.removeAttribute('data-icon');});}
const $=q=>document.querySelector(q), $$=q=>[...document.querySelectorAll(q)];
let toastTimer=0;
function toast(s){const t=$('#appToast');t.textContent=s;t.classList.add('show');clearTimeout(toastTimer);toastTimer=setTimeout(()=>t.classList.remove('show'),3500);}
function escapeHtml(s){return String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
function setInput(inp,text){inp.value=text;inp.style.height='auto';inp.style.height=Math.min(130,inp.scrollHeight)+'px';inp.focus();}
function autoSize(inp){inp.style.height='auto';inp.style.height=Math.min(130,inp.scrollHeight)+'px';}
function scrollEnd(el){requestAnimationFrame(()=>el.scrollTo({top:el.scrollHeight,behavior:'smooth'}));}
const jobRole='Machine Learning Engineer';
const phrases={
 roadmap:'I want a 12-month roadmap to transition into a machine learning engineer role. Start from my current background and break it into practical next steps.',
 skills:'Review my current skill gaps for a Machine Learning Engineer role.',
 comparison:'Compare Machine Learning Engineer, Data Scientist, and Applied AI Engineer paths.'
};
function roadmapHTML(){const rows=[
 ['Months 1–2: Build foundations','Strengthen core ML and engineering fundamentals.','Learn'],
 ['Months 3–4: Develop core skills','Gain hands-on experience with Python, evaluation, and ML workflows.','Practice'],
 ['Months 5–6: Build & ship projects','Complete portfolio projects and document your work.','Build'],
 ['Months 7–9: Gain real-world experience','Contribute to open source, internships, or relevant projects.','Apply'],
 ['Months 10–12: Prepare and transition','Polish your portfolio, practice interviews, and begin applying.','Transition']];
return `<p>Based on your current profile and target role, here's a practical 12-month preparation roadmap. It focuses on a few concrete milestones and measurable project evidence.</p><div class="rich-answer"><h3>12-month transition roadmap</h3><p class="rich-answer-sub">A proposed learning and portfolio sequence · Illustrative plan</p>${rows.map((r,i)=>`<div class="roadmap-item"><span class="number">${i+1}</span><div class="roadmap-copy"><strong>${r[0]}</strong><small>${r[1]}</small></div><span class="tag">${r[2]}</span></div>`).join('')}</div><p>Would you like me to turn this into a detailed weekly plan with specific resources and projects?</p>`;}
function skillHTML(){return `<p>For a machine learning engineering pathway, focus on demonstrated capabilities rather than treating unassessed skills as zero.</p><div class="rich-answer"><h3>Skills to build next</h3><p class="rich-answer-sub">Example priorities — update with your actual skill evidence</p>${[['Model deployment','Package, serve and monitor an ML model.','High'],['MLOps foundations','Learn repeatable pipelines and basic cloud operations.','High'],['Experiment evaluation','Measure performance and investigate failure modes.','Medium']].map((r,i)=>`<div class="roadmap-item"><span class="number">${i+1}</span><div class="roadmap-copy"><strong>${r[0]}</strong><small>${r[1]}</small></div><span class="tag">${r[2]}</span></div>`).join('')}</div><p>Connect your profile and evidence to replace this example with personalized recommendations.</p>`;}
function compareHTML(){return `<p>Three related roles share important foundations but differ in the work they emphasize.</p><div class="rich-answer"><h3>Career path comparison</h3><p class="rich-answer-sub">Illustrative distinctions, not validated match scores</p>${[['Machine Learning Engineer','ML implementation, evaluation and deployment'],['Data Scientist','Statistical analysis, experimentation and business insight'],['Applied AI Engineer','AI capabilities integrated into applications and workflows']].map((r,i)=>`<div class="roadmap-item"><span class="number">${i+1}</span><div class="roadmap-copy"><strong>${r[0]}</strong><small>${r[1]}</small></div></div>`).join('')}</div><p>Which day-to-day work would you most like to explore?</p>`;}
const chatState={started:false,busy:false};
function chatWelcome(){chatState.started=false;chatState.busy=false;$('#minderWelcome').classList.remove('hide');$('#minderActive').classList.add('hide');$('#minderThread').innerHTML='';$('#minderContext').classList.add('hide');$('#minderInput').value='';$('#minderInput').style.height='';}
function showChat(){if(chatState.started)return;chatState.started=true;$('#minderWelcome').classList.add('hide');$('#minderActive').classList.remove('hide');if(innerWidth>1200)$('#minderContext').classList.remove('hide');}
function typeMessage(prompt,{immediate=false,thinkingOnly=false}={}){
 const trimmed=prompt.trim();if(!trimmed||chatState.busy)return;
 showChat();const thread=$('#minderThread');
 const bubble=document.createElement('div');bubble.className='user-message';bubble.textContent=trimmed;thread.appendChild(bubble);
 const row=document.createElement('div');row.className='thinking-row';row.innerHTML='<span class="spinner"></span><span>Minder is thinking...</span><span class="dots"><span></span><span></span><span></span></span>';thread.appendChild(row);
 chatState.busy=true;scrollEnd($('#minderScroll'));
 if(thinkingOnly)return;
 const finish=()=>{
  if(!chatState.started||!row.isConnected)return;
  row.remove();chatState.busy=false;
  const response=document.createElement('article');response.className='assistant-answer';
  const lower=trimmed.toLowerCase();let answer=lower.includes('skill gap')?skillHTML():lower.includes('compare')?compareHTML():roadmapHTML();
  response.innerHTML=answer+`<div class="message-tools"><button class="icon-button copy-answer" title="Copy response">${svg('copy')}</button><button class="icon-button" title="Sample response">${svg('sparkles')}</button></div>`;
  thread.appendChild(response);
  const chips=document.createElement('div');chips.className='followups';
  [['calendar-days','Turn this into weekly tasks','Turn my roadmap into a concrete weekly task list.'],['chart-no-axes-column','Show skill gaps',phrases.skills],['route','Compare role alternatives',phrases.comparison]].forEach(([icon,title,prompt])=>{const b=document.createElement('button');b.type='button';b.className='chip';b.dataset.prompt=prompt;b.innerHTML=svg(icon)+escapeHtml(title);chips.appendChild(b);});
  thread.appendChild(chips);scrollEnd($('#minderScroll'));
 };
 if(immediate)finish();else setTimeout(finish,1150);
}
function initMinder(){const inp=$('#minderInput');$('#minderComposer').addEventListener('submit',e=>{e.preventDefault();const t=inp.value;inp.value='';autoSize(inp);typeMessage(t);});
 inp.addEventListener('input',()=>autoSize(inp));inp.addEventListener('keydown',e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();$('#minderComposer').requestSubmit();}});
 $('#minderAdd').addEventListener('click',()=>toast('Attachments are not connected in this HTML prototype.'));
 $('#minderContextToggle').addEventListener('click',()=>$('#minderContext').classList.toggle('hide'));
 $('#minderNewSmall').addEventListener('click',chatWelcome);
 document.addEventListener('click',e=>{const s=e.target.closest('[data-prompt]');if(s&&!s.closest('.agent-page'))setInput(inp,s.dataset.prompt);
  if(e.target.closest('.copy-answer')){const text=e.target.closest('.assistant-answer').innerText;navigator.clipboard?.writeText(text).then(()=>toast('Response copied')).catch(()=>toast('Copy unavailable in this browser'));}
  const b=e.target.closest('[data-demo]');if(b)toast(b.dataset.demo+' is an example action. Connect an API to activate it.');
 });
 const state=new URLSearchParams(location.search).get('state');if(state==='active')typeMessage(phrases.roadmap,{immediate:true});if(state==='thinking')typeMessage(phrases.roadmap,{thinkingOnly:true});
}
let prefs={name:'Nimo',color:'blue',character:'blob',persona:'Professional & focused',language:'English'};
function agentAsset(kind,color){return window.MINDER_CHARACTER_IMAGES?.[kind]?.[color]||window.MINDER_AVATARS[color]||window.MINDER_AVATARS.blue;}
try{prefs={...prefs,...JSON.parse(localStorage.getItem('minder-mindbot-demo-prefs')||'{}')}}catch(_){}
function updateBotUI(){const name=prefs.name||'Nimo';const image=agentAsset(prefs.character,prefs.color);
 ['botHeroName','botProfileName','customPreviewName'].forEach(id=>{const el=$('#'+id);if(el)el.textContent=name;});
 ['botHeroAvatar','botProfileAvatar','customPreviewImage'].forEach(id=>{const el=$('#'+id);if(el){el.src=image;el.alt=name+' avatar';}});
 const el=$('#botWelcomeTitle');if(el)el.textContent='What should '+name+' help with today?';
 const comp=$('#computerTitle');if(comp)comp.textContent=name+"'s computer";
 const nav=$('.nav-link.active');if(nav&&window.MINDER_PAGE==='mindbot'){
  nav.setAttribute('aria-label','MindBot · '+name);
  const icon=nav.querySelector('.icon');if(icon){const im=document.createElement('img');im.className='nav-profile-mini';im.src=image;im.alt='';icon.replaceWith(im);}const old=nav.querySelector('img.nav-profile-mini');if(old)old.src=image;
  const txt=nav.querySelector('span:not(.tag-on)');if(txt)txt.textContent=name;
 }
}
function showModal(id){$('#'+id).classList.remove('hide');document.body.dataset.modal=id;}
function hideModal(id){$('#'+id).classList.add('hide');delete document.body.dataset.modal;}
function botNew(){$('#botWelcome').classList.remove('hide');$('#botThread').classList.add('hide');$('#botThread').innerHTML='';$('#botScroll').scrollTop=0;$('#botInput').value='';$('#botInput').style.height='';}
function addBotMessage(prompt,{immediate=false,thinkingOnly=false}={}){
 if(!prompt.trim())return;$('#botWelcome').classList.add('hide');const thread=$('#botThread');thread.classList.remove('hide');
 const bubble=document.createElement('div');bubble.className='user-message';bubble.textContent=prompt;thread.appendChild(bubble);
 const status=document.createElement('div');status.className='thinking-row';status.innerHTML='<span class="spinner"></span><span>'+escapeHtml(prefs.name)+' is working...</span><span class="dots"><span></span><span></span><span></span></span>';thread.appendChild(status);scrollEnd($('#botScroll'));
 if(thinkingOnly)return;
 const done=()=>{
  if(!status.isConnected)return;status.remove();const report=document.createElement('div');report.className='agent-response';
  report.innerHTML=`<h3>I've prepared a plan for your week.</h3><p>Here is a preview of the changes based on your classes and current priorities. Review these suggestions before applying them to any connected system.</p>
   <div class="agent-action"><span class="icon-circle">${svg('calendar-days')}</span><div class="action-content"><strong>Schedule changes</strong><p>Three proposed adjustments around your classes.</p><ul><li>Move deep work to Tuesday 10:00–12:00</li><li>Keep Wednesday 2:00–4:00 available for project work</li><li>Leave existing classes and appointments unchanged</li></ul></div><span class="status-pill">3 changes</span></div>
   <div class="agent-action"><span class="icon-circle">${svg('clock-3')}</span><div class="action-content"><strong>Updated focus blocks</strong><p>Focus sessions organized around available time.</p><ul><li>Tuesday — Model evaluation</li><li>Wednesday — Portfolio project</li><li>Friday — Technical writing</li></ul></div><span class="status-pill">3 blocks</span></div>
   <div class="agent-action"><span class="icon-circle">${svg('check-square')}</span><div class="action-content"><strong>Tasks affected</strong><p>Move the portfolio write-up to Friday and preserve its dependencies.</p></div><span class="status-pill">1 task</span></div>
   <div class="preview-disclaimer"><span>Sample agent worklog · No external changes were made.</span><button type="button" class="button-primary approve-preview">${svg('check')} Approve preview</button></div>`;
  thread.appendChild(report);scrollEnd($('#botScroll'));
 };
 if(immediate)done();else setTimeout(done,1050);
}
function toggleProfile(force){const panel=$('#botProfile');if(force===undefined)panel.classList.toggle('hide');else panel.classList.toggle('hide',!force);}
function initBot(){updateBotUI();const inp=$('#botInput');$('#botComposer').addEventListener('submit',e=>{e.preventDefault();const t=inp.value;inp.value='';autoSize(inp);addBotMessage(t);});
 inp.addEventListener('input',()=>autoSize(inp));inp.addEventListener('keydown',e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();$('#botComposer').requestSubmit();}});
 $$('#botWelcome [data-prompt]').forEach(b=>b.addEventListener('click',()=>setInput(inp,b.dataset.prompt)));
 $('#botAdd').addEventListener('click',()=>toast('Attachments are not connected in this HTML prototype.'));
 $('#botVoice').addEventListener('click',()=>toast('Voice is not connected in this HTML prototype.'));
 $('#botCall').addEventListener('click',()=>toast('Calls require a connected communications service.'));
 $('#botMore').addEventListener('click',()=>toggleProfile());$('#botProfileToggle').addEventListener('click',()=>toggleProfile());
 $('#closeBotProfile').addEventListener('click',()=>toggleProfile(false));$('#profileCall').addEventListener('click',()=>toast('Calls require a connected communications service.'));
 $('#profileIntegrations').addEventListener('click',()=>toast('Slack is not connected in this HTML preview.'));
 $('#profileComputer').addEventListener('click',()=>toast('No remote computer is connected to this prototype.'));
 $('#openMemory').addEventListener('click',()=>{toggleProfile(true);toast('Memory overview is illustrative; personal memory is not connected.');});
 $('#openSchedule').addEventListener('click',()=>showModal('scheduleOverlay'));$('#profileSchedule').addEventListener('click',()=>{toggleProfile(false);showModal('scheduleOverlay')});
 $('#openCustomize').addEventListener('click',()=>openCustomize());$('#profileCustomize').addEventListener('click',()=>{toggleProfile(false);openCustomize()});$('#botHeroAvatar').addEventListener('click',()=>openCustomize());
 $('#closeCustomize').addEventListener('click',()=>hideModal('customizeOverlay'));
 $('#closeSchedule').addEventListener('click',()=>hideModal('scheduleOverlay'));
 $$('.modal-scrim').forEach(el=>el.addEventListener('click',e=>{if(e.target===el)hideModal(el.id)}));
 $$('.swatch').forEach(s=>s.addEventListener('click',()=>selectColor(s.dataset.color)));
 $$('.avatar-choice').forEach(s=>s.addEventListener('click',()=>selectCharacter(s.dataset.avatar)));
 $('#agentNameField').addEventListener('input',e=>$('#customPreviewName').textContent=e.target.value.trim()||'Your agent');
 $('#saveCustomize').addEventListener('click',saveCustomize);
 $('#addScheduleForm').addEventListener('submit',e=>{e.preventDefault();const nm=$('#scheduleName').value.trim();if(!nm)return;
 const div=document.createElement('div');div.className='schedule-row';div.innerHTML=`<span class="icon-circle">${svg('calendar-days')}</span><div><strong>${escapeHtml(nm)}</strong><small>${escapeHtml($('#scheduleCadence').value)} · Demo schedule</small></div><input type="checkbox" checked class="toggle" aria-label="Enable ${escapeHtml(nm)}">`;$('#scheduleList').appendChild(div);e.target.reset();toast('Schedule added to the local preview.');});
 $('#botThread').addEventListener('click',e=>{if(e.target.closest('.approve-preview'))toast('Approved in the preview. No external calendar or task changes were made.');});
 const state=new URLSearchParams(location.search).get('state');if(state==='active')addBotMessage('Reschedule my deep work blocks this week around my classes and move the portfolio task to Friday.',{immediate:true});
 if(state==='thinking')addBotMessage('Review my schedule and prepare an adjusted weekly plan.',{thinkingOnly:true});
 if(state==='profile'){addBotMessage('Reschedule my deep work blocks this week around my classes and move the portfolio task to Friday.',{immediate:true});toggleProfile(true);}
 if(state==='customize')openCustomize();if(state==='schedule')showModal('scheduleOverlay');
}
function selectColor(color){if(!window.MINDER_AVATARS[color])return;
 $$('.swatch').forEach(el=>{const y=el.dataset.color===color;el.classList.toggle('selected',y);el.setAttribute('aria-pressed',String(y));});
 const kind=$('.avatar-choice.selected')?.dataset.avatar||'blob';$('#customPreviewImage').src=agentAsset(kind,color);
}
function selectCharacter(kind){$$('.avatar-choice').forEach(el=>{const active=el.dataset.avatar===kind;el.classList.toggle('selected',active);el.setAttribute('aria-pressed',String(active));});const col=$('.swatch.selected')?.dataset.color||'blue';$('#customPreviewImage').src=agentAsset(kind,col);}
function openCustomize(){toggleProfile(false);$('#agentNameField').value=prefs.name;$('#agentPersona').value=prefs.persona;$('#agentLanguage').value=prefs.language;$('#customPreviewName').textContent=prefs.name;selectCharacter(prefs.character||'blob');selectColor(prefs.color);showModal('customizeOverlay');}
function saveCustomize(){const name=$('#agentNameField').value.trim();if(!name){$('#agentNameField').focus();toast('Enter a name to continue.');return;}
 const sel=$('.swatch.selected');prefs={name,persona:$('#agentPersona').value,language:$('#agentLanguage').value,color:sel?.dataset.color||'blue',character:$('.avatar-choice.selected')?.dataset.avatar||'blob'};
 try{localStorage.setItem('minder-mindbot-demo-prefs',JSON.stringify(prefs))}catch(_){}
 updateBotUI();hideModal('customizeOverlay');toast('Agent appearance and preferences updated in this preview.');}
function common(){hydrateIcons();$('#globalNewChat').addEventListener('click',()=>window.MINDER_PAGE==='minder'?chatWelcome():botNew());
 $$('.demo-route').forEach(el=>el.addEventListener('click',e=>{e.preventDefault();toast((el.dataset.description||'This module')+' is outside this two-page HTML preview.');}));
 $('#accountMenu').addEventListener('click',()=>toast('Account settings are not part of this two-page preview.'));
 $('#globalSearch').addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();toast('Global search requires an application backend.');}});
 document.addEventListener('keydown',e=>{if(e.key==='Escape'){['customizeOverlay','scheduleOverlay'].forEach(id=>{const el=$('#'+id);if(el&&!el.classList.contains('hide'))hideModal(id)});const p=$('#botProfile');if(p)toggleProfile(false);}});
}
common(); if(window.MINDER_PAGE==='minder')initMinder();else initBot();
})();
