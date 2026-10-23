import {api,validateChat} from '../client.js';
import {esc,facts,showError,bind} from '../ui.js';
import {hydrateIcons,svg} from '../icons.js';
// Display context lasts only in this tab's memory; the backend has no transcript CRUD.
const state={messages:[],draft:'',contextOpen:false,scrollTop:0,pending:null};
let renderCurrent=null;
function releaseInert(){document.querySelectorAll('.sidebar,.topbar,.chat-page .content-col').forEach(n=>n.inert=false);}
window.addEventListener('hashchange',()=>{if(location.hash!=='#minder')releaseInert();});
export async function minder(ctx) {
  const response=await fetch('pages/minder.html');if(!response.ok)throw new Error('Chat layout unavailable.');
  ctx.view.innerHTML=await response.text();ctx.view.className='page-main chat-page';
  const $=s=>ctx.view.querySelector(s),input=$('#minderInput'),thread=$('#minderThread'),panel=$('#minderContext'),toggle=$('#minderContextToggle'),scroll=$('#minderScroll');
  if(ctx.chatDraft){state.draft=ctx.chatDraft;delete ctx.chatDraft;}input.value=state.draft;
  const mounted=()=>ctx.view.querySelector('#minderThread')===thread;
  function contextLayout(focus=false){
    if(!mounted())return;const overlay=innerWidth<=1050&&state.contextOpen;
    panel.classList.toggle('hide',!state.contextOpen);toggle.setAttribute('aria-expanded',String(state.contextOpen));
    panel.setAttribute('role',overlay?'dialog':'complementary');if(overlay)panel.setAttribute('aria-modal','true');else panel.removeAttribute('aria-modal');
    releaseInert();if(overlay)document.querySelectorAll('.sidebar,.topbar,.chat-page .content-col').forEach(n=>n.inert=true);
    if(focus&&state.contextOpen)$('#closeMinderContext').focus();
  }
  function setContext(open){const top=scroll.scrollTop;state.contextOpen=open;contextLayout(open);scroll.scrollTop=top;if(!open)toggle.focus();}
  panel.innerHTML=`<div class="context-heading"><strong>Context</strong><button type="button" class="icon-button" id="closeMinderContext" aria-label="Close Context">${svg('x')}</button></div><div class="rail-card"><div class="rail-heading"><strong>Your context</strong></div><p>${esc(ctx.profile?.career_context?.goals||'No goal reported yet.')}</p><p>${esc(ctx.profile?.timezone||'Timezone not set')}</p><p>${esc(ctx.profile?.evidence?.length??0)} evidence items recorded.</p><a href="#profile">Review profile →</a></div><div class="rail-card"><strong>Keep moving</strong><p><a href="#roadmap">Review roadmap →</a></p><p><a href="#mindbots">Review proposed changes →</a></p></div>`;
  function update(toEnd=false){
    if(!mounted())return;const oldTop=scroll.scrollTop,active=state.messages.length>0;
    $('#minderWelcome').classList.toggle('hide',active);$('#minderActive').classList.toggle('hide',!active);
    thread.innerHTML=state.messages.map((m,i)=>{
      if(m.role==='user')return `<div class="user-message">${esc(m.text)}</div>`;
      if(m.role==='error')return `<article class="assistant-answer request-result" data-result="${esc(m.code||'error')}"><p role="status">${esc(m.text)}</p><button class="button-outline" data-review-question="${i}">Review question to try again</button></article>`;
      const limits=m.result.statements.filter(s=>s.category==='limitation'),content=m.result.statements.filter(s=>s.category!=='limitation');
      return `<article class="assistant-answer">${facts(content)}${limits.length?`<div class="reply-limitation">${facts(limits.slice(0,1))}${limits.length>1?`<details><summary>Additional limitations</summary>${facts(limits.slice(1))}</details>`:''}</div>`:''}<details class="response-details"><summary>Response details</summary><p>${m.result.provider.status==='available'?'Language assistance available; only validated content is shown.':'Language service unavailable; this response is limited to verified fallback content.'}</p></details></article>`;
    }).join('')+(state.pending?'<div class="thinking-row" role="status"><span class="spinner"></span><span>Working…</span></div>':'');
    $('#minderComposer button[type=submit]').disabled=!!state.pending;input.disabled=!!state.pending;$('#minderNewSmall').disabled=!!state.pending;
    $('#cancelMinder').classList.toggle('hide',!state.pending);contextLayout();hydrateIcons(ctx.view);
    ctx.view.querySelectorAll('[data-review-question]').forEach(b=>b.onclick=()=>{state.draft=state.messages[Number(b.dataset.reviewQuestion)].question;input.value=state.draft;input.focus();});
    scroll.scrollTop=toEnd?scroll.scrollHeight:oldTop;
  }
  renderCurrent=update;
  async function send(){
    const message=input.value.trim();if(!message||state.pending)return;
    if(!ctx.profile){showError(new Error('Save a partial profile first so Minder can use its current context. Open My profile.'));return;}
    if(message.length>4000)throw new Error('Please keep your question within 4,000 characters.');
    state.messages.push({role:'user',text:message});state.draft='';input.value='';
    const request={controller:new AbortController(),message};state.pending=request;update(true);
    try{const result=validateChat(await api('chat',{message,expected_profile_version:ctx.profile.version,...(ctx.selectedRole?{selected_role_ids:[ctx.selectedRole]}:{})},'POST',{signal:request.controller.signal}));state.messages.push({role:'assistant',result});}
    catch(e){state.messages.push({role:'error',question:message,code:e.code,text:e.message+(e.code==='request_cancelled'?'':' Your question was not automatically retried.')});}
    finally{state.pending=null;renderCurrent?.(true);}
  }
  bind('minderComposer',send);$('#cancelMinder').onclick=()=>state.pending?.controller.abort();
  input.maxLength=4000;input.addEventListener('input',()=>{state.draft=input.value;input.style.height='auto';input.style.height=Math.min(130,input.scrollHeight)+'px';});
  input.addEventListener('keydown',e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();$('#minderComposer').requestSubmit();}});
  scroll.addEventListener('scroll',()=>state.scrollTop=scroll.scrollTop);
  const prompts=['Help me understand a practical preparation path using my saved profile and selected role.','Explain which requirements are supported by my evidence and which are unassessed.','Help me review my current plan and suggest realistic next steps without changing it.','Help me compare career directions using the available evidence and its limits.'];
  ctx.view.querySelectorAll('[data-prompt]').forEach((b,i)=>b.onclick=()=>{state.draft=prompts[i]||b.dataset.prompt;input.value=state.draft;input.focus();});
  toggle.onclick=()=>setContext(!state.contextOpen);$('#closeMinderContext').onclick=()=>setContext(false);
  panel.addEventListener('keydown',e=>{if(e.key==='Escape'){e.preventDefault();e.stopPropagation();setContext(false);}else if(e.key==='Tab'&&innerWidth<=1050){const controls=[...panel.querySelectorAll('button,a[href]')];if(e.shiftKey&&document.activeElement===controls[0]){e.preventDefault();controls.at(-1).focus();}else if(!e.shiftKey&&document.activeElement===controls.at(-1)){e.preventDefault();controls[0].focus();}}});
  window.addEventListener('resize',()=>{if(mounted())contextLayout();},{signal:ctx.signal});
  $('#minderNewSmall').onclick=()=>{if(clearConversation()){input.value='';update();}};$('#minderAdd').onclick=()=>{location.hash='profile';};
  update();scroll.scrollTop=state.scrollTop;
}
export function clearConversation(){if(state.pending)return false;state.messages.length=0;state.draft='';state.contextOpen=false;state.scrollTop=0;releaseInert();return true;}
